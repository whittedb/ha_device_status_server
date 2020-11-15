import settings
from pynamodb.models import Model as PynamoModel
from pynamodb.attributes import (UnicodeAttribute, NumberAttribute)
from marshmallow import Schema, fields, post_load, pre_dump
from pyisy.nodes import Node


class DeviceStatus(object):
    def __init__(self, node):
        # type: (Node) -> DeviceStatus
        self._node = node
        self.id = node.name.replace(" ", "").replace(".", "").replace("'", "").lower()
        self.name = node.name
        self.value = node.formatted
        self.last_changed = node.last_changed
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None
        self.second = None
        self.microsecond = None


class DeviceSchema(Schema):
    id = fields.String(data_key="_id")
    name = fields.String()
    value = fields.String()
    year = fields.Integer()
    month = fields.Integer()
    day = fields.Integer()
    hour = fields.Integer()
    minute = fields.Integer()
    second = fields.Integer()
    microsecond = fields.Integer()

    @post_load
    def make_object(self, data, **kwargs):
        # type: (dict, dict) -> dict
        obj = {}
        changed_time = data["last_changed"]
        if "_id" not in data:
            obj.update({"_id": "{}".format(data["name"].replace(" ", "").replace("'", "").replace(".", "").lower())})
        obj.update(dict(year=changed_time.year, month=changed_time.month, day=changed_time.day,
                        hour=changed_time.hour, minute=changed_time.minute, second=changed_time.second,
                        microsecond=changed_time.microsecond))
        return obj

    @pre_dump
    def set_timestamp_from_db(self, data, **kwargs):
        # type: (DeviceStatus, **dict) -> DeviceStatus
        data.year = data.last_changed.year
        data.month = data.last_changed.month
        data.day = data.last_changed.day
        data.hour = data.last_changed.hour
        data.minute = data.last_changed.minute
        data.second = data.last_changed.second
        data.microsecond = data.last_changed.microsecond
        return data


class AwsTellMeTable(PynamoModel):
    class Meta:
        table_name = "TellMe"
        if settings.AWS_HOST:
            host = settings.AWS_HOST
        region = settings.AWS_REGION
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        read_capacity_units = 5
        write_capacity_units = 5

    _id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    value = UnicodeAttribute()
    year = NumberAttribute()
    month = NumberAttribute()
    day = NumberAttribute()
    hour = NumberAttribute()
    minute = NumberAttribute()
    second = NumberAttribute()
    microsecond = NumberAttribute()
