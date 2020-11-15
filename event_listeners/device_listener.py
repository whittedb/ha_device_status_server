import logging
from pyisy.nodes import Node
from models import DeviceSchema, DeviceStatus
from db import get_local_db, get_aws_table

_logger = logging.getLogger(__name__)


class DeviceListener(object):
    def __init__(self, node):
        # type: (Node) -> None
        self._node = node
        self._listener = self._node.status_events.subscribe(self.callback)

    @property
    def node(self):
        return self._node

    def unsubscribe(self):
        self._listener.unsubscribe()
        self._listener = None

    def callback(self, event):
        # type: (dict) -> None
        # _logger.debug("Event: {}".format(event))
        self.update_db_device_status()

    def update_db_device_status(self):
        """Override this to change database storage behavior"""
        device_status = DeviceStatus(self.node)
        device_status = DeviceSchema().dump(device_status)

        _logger.debug(device_status)
        db_id = device_status["_id"]

        # Update local DB
        with get_local_db() as db:
            if db_id in db:
                # Update item if it exists
                local_db_doc = db[db_id]

                # Don't do any database updates if the value has not changed
                if local_db_doc["value"] != device_status["value"]:
                    local_db_doc.update(device_status)
                    local_db_doc.save()

            else:
                # Create item if it doesn't exist
                local_db_doc = db.create_document(device_status)

        # Update AWS DB
        aws_table = get_aws_table()
        try:
            # Update item if it exists
            current_doc = aws_table.get(db_id)
            if current_doc.value != device_status["value"]:
                actions = [
                    # name should never change
                    # aws_table.name.set(device_status["name"]),
                    aws_table.value.set(device_status["value"]),
                    aws_table.year.set(device_status["year"]),
                    aws_table.month.set(device_status["month"]),
                    aws_table.day.set(device_status["day"]),
                    aws_table.hour.set(device_status["hour"]),
                    aws_table.minute.set(device_status["minute"]),
                    aws_table.microsecond.set(device_status["microsecond"])
                ]
                current_doc.update(actions=actions)
        except aws_table.DoesNotExist:
            # Create item if it doesn't exist
            new_doc = dict(**device_status)
            new_doc.pop("_id")
            item = aws_table(db_id, **new_doc)
            item.save()

        return local_db_doc
