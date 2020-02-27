#!/bin/bash

echo "SETTING UP MQTT"

#apt-get update
#apt-get upgrade

#apt-get install mosquitto mosquitto-clients

read -p "Enable TLS V1.2 (y/n)? " opt_tls
read -p "Require Username and Password (y/n)? " opt_pass
read -p "Require Client Certificates (y/n)? " opt_cert


conf_file="./PINET.conf"
echo "PiNet Configuration File:" > $conf_file
echo " " >> $conf_file

if [ "$opt_tls" == "y" ]; then
	echo "cafile /etc/mosquitto/ca_certificates/ca.crt" >> $conf_file
	echo "keyfile /etc/mosquitto/certs/server.key" >> $conf_file
	echo "certfile /etc/mosquitto/certs/server.crt" >> $conf_file
	echo "tls_version tlsv1_2" >> $conf_file
fi

if [ "$opt_pass" == "y" ]; then
	pass_file="/etc/mosquitto/users.pass"
#	mosquitto_passwd -c $pass_file

	echo "allow_anonymous false" >> $conf_file
	echo "password_file $pass_file" >> $conf_file
fi
