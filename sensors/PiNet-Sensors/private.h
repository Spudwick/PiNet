#ifndef __PRIVATE_H
#define __PRIVATE_H


struct ssid_s {
  const char* ssid;
  const char* pass;
};


// List of possible SSIDs
extern struct ssid_s ssid_lst[1];

// Certificate Authority Certificate
extern const char *ca_crt;

// Client Private Key
extern const char *client_key;

// Client Authentication Certificate
extern const char *client_crt;

#endif
