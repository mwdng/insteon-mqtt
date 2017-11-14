#===========================================================================
#
# Network and serial link management
#
#===========================================================================
import logging
import paho.mqtt.client as paho
from .Link import Link
from .. import Signal


class Mqtt (Link):
    """TODO: doc
    """
    def __init__(self, host, port=1883, id=None, reconnect_dt=10):
        """TODO: doc
        """
        super().__init__()
        self.host = host
        self.port = port
        self.connected = False
        self.id = id if id is not None else "insteon-mqtt"

        # Insure poll is called at least once every 15 seconds so we
        # can send a keep alive message to the server so our
        # connection doesn't get dropped.
        self.time_out = 15

        self.signal_message = Signal.Signal()    # (MqttLink, Message msg)

        self._reconnect_dt = reconnect_dt
        self._fd = None

        self.client = paho.Client(client_id=self.id, clean_session=False)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.log = logging.getLogger(__name__)

    #-----------------------------------------------------------------------
    def load_config(self, config):
        """TODO: doc
        """
        assert(not self.connected)

        self.host = config['broker']
        self.port = config['port']

        username =  config.get('username', None)
        if username is not None:
            password = config.get('password', None)
            self.client.username_pw_set(username, password)

    #-----------------------------------------------------------------------
    def publish(self, topic, payload, qos=0, retain=False):
        """TODO: doc
        """
        self.client.publish(topic, payload, qos, retain)
        self.signal_needs_write.emit(self, True)

        self.log.debug("MQTT publish %s %s qos=%s ret=%s", topic, payload,
                       qos, retain)

    #-----------------------------------------------------------------------
    def subscribe(self, topic, qos=0):
        """TODO: doc
        """
        self.client.subscribe(topic, qos)
        self.signal_needs_write.emit(self, True)

        self.log.debug("MQTT subscribe %s qos=%s", topic, qos)

    #-----------------------------------------------------------------------
    def unsubscribe(self, topic):
        """TODO: doc
        """
        self.client.unsubscribe(topic)
        self.signal_needs_write.emit(self, True)

        self.log.debug("MQTT unsubscribe %s", topic)

    #-----------------------------------------------------------------------
    def fileno(self):
        """TODO: doc
        """
        assert(self._fd)
        return self._fd

    #-----------------------------------------------------------------------
    def poll(self, t):
        """TODO: doc
        """
        # This is required to handle keepalive messages.
        self.client.loop_misc()

    #-----------------------------------------------------------------------
    def retry_connect_dt(self):
        """TODO: doc
        """
        return self._reconnect_dt

    #-----------------------------------------------------------------------
    def connect(self):
        """TODO: doc
        """
        try:
            self.client.connect(self.host, self.port, keepalive=60)
            self._fd = self.client.socket().fileno()

            self.log.info("MQTT device opened %s %s", self.host, self.port)
            return True
        except:
            self.log.exception("MQTT connection error to %s %s", self.host,
                               self.port)
            return False

    #-----------------------------------------------------------------------
    def read_from_link(self):
        """TODO: doc
        """
        status = self.client.loop_read()
        # If status is zero, everything is ok.  Return 1 to tell the
        # link that reading was successful.
        if status == 0:
            return 1

        # Otherwise tell the link that reading failed and we should be
        # closed.
        else:
            return -1

    #-----------------------------------------------------------------------
    def write_to_link(self):
        """TODO: doc
        """
        self.client.loop_write()

        self.log.debug("MQTT writing")

        if not self.client.want_write():
            self.signal_needs_write.emit(self, False)

    #-----------------------------------------------------------------------
    def close(self):
        """TODO: doc
        """
        self.log.info("MQTT device closing %s %s", self.host, self.port)

        self.client.disconnect()
        self.signal_needs_write.emit(self, True)

    #-----------------------------------------------------------------------
    def _on_connect(self, client, data, flags, result):
        """TODO: doc
        """
        if result == 0:
            self.connected = True
        else:
            self.log.error("MQTT connection refused %s %s %s", self.host,
                           self.port, result)

    #-----------------------------------------------------------------------
    def _on_disconnect(self, client, data, result):
        """TODO: doc
        """
        self.log.debug("MQTT disconnection %s %s", self.host, self.port)

        self.connected = False
        self.signal_closing.emit(self)

    #-----------------------------------------------------------------------
    def _on_message(self, client, data, message):
        """TODO: doc
        """
        self.log.info("MQTT message %s %s", message.topic, message.payload)
        self.signal_message.emit(self, message)

    #-----------------------------------------------------------------------
    def __str__(self):
        return "MQTT %s:%d" % (self.host, self.port)
    
    #-----------------------------------------------------------------------
