#ifndef __CONFIG_H
#define __CONFIG_H


#define NODE_ID         12345       // Numerical Node ID
#define DEBUG           1           // Compile with debugging
#define WIFI_TIMEOUT    5           // Timeout for connecting to WiFi SSID (s)
#define SNSR_POLL_INTVL 1*60        // Sensor Polling interval (s)
#define MQTT_PORT       1883        // Port of MQTT Broker

IPAddress broker(192,168,0,150);

enum pins_e {
  PIN_AWAKE	= 25,
  PIN_CONN	= 26,
  PIN_ERROR	= 27,
};


#endif
