
#include <WiFiClientSecure.h>         // ESP32 Secure WiFi Client Library
#include <PubSubClient.h>             // MQTT Client Library
#include <Adafruit_BME280.h>          // Adafruit BME280 Sensor Package Library
#include <Arduino_JSON.h>             // Arduino JSON Library

#include "config.h"
#include "private.h"


//====================================================================
// Utility Macros:
//====================================================================
#define S2uS                  1000000ULL                  // Conversion factor for Seconds to Micro-Seconds
#define ARY_LEN(ary)    (sizeof(ary) / sizeof(ary[0]))    // Get number of elements in array
#if(DEBUG==1)
  #define DBG_PRINTF(...)  Serial.printf(__VA_ARGS__)
#else
  #define DBG_PRINTF(...)
#endif

#define STR_HELPER(x)     #x
#define STR(x)            STR_HELPER(x)
#define MQTT_NODE_TOPIC   "/sensors/raw/" STR(NODE_ID)
#define MQTT_CLIENT_NAME  "esp32-" STR(NODE_ID)
//====================================================================


struct client_s {
  WiFiClientSecure wifi;
  PubSubClient mqtt;
};
struct client_s client;

Adafruit_BME280 bme;      // BME280 Sensor on I2C


//====================================================================
// Function Prototypes:
//====================================================================
void enter_sleep(void);                                                   // Enter Deep Sleep Mode.
void error_halt(void);
int connect_wifi(ssid_s* ssids, int cnt);                                 // Connect to one of provided SSIDs.
int connect_mqtt(struct client_s* client, IPAddress* broker, int port);
//====================================================================


void setup()
{
#if(DEBUG==1)
  Serial.begin(115200);   // Startup Serial peripheral
  while(!Serial);         // Wait until Serial peripheral is up and running
#endif
  
  DBG_PRINTF("Started with Debugging...\n");

  // Setup LED Pins.
  pinMode(PIN_AWAKE, OUTPUT);
  digitalWrite(PIN_AWAKE, HIGH);
  pinMode(PIN_CONN, OUTPUT);
  digitalWrite(PIN_CONN, LOW);
  pinMode(PIN_ERROR, OUTPUT);
  digitalWrite(PIN_ERROR, LOW);

  // Connect to WiFi.
  if( connect_wifi(ssid_lst, ARY_LEN(ssid_lst)) < 0 )
    error_halt();

  // Connect to MQTT Broker.
  if( connect_mqtt(&client, &broker, MQTT_PORT) < 0 )
    error_halt();

  // Connect to BME280 Package.
  if( connect_bme280() < 0 )
    error_halt();

  digitalWrite(PIN_CONN, HIGH);       // Indicate through LEDs that we have connected successfully.
}

void loop()
{
  JSONVar json;
  json["temperature"] = bme.readTemperature();        // *C
  json["humidity"] = bme.readHumidity();              // %
  json["pressure"] = bme.readPressure() / 100.0F;     // hPa
  
  DBG_PRINTF("[MQTT:%s@%d] PUBLISH \"%s\"\n",broker.toString().c_str(),MQTT_PORT, JSON.stringify(json).c_str() );
  if( !client.mqtt.publish( MQTT_NODE_TOPIC, JSON.stringify(json).c_str() ) )
    error_halt();

  enter_sleep();
}


//====================================================================
// void enter_sleep(void)
//--------------------------------------------------------------------
// Triggers CPU Deep Sleep mode for SNSR_POLL_INTVL (see config.h)
// seconds.
//====================================================================
void enter_sleep(void)
{
  // Turn off all LEDs.
  digitalWrite(PIN_AWAKE, LOW);
  digitalWrite(PIN_CONN, LOW);
  digitalWrite(PIN_ERROR, LOW);
  
  DBG_PRINTF("Going to sleep for %ds...\n", SNSR_POLL_INTVL);  
  esp_sleep_enable_timer_wakeup(SNSR_POLL_INTVL * S2uS);      // Configure wakeup time
  esp_deep_sleep_start();                                     // Enter Deep Sleep
}
//====================================================================

//====================================================================
// void error_halt(void)
//--------------------------------------------------------------------
// Indicates node is in error using LEDs, then enters Deep Sleep.
//====================================================================
void error_halt(void)
{
  DBG_PRINTF("An ERROR has occured!!!\n");

  digitalWrite(PIN_ERROR, HIGH);        // Indicate Error Status on LEDs.
  delay(1000);

  enter_sleep();                        // Put CPU to sleep.
}
//====================================================================

