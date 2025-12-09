"""
Pydantic models for request and response validation.
These schemas define the structure of data sent to and received from the API.
"""

from pydantic import BaseModel, Field


class HousingFeatures(BaseModel):
    """
    Input schema for housing price prediction.
    Contains the 8 features from the California Housing dataset.
    """
    MedInc: float = Field(..., description="Median income in block group")
    HouseAge: float = Field(..., description="Median house age in block group")
    AveRooms: float = Field(..., description="Average number of rooms per household")
    AveBedrms: float = Field(..., description="Average number of bedrooms per household")
    Population: float = Field(..., description="Block group population")
    AveOccup: float = Field(..., description="Average number of household members")
    Latitude: float = Field(..., description="Block group latitude")
    Longitude: float = Field(..., description="Block group longitude")

    class Config:
        # Example values for API documentation
        json_schema_extra = {
            "example": {
                "MedInc": 8.3252,
                "HouseAge": 41.0,
                "AveRooms": 6.98,
                "AveBedrms": 1.02,
                "Population": 322.0,
                "AveOccup": 2.55,
                "Latitude": 37.88,
                "Longitude": -122.23
            }
        }


class PredictionResponse(BaseModel):
    """
    Output schema for housing price prediction.
    Returns the predicted house value.
    """
    predicted_price: float = Field(..., description="Predicted house price in $100,000s")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_price": 4.526
            }
        }
