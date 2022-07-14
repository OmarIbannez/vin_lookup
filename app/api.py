from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from . import models, schemas, service
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/lookup/{vin}", response_model=schemas.Vehicle)
def get_vehicle(vin: str, db: Session = Depends(get_db)):
    """
    GET Endpoint that returns vehicle information based on the VIN.
    :param vin: Vehicle Identification Number
    :param db: Database session
    :return Vehicle: Vehicle instance
    """
    vehicle_service = service.VehicleService(vin=vin, db=db)
    vehicle = vehicle_service.get_vehicle()

    if not vehicle:
        raise HTTPException(status_code=404, detail="VIN not found")

    return vehicle


@app.delete("/remove/{vin}", status_code=204)
def delete_vehicle(vin: str, db: Session = Depends(get_db)):
    """
    DELETE Endpoint that removes a vehicle from DB if it exists.
    :param vin: Vehicle Identification Number
    :param db: Database session
    :return HTTPResponse:
    """
    vehicle_service = service.VehicleService(vin=vin, db=db)
    deleted = vehicle_service.delete_vehicle()

    if not deleted:
        raise HTTPException(status_code=404, detail="VIN not found")


@app.get("/export")
def export(db: Session = Depends(get_db)):
    """
    GET Endpoint that returns a Parquet file with all the vehicles stored in DB.
    :param db: Database session
    :return FileResponse: Parquet file
    """
    vehicle_service = service.VehicleService(vin=None, db=db)
    file_name, path = vehicle_service.generate_parquet_export()

    return FileResponse(path, filename=file_name)
