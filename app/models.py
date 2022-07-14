from sqlalchemy import Column, Integer, String

from .database import Base


class Vehicle(Base):
    __tablename__ = "vehicle"

    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String)
    make = Column(String)
    model = Column(String)
    model_year = Column(String)
    body_class = Column(String)
