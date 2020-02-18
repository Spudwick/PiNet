
from CA_Helper import *


MQTT_CA = CA(ca_id="mqtt-ca")
NodeRed_CA = CA(ca_id="nodered-ca")

NodeRed_CA.gen_crt(cn="Test")

print(repr(NodeRed_CA))
