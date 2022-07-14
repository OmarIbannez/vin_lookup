import factory

from app.models import Vehicle


class VehicleFactory(factory.Factory):
    class Meta:
        model = Vehicle
