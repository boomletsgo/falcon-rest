import datetime

import falcon
from falcon_rest import exceptions, session
import sqlalchemy


class BaseResource(object):

    def __init__(self):
        self.id_param = getattr(self, "id_param", "id")
        self.id_field = getattr(self, "id_field", "id")

    def get_data_filters(self, kwargs=None):
        return {}

    def meta_data(self, data):
        data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "data": data
        }

        return data

    def on_get(self, request, response, *args, **kwargs):
        if hasattr(self, "allowed_methods") and "GET" not in self.allowed_methods:
            raise falcon.HTTPMethodNotAllowed(self.allowed_methods)

        if self.id_param in kwargs:
            data = self.retrieve(request, kwargs[self.id_param])
        else:
            data_filters = self.get_data_filters(kwargs)
            data = self.list(request, data_filters)

        data = self.meta_data(data)

        response.json = data

    def retrieve(self, request, id):
        data = self.data_retrieve(request, id)
        data = self.serialize_retrieve(data)

        return data

    def data_retrieve(self, request, id):
        return {}

    def serialize_retrieve(self, data):
        serializer = getattr(self, "retrieve_serializer", getattr(self, "serializer", None))
        if not serializer:
            raise exceptions.FalconRestException(
                "No retrieve_serializer or serializer defined on {0}".format(self.__class__.__name__))

        data = serializer.dump(data).data

        return data

    def list(self, request, data_filters):
        data = self.data_list(request, data_filters)
        data = self.serialize_list(data)

        return data

    def data_list(self, request, data_filters, db_session):
        return []

    def serialize_list(self, data):
        serializer = getattr(self, "list_serializer", getattr(self, "serializer", None))
        if not serializer:
            raise exceptions.FalconRestException(
                "No list_serializer or serializer defined on {0}".format(self.__class__.__name__))

        data = serializer.dump(data, many=True).data
        return data

    def on_post(self, request, response, *args, **kwargs):
        if hasattr(self, "allowed_methods") and "POST" not in self.allowed_methods:
            raise falcon.HTTPMethodNotAllowed(self.allowed_methods)

        dataset = request.json
        if not isinstance(dataset, list):
            dataset = [dataset]

        created = self.create(request, dataset)
        created = self.meta_data(created)

        response.json = created

    def create(self, request, dataset):
        dataset = self.data_create(request, dataset)
        dataset = self.serialize_create(dataset)

        return dataset

    def data_create(self, request, dataset):
        return dataset

    def serialize_create(self, dataset):
        serializer = getattr(self, "create_serializer", getattr(self, "serializer", None))
        if not serializer:
            raise exceptions.FalconRestException(
                "No create_serializer or serializer defined on {0}".format(self.__class__.__name__))

        dataset = serializer.dump(dataset, many=True).data
        return dataset

    def on_patch(self, request, response, *args, **kwargs):
        if hasattr(self, "allowed_methods") and "PATCH" not in self.allowed_methods:
            raise falcon.HTTPMethodNotAllowed(self.allowed_methods)

        dataset = request.json
        if not isinstance(dataset, list):
            dataset = [dataset]

        patched = self.patch(request, dataset, kwargs.get(self.id_param))
        patched = self.meta_data(patched)

        response.json = patched

    def patch(self, request, dataset, id):
        dataset = self.data_patch(request, dataset, id)
        dataset = self.serialize_patch(dataset)

        return dataset

    def data_patch(self, request, dataset):
        return dataset

    def serialize_patch(self, dataset):
        serializer = getattr(self, "patch_serializer", getattr(self, "serializer", None))
        if not serializer:
            raise exceptions.FalconRestException(
                "No patch_serializer or serializer defined on {0}".format(self.__class__.__name__))

        dataset = serializer.dump(dataset, many=True).data
        return dataset

    def on_delete(self, request, response, *args, **kwargs):
        if hasattr(self, "allowed_methods") and "DELETE" not in self.allowed_methods:
            raise falcon.HTTPMethodNotAllowed(self.allowed_methods)

        dataset = request.json
        if not isinstance(dataset, list):
            dataset = [dataset]

        self.delete(request, dataset, kwargs.get(self.id_param))
        deleted = self.meta_data({"status": "deleted"})

        response.json = deleted

    def delete(self, request, dataset, id):
        self.data_delete(request, dataset, id)

    def data_delete(self, request, dataset):
        pass


class ModelResource(BaseResource):

    def __init__(self, db_engine, *args, **kwargs):
        super(ModelResource, self).__init__(*args, **kwargs)
        self.db_engine = db_engine

        if not hasattr(self, "model"):
            raise exceptions.FalconRestException("No model defined on {0}".format(self.__class__.__name__))

    def retrieve(self, request, id):
        with session.make(self.db_engine) as db_session:
            data = self.data_retrieve(request, id, db_session)
            data = self.serialize_retrieve(data)

        return data

    def data_retrieve(self, request, id, db_session):
        params = {self.id_field: id}

        result = db_session.query(self.model).filter_by(**params)
        result = result.options(sqlalchemy.orm.joinedload("*"))
        result = result.first()

        return result

    def list(self, request, data_filters):
        with session.make(self.db_engine) as db_session:
            data = self.data_list(request, data_filters, db_session)
            data = self.serialize_list(data)

        return data

    def data_list(self, request, data_filters, db_session):
        result = db_session.query(self.model).filter_by(**data_filters)
        return result

    def create(self, request, dataset):
        with session.make(self.db_engine) as db_session:
            dataset = self.data_create(request, dataset, db_session)

            try:
                dataset = self.serialize_create(dataset)
            except Exception as ex:
                db_session.rollback()
                raise falcon.HTTPBadRequest(str(ex))

        return dataset

    def data_create(self, request, dataset, db_session):
        models = []

        for data in dataset:
            model = self.data_set(self.model, data)
            model = self.before_save(request, model, db_session)
            models.append(model)

        if models:
            db_session.add_all(models)

        try:
            db_session.commit()
        except Exception as ex:
            db_session.rollback()
            raise falcon.HTTPBadRequest(str(ex))

        return models

    def patch(self, request, dataset, id):
        with session.make(self.db_engine) as db_session:
            dataset = self.data_patch(request, dataset, id, db_session)

            try:
                dataset = self.serialize_patch(dataset)
            except Exception as ex:
                db_session.rollback()
                raise falcon.HTTPBadRequest(str(ex))

        return dataset

    def data_patch(self, request, dataset, id, db_session):
        models = []

        for data in dataset:
            id = data.pop(self.id_field, id)
            if not id:
                models.append(None)
                continue

            params = {self.id_field: id}
            model = db_session.query(self.model).filter_by(**params).first()
            if not model:
                models.append(None)
                continue

            for key in data:
                setattr(model, key, data[key])

            model = self.before_save(request, model, db_session)

            models.append(model)

        if not models:
            return []

        try:
            db_session.commit()
        except Exception as ex:
            db_session.rollback()
            raise falcon.HTTPBadRequest(str(ex))

        return models

    def data_set(self, model, data):
        model = self.model()
        for key in data:
            if hasattr(model, key):
                setattr(model, key, data[key])

        return model

    def before_save(self, request, resource, db_session):
        return resource

    def data_delete(self, request, dataset, id):
        with session.make(self.db_engine) as db_session:
            for data in dataset:
                id = data.pop(self.id_field, id)
                if not id:
                    continue

                params = {self.id_field: id}
                db_session.query(self.model).filter_by(**params).delete()

            try:
                db_session.commit()
            except Exception as ex:
                db_session.rollback()
                raise falcon.HTTPBadRequest(str(ex))