//====================================================================
// int connect_wifi(ssid_s* ssids, int cnt)
//--------------------------------------------------------------------
// Connect WiFi radio to network, from known SSID/Pasword list, that
// has strongest RSSI.
// Arguments:
//   ssids  = List of SSID/Password Pairs.
//   cnt    = Number of elements in list.
// Returns:
//   >=0    = Index in list of SSID connected.
//   -1     = No SSID Matched.
//   -2     = Timeout whilst connecting.
//====================================================================
int connect_wifi(ssid_s* ssids, int cnt)
{
  int idx=0, n=0, found=0;

  WiFi.mode(WIFI_STA);          // Ensure Radio is in Station Mode
  WiFi.disconnect();            // Ensure WiFi is disconnected
  delay(100);

  // If there are no SSIDs in list, error return.
  if(cnt <= 0)
    return -1;

  DBG_PRINTF("Scanning for WiFi Networks...\n");
  n = WiFi.scanNetworks();      // Scan for SSIDs.
  DBG_PRINTF("Known %d, Found %d:\n",cnt,n);

  // Iterate over each scanned SSID. WiFi.SSID list is ordered from strongest signal to weakest. Scan through
  // list until we find the first known and connect, thus we connect to the strongest AP.
  for(int i=0; i<n; i++)
  {    
    DBG_PRINTF("  %s @ %d\n",WiFi.SSID(i).c_str(),WiFi.RSSI(i));

    // For each scanned SSID, check if it's a known SSID.
    for(idx=0; idx<cnt; idx++)
    {
      // If SSID Strings are not the same length, not a match, continue.
      if(strlen(WiFi.SSID(i).c_str()) != strlen(ssids[idx].ssid))
        continue;

      // If SSID Strings are the same, we have found a known SSID, continue to connect.
      if(strncmp(WiFi.SSID(i).c_str(),ssids[idx].ssid,strlen(ssids[idx].ssid)) == 0)
        goto _connect;
    }
  }

  // If we get here, we didn't match any known and scanned SSIDs, in this case error return.
  return -1;

_connect:
  DBG_PRINTF("Connecting to %s : %s\n",ssids[idx].ssid,ssids[idx].pass);

  // Connect WiFi radio to selected SSID.
  WiFi.begin(ssids[idx].ssid,ssids[idx].pass);

  // Poll WiFi status every 500mS, up to set timeout limit, until connected.
  for(n=0; ( (n<(2*WIFI_TIMEOUT)) && (WiFi.status() != WL_CONNECTED) ); n++)
  {
    DBG_PRINTF(".");
    delay(500);
  }
  // If we hit timeout limit, ensure WiFi is disconnected and error return.
  if(n >= 2*WIFI_TIMEOUT)
  {
    DBG_PRINTF("\nConnection Timed Out!\n");
    WiFi.disconnect();
    return -2;
  }
  DBG_PRINTF("\nConnected Succesfully!\n");

  delay(100);               // Small delay to ensure everything is ready to go.

  return idx;
}
//====================================================================

//====================================================================
// int connect_mqtt(struct client_s* client, IPAddress* broker, int port)
//--------------------------------------------------------------------
// Connect MQTT Client to remote Broker using TLS V1.2 (see ca_crt in
// private.c) and Client Certificate Authentication (see client_key
// and client_crt in private.c).
// Arguments:
//   *client  = Pointer to structure to store client info. 
//   *broker  = Pointer to IP Address of Remote Broker.
//   port     = Port that MQTT service is exposed on Broker.
// Returns:
//   0      = Succesfully Connected.
//   -2     = Timeout whilst connecting.
//====================================================================
int connect_mqtt(struct client_s* client, IPAddress* broker, int port)
{
  int i=0;

  // Setup base WiFi client.
  client->wifi = WiFiClientSecure();
  client->wifi.setCACert(ca_crt);               // CA Certificate for TLS V1.2
  client->wifi.setPrivateKey(client_key);       // Client Private Key for Client Athentication
  client->wifi.setCertificate(client_crt);      // Client Certificate for Client Athentication

  // Setup MQTT Client wrapper.
  client->mqtt = PubSubClient(client->wifi);    // Point at WiFi Client
  client->mqtt.setServer(*broker, port);        // Point Client at Broker

  DBG_PRINTF("Connecting to remote MQTT Broker @ %s:%d...\n",broker->toString().c_str(),port);
  // Attempt to connect to Remote Broker, error return if fails.
  if(!client->mqtt.connect(MQTT_CLIENT_NAME))
  {
    DBG_PRINTF("Connection Timed Out!\n");
    return -2;
  }
  DBG_PRINTF("Connected Succesfully!\n");

  delay(100);               // Small delay to ensure everything is ready to go.
  
  return 1;
}
//====================================================================

//====================================================================
// int connect_bme280(void)
//--------------------------------------------------------------------
// Setup I2C peripheral used to connect to BME280 package.
// Returns:
//   0      = Succesfully Connected.
//   -1     = Failed to connect.
//====================================================================
int connect_bme280(void)
{
  DBG_PRINTF("Connecting to BME280 Package...\n");
  
  if( !bme.begin(0x76) )
  {
    DBG_PRINTF("Failed to connect to package! Sensor ID was %d\n",bme.sensorID());
    return -1;
  }
  DBG_PRINTF("Connected Succesfully!\n");

  delay(100);               // Small delay to ensure everything is ready to go.
}
//====================================================================
