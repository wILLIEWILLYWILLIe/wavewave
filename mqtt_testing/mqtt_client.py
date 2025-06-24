import paho.mqtt.client as mqtt

class MqttPublisher:
    """
    A simple MQTT publisher class for sending messages to MQTT broker.
    """
    def __init__(self, broker="127.0.0.1", port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.__on_connect
        self.connected = False
        
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f'MQTT Publisher connection failed: {e}')
    
    def __on_connect(self, client, userdata, flags, rc, properties):
        print(f"MQTT Publisher connected with result code {rc}")
        self.connected = True
    
    def publish(self, topic, message):
        """Publish a message to a topic"""
        if self.connected:
            self.client.publish(topic, message, qos=0)
        else:
            print(f"MQTT Publisher not connected. Cannot publish to {topic}")
    
    def stop(self):
        """Stop the MQTT client"""
        if hasattr(self, 'client'):
            self.client.loop_stop()
            self.client.disconnect()
