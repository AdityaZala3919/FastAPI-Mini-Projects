"""
Training script for the housing price prediction model.
This script loads the California Housing dataset, trains a regression model,
and saves it to disk as model.pkl.
"""

import joblib
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np


def train_model():
    """
    Load data, train model, and save to disk.
    """
    print("Loading California Housing dataset...")
    # Load the built-in California Housing dataset
    housing = fetch_california_housing()
    X, y = housing.data, housing.target
    
    print(f"Dataset shape: {X.shape}")
    print(f"Features: {housing.feature_names}")
    
    # Split data into training and testing sets (80/20 split)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("\nTraining Random Forest Regressor...")
    # Create and train a Random Forest model
    # Using fewer trees and limited depth for faster training
    model = RandomForestRegressor(
        n_estimators=100,      # Number of trees in the forest
        max_depth=10,          # Maximum depth of each tree
        random_state=42,       # For reproducibility
        n_jobs=-1              # Use all CPU cores
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Evaluate the model on test data
    print("\nEvaluating model performance...")
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Root Mean Squared Error: {rmse:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    # Save the trained model to disk
    model_filename = "model.pkl"
    joblib.dump(model, model_filename)
    print(f"\nModel saved as '{model_filename}'")
    print("✓ Training complete!")


if __name__ == "__main__":
    train_model()
