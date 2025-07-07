## ImmoEliza ML Price Prediction API

## Structure:
challenge-api-deployment/

├── .venv/                   # Local virtual environment (excluded from Git)

├── app.py                   # Main FastAPI app

├── Dockerfile               # To be created later

├── model/                   # Trained model (e.g. model.pkl)

├── predict/

│   └── prediction.py        # predict() function

├── preprocessing/

│   └── cleaning_data.py     # preprocess() function

├── README.md                # Documentation

└── .gitignore


## A FastAPI-powered service predicting property prices for Belgium.

## Input / Output Schema

### Input Schema

| **Field Name**   | **Type**     | **Value**         | **Notes**                                                                                                   |
| ---------------- | ------------ | ----------------- | ----------------------------------------------------------------------------------------------------------- |
| `rooms_number`   | `int`        | `1`               | ✅ Meets the constraint: greater than 0.                                                                     |
| `area`           | `float`      | `10`              | ⚠️ Just meets the minimum: must be greater than 10 — check if `gt=9` is intentional.                        |
| `lift`           | `bool`       | `false`           | Uses default value.                                                                                         |
| `garden`         | `bool`       | `false`           | Uses default value.                                                                                         |
| `swimming_pool`  | `bool`       | `false`           | Uses default value.                                                                                         |
| `terrace`        | `bool`       | `false`           | Uses default value.                                                                                         |
| `building_state` | `str` (enum) | `"TO BE DONE UP"` | Uses default value. Options: `NEW`, `GOOD`, `JUST RENOVATED`, `TO BE DONE UP`, `TO RENOVATE`, `TO RESTORE`. |
| `property_type`  | `str` (enum) | `"APARTMENT"`     | ✅ Required value provided. Options: `APARTMENT`, `HOUSE`.                                                   |
| `zip_code`       | `int`        | `0`               | ⚠️ Typically, a ZIP code should be > 0 — check for validity.                                                |

### Output Schema

| **Field Name** | **Type**          | **Description**                           |
| -------------- | ----------------- | ----------------------------------------- |
| `prediction`   | `Optional[float]` | The predicted value (may be `null`).      |
| `status_code`  | `Optional[int]`   | The response status code (may be `null`). |


## Routes

    GET / : Check if server is alive.

    GET /predict : Instructions for POST usage.

    POST /predict :

        Input: JSON body with property details:
        
          Calls function preprocess() and returns an array.

          Use the array in predict() and with the Catboost model loaded from .joblib file predicts price.

        Output:

        {"prediction": 320000, "status_code": 200}

## Input Format

{
  "rooms_number": 1,
  "area": 10,
  "lift": false,
  "garden": false,
  "swimming_pool": false,
  "terrace": false,
  "building_state": "TO BE DONE UP",
  "property_type": "APARTMENT",
  "zip_code": 0
}

✅ Only area, property_type, rooms_number, zip_code are mandatory. (It checks if valid zip_code)

✅ All others are optional, default values if not filled: false for boolean fields and TO BE DONE UP for building-state.

## Deployment

    Fully containerized with Docker.

    Deployed on Render.com.

    Access the interactive API docs at:

    https://<your-render-url>/docs


## Usage

    Clone the repo

    Build and run:

    docker build -t challenge-api-deployment .

    docker run -p 8000:8000 challenge-api-deployment

    Use Swagger UI at http://localhost:8000/docs for testing.

## Render Deployment Checklist

✅ Link GitHub repo with Render.

✅ Use Docker deployment option.

✅ Add environment variable:

PORT = 8000

✅ Build and deploy.

## How to test for correctness

1️⃣ Deploy on Render.

2️⃣ Use Swagger UI (/docs) to send:

{
  "data": {
    "area": 90,
    "property_type": "APARTMENT",
    "rooms_number": 2,
    "zip_code": 1000
  }
}

and

{
  "data": {
    "area": 90,
    "property_type": "HOUSE",
    "rooms_number": 2,
    "zip_code": 5000
  }
}

✅ You should get different predicted prices thanks to latitude/longitude injection based on zip_code.