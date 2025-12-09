"""
FastAPI application for housing price prediction.
This app loads a pre-trained model and exposes a /predict endpoint.
"""

import joblib
from fastapi import FastAPI, HTTPException
from schemas import HousingFeatures, PredictionResponse
import numpy as np
import os


# Initialize FastAPI app
app = FastAPI(
    title="Housing Price Prediction API",
    description="Predict California housing prices using machine learning",
    version="1.0.0"
)

# Global variable to store the loaded model
model = None


@app.on_event("startup")
async def load_model():
    """
    Load the trained model when the application starts.
    This runs once when the server starts up.
    """
    global model
    model_path = "model.pkl"
    
    # Check if model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file '{model_path}' not found. "
            "Please run 'python train.py' first to create the model."
        )
    
    # Load the model from disk
    print(f"Loading model from {model_path}...")
    model = joblib.load(model_path)
    print("✓ Model loaded successfully!")


@app.get("/")
async def root():
    """
    Root endpoint - provides basic API information.
    """
    return {
        "message": "Housing Price Prediction API",
        "endpoints": {
            "/predict": "POST - Predict housing price from features",
            "/docs": "GET - Interactive API documentation"
        }
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(features: HousingFeatures):
    """
    Predict housing price based on input features.
    
    Args:
        features: HousingFeatures object containing 8 housing attributes
        
    Returns:
        PredictionResponse with predicted price (in $100,000s)
    """
    # Check if model is loaded
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please restart the server."
        )
    
    try:
        # Convert Pydantic model to numpy array in correct order
        # Order must match the training data features
        feature_array = np.array([[
            features.MedInc,
            features.HouseAge,
            features.AveRooms,
            features.AveBedrms,
            features.Population,
            features.AveOccup,
            features.Latitude,
            features.Longitude
        ]])
        
        # Make prediction using the loaded model
        prediction = model.predict(feature_array)
        
        # Return the prediction
        return PredictionResponse(predicted_price=float(prediction[0]))
        
    except Exception as e:
        # Handle any errors during prediction
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }
