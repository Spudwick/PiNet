
#include <WiFiClientSecure.h>     // ESP32 Secure WiFi Library
#include <PubSubClient.h>         // MQTT Pub/Sub Library


#define DEBUG           1                     // Compile with debugging
#define WIFI_TIMEOUT    5                     // Timeout for connecting to WiFi SSID (s)
#define MQTT_TIMEOUT    5                     // Timeout for MQTT Operations (s)
#define SNSR_POLL_INTVL 5                     // Sensor Polling interval (s)
#define MQTT_PORT       1883                  // Port of MQTT Broker

const char *broker = "192.168.0.150";         // MQTT Broker IP Address


// Certificate Authority Certificate
const char *ca_crt = \
"-----BEGIN CERTIFICATE-----\n"\
"MIIDpzCCAo+gAwIBAgIUY3gV0OHCV9jhT2NS2/jDLVewbHkwDQYJKoZIhvcNAQEL\n"\
"BQAwYzELMAkGA1UEBhMCVUsxETAPBgNVBAgMCE1pZGxhbmRzMRMwEQYDVQQHDApC\n"\
"aXJtaW5naGFtMREwDwYDVQQKDAhDQW1hc3RlcjELMAkGA1UECwwCQ0ExDDAKBgNV\n"\
"BAMMA1RvbTAeFw0yMDAyMTMyMTE1MzVaFw0yNTAyMTIyMTE1MzVaMGMxCzAJBgNV\n"\
"BAYTAlVLMREwDwYDVQQIDAhNaWRsYW5kczETMBEGA1UEBwwKQmlybWluZ2hhbTER\n"\
"MA8GA1UECgwIQ0FtYXN0ZXIxCzAJBgNVBAsMAkNBMQwwCgYDVQQDDANUb20wggEi\n"\
"MA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDUNlINuafNZsuRCM1fHO5QPlGR\n"\
"5ms0FoWCXC9p7EB+lbfNb4I8iJkUJzmBRdfMckloIV6CdIY8k/26YrSXfppg4naD\n"\
"q5eIyocjTUrboS3kBdGVSNHCXELmqb2WrZiQ95+BxAfOzqPyJ2Ab3/m0mGKij0xn\n"\
"dUUtwwswDpFoi2uFwzocMtLJJD7D0pY32nxXIAGg170/I3dZsjdXeg8WNPud3QzO\n"\
"y9Q290fBeqh/OLiPsVz+twYmFJzYc4RS/q9B/eN5Ad8l5Y22pw6e2g/k3VaWdciO\n"\
"Zz+IoRAO889rX0GAhhmIyy51r/d1jTByfq5cQQxC+Qr992Pnb1KblYxKnDhRAgMB\n"\
"AAGjUzBRMB0GA1UdDgQWBBTc2sOnz3e1sS7ENkaoE59WWZpCuDAfBgNVHSMEGDAW\n"\
"gBTc2sOnz3e1sS7ENkaoE59WWZpCuDAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3\n"\
"DQEBCwUAA4IBAQBvDKKXcNsHIz6wgbxdBOhjzduf4F6SZqBoQ86nqNDLyVaFOwiU\n"\
"JmCmChxs4/Y/ZtDXWyzMYGOEKWkyJhB67pkpGyFE1b5MzkdO9bLNytxVevN0WHf0\n"\
"woEoH9P9n32o4ICTZWV2vwUcOjFwa/rYYuuLYknKivff0jzxmVwxbZ1efTlFEmma\n"\
"ZA/CiahxO2iprxNWV6naN3z/pgzLcMyZRKEdY0rWQNl1kGZgrkb7nrzgYEBimHP9\n"\
"3UlW3xiexTWEFrHTpWbxxslA/UjvWScP2p4Hs48Q5NYtjFbDVT0HLibfW2B9cGOJ\n"\
"ZvpQC3A2jGjo6QRodAGfDZmqHolEqBHNoAmH"\
"-----END CERTIFICATE-----";

// Client Private Key
const char *client_key =\
"-----BEGIN RSA PRIVATE KEY-----\n"\
"MIIEpQIBAAKCAQEA1XWuI+U6sg2c//7PLQZ/pAhhkr+0PnGZxkMbddvAe/k8Piqd\n"\
"8FFsb2w1Cu4Wo+wdxhXN7gwHUVhIQ0K/c0dUUgVARbf+rItaOsvH+2nAN6ZrO5Pe\n"\
"f/l4cZwdJfyBnugx6RrVFfeJDOJ8MU1wYLJ78U+Rik8Uae+FcxHquDu/QWQHeIDg\n"\
"3xt2HesI8xy5w7UFhHdG+ZaDeRBQHHoAUYOY8Oi7h8Upk6gQyr3hWKXxZl0ENIzI\n"\
"j8TZ7CHKgM+sBJUt1mwx6dJMqsVrx2cqyh0avBtb/EGuit5BtVsV3LA/Vw8QH+WT\n"\
"aCdj9c/tQ4Sc3hfHMowlTmQttL2ISC97Yj/DYQIDAQABAoIBAQCiKsZCdPrznE4D\n"\
"WhURMtezyb4/G68WpX1a1068alfAl6fB3uSgV2uW9tERXbILlO1FuPj6+V5x2S0F\n"\
"FGeYb79KlLyweslbUn8ZHgnvIfcrEB51Y7Bs7x0myqCGZGAhVmvcmUr7ZlRTWplZ\n"\
"Z2iRvedVe8qpFcz/cj2jHyCAGLwDM1RE3SsYwJdi1FlBh0djrTKTR1Fs6dq/P6Ml\n"\
"80KDxdMvkj2wPs1vfTFTkvA45U/QueJhPZ3rerNwUSDWP3RzisXC4DPoUvwatsU6\n"\
"F0Dwd9jfnaco/ddTR4I5ZdNXHgYrK/G5r5i+IY6XuTWMyZXijhOMqZjohAEAehuj\n"\
"0p1/p1H1AoGBAPpxDNXJcXEItlkhIRuA4UoArqRhwS9GHeIFjLCFeoCTnXnti08E\n"\
"7UrOLNS2oTRsB9Iwq3qEXA8q8Lc8ehHhzgb4FwvNbTM/DEQGm55PEDYSMdBgO2bB\n"\
"QsMaxp57nKGwOfPsuiHhPVGYz00W20gk0ruF0apyuLvoqyB6CevjSQsXAoGBANoy\n"\
"gfOo0jY4SfpmtXnABO6dnGxWMrbTl5w1IzRgTL6lGHhqY+d40+7C7pPwAUojSbfz\n"\
"Ws1naBPmfebXOd6L0QhZY5kgxBMVJzQO0rNhCNMKbfXtGp08niUjhg+FuDnPJzAH\n"\
"Ni/6Fjrk05kyeyz1BDVQQ7gcTSIBfQnfN0GwvdBHAoGBAORGF0TmkJhPMKadI+hF\n"\
"2RPy+zyqPcQxTRuvo0Vi5P49jtSMSOaFvyToOMTKkrWNorNb2XGbI65PnYnnffy+\n"\
"rWR8zcTcQiTr2upGe6IYvtYKT413qa1Hiur7hP7//Q0D7E8B/8bR32p4tru1kbp4\n"\
"lfyHRUzvtKLSuOipVFHGodWRAoGACnKUqlgRCKuVTzoPwm6hTdOaI83Uy9BB2Cbr\n"\
"MpzRz+cTzuA5PGIas7n9tnOtfCFIbFhopqEm6J0GtkDj8nX7Ykz1aeWZvdgrcmCr\n"\
"Ug95XrGHJlleBt1aLSkQSDn84je7Bp+xxoZQ/izqvNEf+L0aoHrhYzVntBMiK5DW\n"\
"knyl+g0CgYEAys8rzP6UYIfmfFjJ2OmxcTKDV6FO+P22+sjDVr6AdZE8lvhMVT2M\n"\
"PD/5B2JAq2r4Av8pL+9MGhGz3Zgk4ha1w4vKBiKxxXbIp8/ZQVd7H1U3DTbN3wHH\n"\
"P88i9Gb+WVQQ5j0YjJPh6SQxwSh+JUptRDeVolHv1iExwAlp2FKWGBY=\n"\
"-----END RSA PRIVATE KEY-----";

