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

## INput /Output schema

## Routes

    GET / : Check if server is alive.

    GET /predict : Instructions for POST usage.

    POST /predict :

        Input: JSON body with property details.

        Output:

        {"prediction": 320000, "status_code": 200}

## Input Format


{
  "data": {
    "area": 120,
    "property_type": "HOUSE",
    "rooms_number": 3,
    "zip_code": 1000,
    "garden": true,
    "terrace": true
  }
}

✅ Only area, property_type, rooms_number, zip_code are mandatory.
✅ All others are optional.

## Deployment

    Fully containerized with Docker.

    Deployed on Render.com.

    Access the interactive API docs at:

    https://<your-render-url>/docs


## Usage

    Clone the repo

    Build and run:
```bash
    docker build -t challenge-api-deployment .

    docker run -p 8000:8000 challenge-api-deployment
```
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




