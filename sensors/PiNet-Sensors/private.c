
#include "private.h"


//=============================================================
// This file contains sensitive data related to network
// connection. Before the code will work these strings must be
// replaced with valid data.
//=============================================================

// List of Network SSIDs
struct ssid_s ssid_lst[2] = {
	{"***", "***"},
	{"***", "***"},
};

// CA Certificate (For TLS V1.2)
const char* ca_crt =\
"***";

// Client Private Key (For MQTT Client Authentication)
const char* client_key =\
"***";

// Client Certificate (For MQTT Client Authentication)
const char* client_crt =\
"***";