// Client Authentication Certificate
const char *client_crt =\
"-----BEGIN CERTIFICATE-----\n"\
"MIIDYDCCAkgCFCVLnvsNzidqpfO7OKN/VsMXO1OgMA0GCSqGSIb3DQEBCwUAMGMx\n"\
"CzAJBgNVBAYTAlVLMREwDwYDVQQIDAhNaWRsYW5kczETMBEGA1UEBwwKQmlybWlu\n"\
"Z2hhbTERMA8GA1UECgwIQ0FtYXN0ZXIxCzAJBgNVBAsMAkNBMQwwCgYDVQQDDANU\n"\
"b20wHhcNMjAwMzAxMTkxNDQ2WhcNMjEwMjI0MTkxNDQ2WjB2MQswCQYDVQQGEwJV\n"\
"SzEWMBQGA1UECAwNV2VzdCBNaWRsYW5kczETMBEGA1UEBwwKQmlybWluZ2hhbTEO\n"\
"MAwGA1UECgwFUGlOZXQxFDASBgNVBAsMC1BpTmV0LWVzcDMyMRQwEgYDVQQDDAtl\n"\
"c3AzMi0xMjM0NTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANV1riPl\n"\
"OrINnP/+zy0Gf6QIYZK/tD5xmcZDG3XbwHv5PD4qnfBRbG9sNQruFqPsHcYVze4M\n"\
"B1FYSENCv3NHVFIFQEW3/qyLWjrLx/tpwDemazuT3n/5eHGcHSX8gZ7oMeka1RX3\n"\
"iQzifDFNcGCye/FPkYpPFGnvhXMR6rg7v0FkB3iA4N8bdh3rCPMcucO1BYR3RvmW\n"\
"g3kQUBx6AFGDmPDou4fFKZOoEMq94Vil8WZdBDSMyI/E2ewhyoDPrASVLdZsMenS\n"\
"TKrFa8dnKsodGrwbW/xBroreQbVbFdywP1cPEB/lk2gnY/XP7UOEnN4XxzKMJU5k\n"\
"LbS9iEgve2I/w2ECAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAXSUta0jnWDos2M2P\n"\
"rTAqJsExSIfQPZNWJIuQpDdn7ynV1+yfeaTpxgc/oQ0iQhehmAZjreglv7IZOMnK\n"\
"WWq1rfp3gaXZwFZGubV86AUAWmEAP0FfRR2fpaqnkUJZozGhfirl83QCs/CDB3Zb\n"\
"WnRsKn6OZh6s/YAk7MXMmSdqTYCatXbxXbdtnKyRLIJUg1w2g3at1PqtMWCA/8Fc\n"\
"OQ0c7me3fUP/X3F3pmTSo11wsQ1a5LTLyyuKzTNEbikLEjb92jL7xVVSLHuXNk3+\n"\
"rqXTewduGbiYTx27VhnXBVj/GMEjlkNCuqPy30JB/gkEiaMYNPQCfd09oalbiEJe\n"\
"TOQjdQ==\n"\
"-----END CERTIFICATE-----";


#define S2uS            1000000ULL                        // Conversion factor for Seconds to Micro-Seconds
#define ARY_LEN(ary)    (sizeof(ary) / sizeof(ary[0]))    // Get number of elements in array
#if(DEBUG==1)
  #define DBG_PRINTF(...)  Serial.printf(__VA_ARGS__)
#else
  #define DBG_PRINTF(...)
#endif


// List of possible SSIDs
struct ssid_s {
  const char* ssid;
  const char* pass;
};
struct ssid_s ssid_lst[] = {
  {"***", "***"},
  {"***", "***"},
};

struct client_s {
  WiFiClientSecure wifi;
  PubSubClient mqtt;
};
struct client_s client;


