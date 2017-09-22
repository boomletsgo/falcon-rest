# Falcon REST
Lightweight REST framework for [Falcon Framework](https://falconframework.org/) and (optionally) SQLAlchemy.

[![Build Status](https://travis-ci.org/boomletsgo/falcon-rest.svg?branch=master)](https://travis-ci.org/boomletsgo/falcon-rest)
[![PyPI](https://img.shields.io/pypi/v/falcon-rest.svg)](https://pypi.python.org/pypi/falcon-rest/)
[![Python Versions](https://img.shields.io/pypi/pyversions/falcon-rest.svg)](https://pypi.python.org/pypi/falcon-rest/)
[![Coverage Status](https://coveralls.io/repos/boomletsgo/falcon-rest/badge.svg?branch=master)](https://coveralls.io/r/boomletsgo/falcon-rest?branch=master)




## Installation

`$ pip install falcon-rest`

Note: This installs the `falcon_json_middleware` dependency

## Usage

Inside your application file:

```
import falcon
import falcon_json_middleware
from falcon_rest.resources import ModelResource
from marshmallow import Schema, fields
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


# First, let's generate the engine and declare a SQLAlchemy model
db_engine = create_engine("sqlite:///sqlite.db")
Base = declarative_base()


class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    legs = Column(Integer, default=4)



# Next, let's create a serializer for the Animal model. We use marshmallow for serialization.

class AnimalSerializer(Schema):
    name = fields.Str()
    legs = fields.Integer()


class AnimalResource(ModelResource):
    """Example API endpoint to show basics of usage"""

    model = Animal
    serializer = AnimalSerializer()
    # Default is to allow all methods
    allowed_methods = ["GET", "POST", "PATCH", "DELETE"]
    # If you want to use a custom parameter name in your routes
    id_param = "animal_id"  
	

middleware = [falcon_json_middleware.Middleware()]
application = falcon.API(middleware=middleware)

application.add_route("/animal", AnimalResource(db_engine=db_engine))
application.add_route("/animal/{animal_id}", AnimalResource(db_engine=db_engine))
```

Now, start up your app with your wsgi server of choice and do a `POST /animal` with `{"name": "Cat", "legs": 4}` and you should see a JSON response. You can then take the id from that response and plug it into a `GET /animal/<id>`.

### GET Endpoint (List)
By default, the plain GET endpoint will return a list of all records for the model.

### GET Endpoint (Retrieve)
Pass in the id to the route and perform a GET to retrieve a single item.

### POST Endpoint
POST any JSON data to the plain endpoint to create a new record. Extraneous fields are ignored. Bulk POST is supported. Return order for bulk POST is guaranteed.

### PATCH Endpoint (Single)
You can PATCH a single record if you pass the id into the route.

### PATCH Endpoint (Bulk)
You can PATCH multiple records by passing the id field into your JSON array. Return order is guaranteed.

### DELETE Endpoint (Single)
You can DELETE a single record if you pass the id into the route.

### DELETE Endpoint (Bulk)
You can DELETE multiple records by passing the id field into your JSON array. Failed deletes are silently ignored.