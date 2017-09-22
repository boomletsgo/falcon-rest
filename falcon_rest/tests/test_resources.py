from falcon import testing
from marshmallow import Schema, fields
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from falcon_rest.resources import BaseResource, ModelResource
from . import MiddlewareTestsMixin


# First, let's generate the engine and declare a SQLAlchemy model
db_engine = create_engine("sqlite:///:memory:")
Base = declarative_base()


class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    legs = Column(Integer, default=4)


class AnimalSerializer(Schema):
    name = fields.Str()
    legs = fields.Integer()


class BaseRequestEndpoint(BaseResource):
    id_param = "another_id"
    id_field = "yet_another_id"
    serializer = AnimalSerializer()


class DisallowedRequestEndpoint(BaseResource):
    allowed_methods = []


class BaseModelEndpoint(ModelResource):
    pass


class TestBaseResource(MiddlewareTestsMixin, testing.TestBase):

    def setUp(self):
        super(TestBaseResource, self).setUp()
        self.api.add_route("/", BaseRequestEndpoint())

    def test_id_param_is_saved(self):
        base_endpoint = BaseRequestEndpoint()

        assert base_endpoint.id_param == "another_id"
        assert base_endpoint.id_field == "yet_another_id"

    def test_get_data_filters(self):
        base_endpoint = BaseRequestEndpoint()
        assert base_endpoint.get_data_filters() == {}

    def test_returns_early_if_no_legitimate_data_sent(self):
        client = testing.TestClient(self.api)
        result = client.simulate_get("/")

        assert result.status_code == 200
        assert "timestamp" in result.json
        assert "data" in result.json
        assert result.json["data"] == []

    def test_check_disallowed_methods(self):
        pass
