"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Replace example schemas with app-specific schemas

class Dataset(BaseModel):
    """Dataset metadata
    Collection name: "dataset"
    """
    title: str = Field(..., description="Dataset title")
    description: Optional[str] = Field(None, description="Short description of the dataset")
    color: Optional[str] = Field("#60a5fa", description="Hex color used when charting")

class Datapoint(BaseModel):
    """Datapoints belonging to a dataset
    Collection name: "datapoint"
    """
    dataset_id: str = Field(..., description="ID of the related dataset (stringified ObjectId)")
    label: str = Field(..., description="X-axis label")
    value: float = Field(..., description="Numeric value for Y-axis")

class DatasetWithPoints(BaseModel):
    title: str
    description: Optional[str]
    color: Optional[str]
    points: List[Datapoint] = []
