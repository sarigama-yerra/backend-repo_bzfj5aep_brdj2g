import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatasetCreate(BaseModel):
    title: str
    description: Optional[str] = None
    color: Optional[str] = "#60a5fa"

class DatapointCreate(BaseModel):
    label: str
    value: float

@app.get("/")
def read_root():
    return {"message": "Chart API ready"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

@app.post("/datasets")
def create_dataset(payload: DatasetCreate):
    dataset = {
        "title": payload.title,
        "description": payload.description,
        "color": payload.color,
    }
    dataset_id = create_document("dataset", dataset)
    return {"id": dataset_id}

@app.get("/datasets")
def list_datasets():
    items = get_documents("dataset")
    # normalize ids
    for it in items:
        it["id"] = str(it.get("_id"))
        it.pop("_id", None)
    return items

@app.post("/datasets/{dataset_id}/points")
def add_datapoint(dataset_id: str, payload: DatapointCreate):
    # validate dataset exists
    try:
        _ = db["dataset"].find_one({"_id": ObjectId(dataset_id)})
    except Exception:
        _ = None
    if not _:
        raise HTTPException(status_code=404, detail="Dataset not found")

    data = {
        "dataset_id": dataset_id,
        "label": payload.label,
        "value": payload.value,
    }
    point_id = create_document("datapoint", data)
    return {"id": point_id}

@app.get("/datasets/{dataset_id}/points")
def list_points(dataset_id: str):
    pts = get_documents("datapoint", {"dataset_id": dataset_id})
    for p in pts:
        p["id"] = str(p.get("_id"))
        p.pop("_id", None)
    # sort by created_at for consistent series
    pts.sort(key=lambda x: x.get("created_at", ""))
    return pts

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