void enter_sleep(void);                     // Enter Deep Sleep Mode.
void error_halt(void);
int connect_wifi(ssid_s* ssids, int cnt);   // Connect to one of provided SSIDs.
int connect_mqtt(struct client_s* client, const char* broker, int port);


void setup()
{
#if(DEBUG==1)
  Serial.begin(115200);
#endif
  
  DBG_PRINTF("Started with Debugging...\n");

  if( connect_wifi(ssid_lst, ARY_LEN(ssid_lst)) < 0 )
    error_halt();
  
  if( connect_mqtt(&client, broker, MQTT_PORT) < 0 )
    error_halt();
}

void loop()
{
  DBG_PRINTF("[MQTT:%s@%d] PUBLISH \"Hello from esp32\"\n",broker,MQTT_PORT);
  client.mqtt.publish("test_topic","Hello from esp32");

  enter_sleep();
}


void enter_sleep(void)
{
  DBG_PRINTF("Going to sleep for %ds...\n", SNSR_POLL_INTVL);  
  esp_sleep_enable_timer_wakeup(SNSR_POLL_INTVL * S2uS);      // Configure wakeup time
  esp_deep_sleep_start();                                     // Enter Deep Sleep
}

void error_halt(void)
{
  DBG_PRINTF("An ERROR has occured!!!\n");

  // TODO: Indicate error with LED.

  enter_sleep();
}

int connect_wifi(ssid_s* ssids, int cnt)
{
  int idx=0, n=0, found=0;

  WiFi.mode(WIFI_STA);          // Ensure Radio is in Station Mode
  WiFi.disconnect();            // Ensure WiFi is disconnected
  delay(100);

  if(cnt <= 1)
    goto _connect;

  DBG_PRINTF("Scanning for WiFi Networks...\n");
  n = WiFi.scanNetworks();
  DBG_PRINTF("Found %d:\n",n);

  for(int i=0; i<n; i++)
  {    
    DBG_PRINTF("  %s @ %d\n",WiFi.SSID(i).c_str(),WiFi.RSSI(i));

    for(idx=0; idx<cnt; idx++)
    {
      if(strlen(WiFi.SSID(i).c_str()) != strlen(ssids[idx].ssid))
        continue;

      if(strncmp(WiFi.SSID(i).c_str(),ssids[idx].ssid,strlen(ssids[idx].ssid)) == 0)
      {  
        goto _connect;
      }
    }
  }

  return -1;

_connect:
  DBG_PRINTF("Connecting to %s : %s\n",ssids[idx].ssid,ssids[idx].pass);

  WiFi.begin(ssids[idx].ssid,ssids[idx].pass);

  for(n=0; ( (n<(2*WIFI_TIMEOUT)) && (WiFi.status() != WL_CONNECTED) ); n++)
  {
    DBG_PRINTF(".");
    delay(500);
  }
  if(n >= 2*WIFI_TIMEOUT)
  {
    DBG_PRINTF("\nConnection Timed Out!\n");
    WiFi.disconnect();
    return -2;
  }
  DBG_PRINTF("\nConnected Succesfully!\n");

  delay(100);

  return idx;
}

int connect_mqtt(struct client_s* client, const char* broker, int port)
{
  int i=0;

  client->wifi = WiFiClientSecure();
  client->wifi.setCACert(ca_crt);               // CA Certificate for TLS V1.2
  client->wifi.setPrivateKey(client_key);       // Client Private Key for Client Athentication
  client->wifi.setCertificate(client_crt);      // Client Certificate for Client Athentication

  client->mqtt = PubSubClient(client->wifi);
  client->mqtt.setServer(broker, port);         // Point Client at Broker

  DBG_PRINTF("Connecting to remote MQTT Broker @ %s:%d...\n",broker,port);
  if(!client->mqtt.connect("esp32-12345"))
  {
    DBG_PRINTF("Connection Timed Out!\n");
    return -2;
  }
  DBG_PRINTF("Connected Succesfully!\n");

  delay(100);
  
  return 1;
}
