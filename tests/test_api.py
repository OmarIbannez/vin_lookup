import responses

from .factories import VehicleFactory


class TestApi:
    @responses.activate
    def test_lookup_valid_vin(self, client, session):
        vin = "1XKWDB0X57J211825"
        vehicle_response = {
            "Results": [
                {
                    "ErrorCode": "0",
                    "VIN": "1XKWDB0X57J211825",
                    "Make": "KENWORTH",
                    "Model": "W9 Series",
                    "ModelYear": "2007",
                    "BodyClass": "Truck-Tractor",
                }
            ]
        }
        url = (
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
        )
        responses.add(responses.GET, url, json=vehicle_response, status=200)
        response = client.get(f"/lookup/{vin}")

        assert response.status_code == 200
        assert response.json()["vin"] == vin

    @responses.activate
    def test_lookup_invalid_vin(self, client, session):
        vin = "invalid"
        error_text = (
            "6 - Incomplete VIN; 7 - Manufacturer is not registered with NHTSA...; "
            "11 - Incorrect Model Year...; "
            "400 - Invalid Characters Present"
        )
        vehicle_response = {
            "Results": [
                {
                    "ErrorCode": "6,7,11,400",
                    "ErrorText:": error_text,
                }
            ]
        }
        url = (
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
        )
        responses.add(responses.GET, url, json=vehicle_response, status=200)
        response = client.get(f"/lookup/{vin}")

        assert response.status_code == 404

    def test_delete_vehicle(self, client, session):
        vin = "1XKWDB0X57J211825"
        vehicle = VehicleFactory.create(
            vin=vin,
            make="KENWORTH",
            model="W9 Series",
            model_year="2007",
            body_class="Truck-Tractor",
        )
        session.add(vehicle)
        session.commit()
        response = client.delete(f"/remove/{vin}")

        assert response.status_code == 204

    def test_delete_vehicle_not_in_db(self, client, session):
        vin = "1XKWDB0X57J211825"
        response = client.delete(f"/remove/{vin}")

        assert response.status_code == 404

    def test_export(self, client, session):
        import io

        import pandas as pd

        vin = "42"
        vehicle = VehicleFactory.create(
            vin=vin,
            make="KENWORTH",
            model="W9 Series",
            model_year="2007",
            body_class="Truck-Tractor",
        )
        session.add(vehicle)
        session.commit()
        response = client.get("/export")
        pq_file = io.BytesIO(response.content)
        df = pd.read_parquet(pq_file)

        assert response.status_code == 200
        assert df.iloc[0]["vin"] == vin
