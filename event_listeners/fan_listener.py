import logging
from pyisy.nodes import Node
from .device_listener import DeviceListener

_logger = logging.getLogger(__name__)


class FanListener(DeviceListener):
    def __init__(self, node):
        # type: (Node) -> None
        super().__init__(node)
