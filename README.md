# VIN decoder powered by [vPIC API](https://vpic.nhtsa.dot.gov/api/)

## Installation
1. Create a python 3.7.12 virtual environment. You can accomplish this with [pyenv](https://github.com/pyenv/pyenv) `pyenv virtualenv 3.7.12 vinlookup`.
2. Install dependencies `pip install -r requirements.txt`.

## Run
To run locally, on the console go to the project directory and execute: `uvicorn app.api:app --reload`

## Testing
To execute unit tests simply run pytest on the project directory: `pytest`

## Functionality

### GET `/lookup/{VIN}`

This endpoint will return the vehicle information based on the Vehicle Identification Number.

Example response:
```
{
    "id": 4,
    "vin": "4V4NC9EJXEN171694",
    "make": "VOLVO TRUCK",
    "model": "VNL",
    "model_year": "2014",
    "body_class": "Truck-Tractor",
    "cached": true
}
```

###  DELETE `/remove/{VIN}`

This endpoint removes the vehicle information if it exists on the database.

###  GET `/export`
This endpoint exports the database in a [Parquet](https://parquet.apache.org/) file.
