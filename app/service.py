from datetime import datetime
from typing import Union

import pandas as pd
import requests
from fastparquet import write
from requests.exceptions import ConnectionError
from sqlalchemy.orm import Session

from . import models


class VehicleService:
    """
    Service layer that contains all the basic operations needed to run the API.
    """

    def __init__(self, vin: Union[str, None], db: Session):
        # vPIC API URL.
        self.api_url = (
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
        )
        # VIN we want to work with.
        self.vin = vin
        # DB Session.
        self.db = db
        # Vehicle cached in DB.
        self.vehicle = None

    def __get_vehicle_from_api(self) -> Union[dict, None]:
        """
        Private method to retrieve vehicle information from the vPIC API.
        """
        try:
            response = requests.get(self.api_url)
        except ConnectionError:
            return

        results = response.json()["Results"]

        for result in results:
            # 0 means no errors found.
            # If an error is found we should not return any result.
            if result["ErrorCode"] != "0":
                return

            # API returns a list of vehicles, if a match is found we return it.
            if result["VIN"] == self.vin:
                return result

    def get_vehicle(self) -> Union[models.Vehicle, None]:
        """
        Method to get a vehicle from DB or retrieve it from API and store it and DB.
        """
        vehicle = (
            self.db.query(models.Vehicle).filter(models.Vehicle.vin == self.vin).first()
        )
        # If a vehicle is found we return it.
        if vehicle:
            self.vehicle = vehicle
            self.vehicle.cached = True
        # If it is not found we try to retrieve it from the API and store it.
        elif not vehicle:
            vehicle_data = self.__get_vehicle_from_api()
            if not vehicle_data:
                return
            vehicle = models.Vehicle(
                vin=vehicle_data["VIN"],
                make=vehicle_data["Make"],
                model=vehicle_data["Model"],
                model_year=vehicle_data["ModelYear"],
                body_class=vehicle_data["BodyClass"],
            )
            self.db.add(vehicle)
            self.db.commit()
            self.vehicle = vehicle
            self.vehicle.cached = False

        return self.vehicle

    def delete_vehicle(self) -> bool:
        """
        Method to delete a vehicle from database
        """
        vehicle = (
            self.db.query(models.Vehicle).filter(models.Vehicle.vin == self.vin).first()
        )
        if not vehicle:
            return False

        self.db.delete(vehicle)
        self.db.commit()

        return True

    def __get_vehicles_as_data_frame(self):
        """
        Private method to return all vehicles form DB as a DataFrame
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
        """
        vehicles_query = self.db.query(models.Vehicle)
        return pd.read_sql(vehicles_query.statement, vehicles_query.session.bind)

    def generate_parquet_export(self):
        """
        Method to generate a Parquet file with all vehicles in DB.
        https://parquet.apache.org/
        """
        df = self.__get_vehicles_as_data_frame()

        date_time = datetime.now().strftime("%m%d%Y%H%M%S")
        file_name = f"{date_time}.parquet"
        path = f"exports/{file_name}"

        write(path, df)

        return file_name, path
