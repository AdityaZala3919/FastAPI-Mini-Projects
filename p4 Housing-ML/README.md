# Housing Price Prediction API

A minimal FastAPI machine learning project that predicts California housing prices using a trained Random Forest model.

## 📁 Project Structure

```
housing-price-prediction/
├── main.py            # FastAPI app that loads model.pkl and exposes /predict
├── train.py           # Script to train a regression model and save model.pkl
├── model.pkl          # Generated after running train.py
├── schemas.py         # Pydantic models for request and response
├── requirements.txt   # FastAPI + scikit-learn + joblib
└── README.md          # This file
```

## 🚀 Getting Started

### 1. Install Dependencies

First, install all required packages:

```bash
pip install -r requirements.txt
```

### 2. Train the Model

Run the training script to create `model.pkl`:

```bash
python train.py
```

This will:
- Load the California Housing dataset from scikit-learn
- Train a Random Forest regression model
- Save the trained model as `model.pkl`
- Display model performance metrics

### 3. Start the FastAPI Server

Start the API server:

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

## 📖 API Usage

### Interactive Documentation

Visit the auto-generated API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Make a Prediction

Send a POST request to `/predict` with housing features:

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.98,
    "AveBedrms": 1.02,
    "Population": 322.0,
    "AveOccup": 2.55,
    "Latitude": 37.88,
    "Longitude": -122.23
  }'
```

**Example using Python:**

```python
import requests

url = "http://localhost:8000/predict"
data = {
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.98,
    "AveBedrms": 1.02,
    "Population": 322.0,
    "AveOccup": 2.55,
    "Latitude": 37.88,
    "Longitude": -122.23
}

response = requests.post(url, json=data)
print(response.json())
```

**Response:**

```json
{
  "predicted_price": 4.526
}
```

Note: The predicted price is in units of $100,000 (so 4.526 means $452,600).

## 🔍 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/predict` | POST | Predict housing price |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

## 📊 Input Features

The model requires 8 features from the California Housing dataset:

1. **MedInc**: Median income in block group
2. **HouseAge**: Median house age in block group
3. **AveRooms**: Average number of rooms per household
4. **AveBedrms**: Average number of bedrooms per household
5. **Population**: Block group population
6. **AveOccup**: Average number of household members
7. **Latitude**: Block group latitude
8. **Longitude**: Block group longitude

## 🛠️ Tech Stack

- **FastAPI**: Modern web framework for building APIs
- **scikit-learn**: Machine learning library for model training
- **joblib**: For model serialization
- **uvicorn**: ASGI server for running FastAPI
- **pydantic**: Data validation using Python type hints

## 📝 Notes

- The model predicts housing prices in units of $100,000
- This is a minimal project for learning purposes
- Model performance: RMSE ~0.5 (on test set)
- The Random Forest model uses 100 trees with max depth of 10

## 🔄 Next Steps

To deploy this application, you can:
1. Create a Dockerfile for containerization
2. Deploy to cloud platforms (AWS, GCP, Azure)
3. Add authentication and rate limiting
4. Implement model versioning
5. Add monitoring and logging
