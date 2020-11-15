import asyncio
import logging.config
import time
from urllib.parse import urlparse
from pyisy import ISY
from pyisy.connection import ISYConnectionError, ISYInvalidAuthError, get_new_client_session
from pyisy.constants import LOG_DATE_FORMAT, LOG_FORMAT
import settings
from event_listeners import LightListener, FanListener
from db import couchdb_admin_session
import versioning

# Set up logging
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=settings.LOG_LEVEL)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pyisy").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.INFO)
logging.getLogger("pynamodb").setLevel(logging.INFO)


async def is_light_device(node):
    return node.family is None \
           and "kpl" not in node.name.lower() \
           and ("light" in node.name.lower() or "lamp" in node.name.lower())


async def is_fan_device(node):
    return node.family is None \
           and "kpl" not in node.name.lower() \
           and "fan" in node.name.lower()


async def is_supported_device(node):
    return is_light_device(node) or is_fan_device(node)


async def main(url, username, password, tls_ver):
    """Execute connection to ISY and load all system info."""
    t0 = time.time()
    host = urlparse(url)
    if host.scheme == "http":
        https = False
        port = host.port or 80
    elif host.scheme == "https":
        https = True
        port = host.port or 443
    else:
        _LOGGER.error("host value in configuration is invalid.")
        return False

    # Use the helper function to get a new aiohttp.ClientSession.
    websession = get_new_client_session(https, tls_ver)

    # Connect to ISY controller.
    isy = ISY(
        host.hostname,
        port,
        username=username,
        password=password,
        use_https=https,
        tls_ver=tls_ver,
        webroot=host.path,
        websession=websession,
        use_websocket=True,
    )

    listeners = []
    try:
        await isy.initialize()
        # nodes = {}
        for node_tuple in isy.nodes:
            node = node_tuple[1]
            if await is_light_device(node):
                listeners.append(LightListener(node))
            elif await is_fan_device(node):
                listener = FanListener(node)
                listeners.append(listener)
                listener.update_db_device_status()
            # if is_supported_device(node):
            #     nodes.update({node.address: node})
    except (ISYInvalidAuthError, ISYConnectionError):
        _LOGGER.error(
            "Failed to connect to the ISY, please adjust settings and try again."
        )
        for listener in listeners:
            await listener.unsubscribe()
        await isy.shutdown()
        return
    except Exception as err:
        _LOGGER.error("Unknown error occurred: %s", err.args[0])
        for listener in listeners:
            await listener.unsubscribe()
        await isy.shutdown()
        raise

    # Print a representation of all the Nodes
    # _LOGGER.debug(repr(isy.nodes))
    _LOGGER.info("Total Loading time: %.2fs", time.time() - t0)

    try:
        isy.websocket.start()
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        for listener in listeners:
            await listener.unsubscribe()
        await isy.shutdown()


if __name__ == "__main__":
    _LOGGER.info("Starting ha_device_status_server %s ..." % versioning.VERSION)
    _LOGGER.info(f"ISY URL: {settings.ISY_URL}, TLS Version: {settings.ISY_TLS_VERSION}")

    with couchdb_admin_session() as session:
        databases = session.all_dbs()
        if "tellme" not in databases:
            session.create_database("tellme")

    # if not AwsTellMeTable.exists():
    #     AwsTellMeTable.create_table(wait=True)

    try:
        asyncio.run(
            main(
                url=settings.ISY_URL,
                username=settings.ISY_USER,
                password=settings.ISY_PWD,
                tls_ver=settings.ISY_TLS_VERSION,
            )
        )
    except KeyboardInterrupt:
        _LOGGER.warning("KeyboardInterrupt received. Disconnecting!")
