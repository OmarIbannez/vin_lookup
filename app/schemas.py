from pydantic import BaseModel


class Vehicle(BaseModel):
    id: int
    vin: str
    make: str
    model: str
    model_year: str
    body_class: str
    cached: bool

    class Config:
        orm_mode = True
