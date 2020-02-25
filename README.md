# PiNet
## About
This repository is for all things related to my RPi based home network. The aim of this project is to explore Networking concepts and system design whilst building a small *"IoT Smart Home"* system. The details laid out below are mainly for me to keep track of stuff I've done/learnt, take everything with a grain of salt as I'm learning as I go myself!

## Table of Contents
* [About](#about)
* [RPi Setup](#rpi-setup)
  * [Formatting SD Card](#formatting-sd-card)
  * [Installing BerryBoot and Raspbian](#installing-berryboot-and-raspbian)
  * [Basic Raspbian Setup](#basic-raspbian-setup)
    * [Enabling SSH](#enabling-ssh)
    * [Customising Bash Prompt](#customising-bash-prompt)
    * [Changing Hostname](#changing-hostname)
    * [Setting Static IP Address](#setting-static-ip-address)
* [MQTT](#mqtt)
  * [Installing Mosquitto MQTT](#installing-mosquitto-mqtt)
  * [Testing Mosquitto MQTT](#testing-mosquitto-mqtt)
  * [Configuring Mosquitto for TLS](#configuring-mosquitto-for-tls)
    * [What is TLS](#what-is-tls)
    * [Configuring the Broker](#configuring-the-broker)
    * [Connecting from Client](#connecting-from-client)
  * [Configuring Mosquitto for Client Authentication](#configuring-mosquitto-for-client-authentication)
    * [Username and Password Authentication](#username-and-password-authentication)
    * [Certificate Authentication](#certificate-authentication)
    
## RPi Setup
### Formatting SD Card
Use `fdisk` to delete all existing partitions and format for FAT32.
Use `fdisk -l` to identify device. Then use following commands to delete partitions and format card.
```
$ fdisk /dev/mmcblk0
```
Delete all existing partitions:
```
Command (m for help): d
Selected partition 1
Partition 1 has been deleted.
```
Create a new partition that spans the whole card:
```
Command (m for help): n
Partition type
   p   primary (0 primary, 0 extended, 4 free)
   e   extended (container for logical partitions)
Select (default p): p
Partition number (1-4, default 1): 1
First sector (2048-31116287, default 2048): 
Last sector, +sectors or +size{K,M,G,T,P} (2048-31116287, default 31116287): 

Created a new partition 1 of type 'Linux' and of size 14.9 GiB.
```
Change the type of the partition to FAT32:
```
Command (m for help): t
Selected partition 1
Partition type (type L to list all types): L

 0  Empty           24  NEC DOS         81  Minix / old Lin bf  Solaris        
 1  FAT12           27  Hidden NTFS Win 82  Linux swap / So c1  DRDOS/sec (FAT-
 2  XENIX root      39  Plan 9          83  Linux           c4  DRDOS/sec (FAT-
 ...          
Partition type (type L to list all types): b
Changed type of partition 'Linux' to 'W95 FAT32'.
```
Write changes to the SD card:
```
Command (m for help): w
The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.
```
Then format the new partition using:
```
$ mkfs.vfat /dev/mmcblk0p1  
```

### Installing BerryBoot and Raspbian
Download BerryBoot ZIP file from the [BerryBoot Website](https://www.berryterminal.com/doku.php/berryboot).
Extract the contents to the newly formatted SD card:
```
$ unzip ./berryboot-20190612-pi0-pi1-pi2-pi3.zip /media/SD_Card
```
Insert the SD card and boot the RPi. Follow the onscreen instructions to install the desired version of Raspbian or other.
Once Raspbian has fully installed, reboot and login as the default user `pi` (default password is `raspberry`). Use the `passwd` command to change the default password and run the following to ensure Raspbian is up-to-date.
```
$ sudo apt-get update
$ sudo apt-get upgrade
```

### Basic Raspbian Setup
#### Enabling SSH
SSH is disabled on Raspbian by default. It can be enabled using:
```
$ sudo raspi-config
```
Navigate to *Interfacing Options->SSH* and enable.
You can also enable SSH by enabling and starting the service as below.
```
$ sudo systemctl enable ssh
$ sudo systemctl start ssh
```
#### Customising Bash Prompt
To customise the Bash prompt edit the definition of `PS1` in the `~/.bashrc` file. I use the below:
```
PS1="${debian_chroot:+($debian_chroot)}\[\e[01;36m\]\u\[\e[m\]@\[\e[01;34m\]\h\[\e[m\] <\[\e[01;33m\]\w\[\e[m\]>: "
```
The changes will take place on reboot, but to test them without having to reboot use `source ~/.bashrc`.
#### Changing Hostname
By default, the RPi has a hostname of `raspberrypi`. This can be changed by editing the 2 files below.
```
$ sudo nano /etc/hostname
$ sudo nano /etc/hosts
```
Then reboot the RPi for the changes to take effect.
#### Setting Static IP Address
The RPi will begin confgured to obtain an IP address automatically through DHCP. It can be configured to use a static IP address by adding the following configuration to `/etc/dhcpcd.conf`.
```
interface eth0
static ip_address=192.168.0.10/24
static routers=192.168.0.1
static domain_name_servers=1.1.1.1 8.8.8.8

interface wlan0
static ip_address=192.168.0.200/24
static routers=192.168.0.1
static domain_name_servers=1.1.1.1 8.8.8.8
```
After rebooting use the following to check configuration.
```
$ ifconfig
$ route -n
$ ping www.google.com
```

## MQTT
### Installing Mosquitto MQTT
Run the following to install and start the Mosquitto MQTT Broker.
```
$ sudo apt-get install mosquitto 
$ sudo systemctl enable mosquitto.service
```
The Mosquitto MQTT client can be installed using:
```
$ sudo apt-get install mosquitto-clients
```

### Testing Mosquitto MQTT
To test the installation of the Mosquitto Broker we can use a client to Subscribe and Publish to a test Topic using the below.
In one terminal tab use the client to subscribe to a test Topic:
```
$ mosquitto_sub -h 192.168.0.200 -t test_topic
```
In another terminal publish a message to the same Topic:
```
$ mosquitto_pub -h 192.168.0.200 -t test_topic -m "Hello World!"
```
If all is working correctly you should see the `mosquitto_sub` tab print out `Hello World!`.

### Configuring Mosquitto for TLS
Most of the below has been taken from this very helpfull [tutorial](http://www.steves-internet-guide.com/mosquitto-tls/).
#### What is TLS
TLS, or Transport Layer Security, is a method of securing a conection between a server and a client. It provides a method for the client to confirm that the server is who it says it is, and then encrypt all further comunications. 3 files are required to setup a TLS secured conection:
1. ca.crt       (CA Certificate)
2. server.key   (Server Key)
3. server.crt   (Server Certificate)

The *server.crt* file is created by signing the *server.key* using the *ca.key* and *ca.crt* files. When a client connects to the server using TLS, the server responds by sending it's Certificate (*server.crt*). The client checks the signature of the Server Certificate using *ca.crt* (Possible as *server.crt* was signed using *ca.crt*). Assuming everything checks out, the client can then use the Servers Public Key, *server.key* (Stored in *server.crt* as part of signing process), to agree a Session Key that can be used to encrypt all further communications.
#### Configuring the Broker
To generate the required certificates and keys we require `openssl`, ensure the package is installed by running:
```
$ sudo apt-get install openssl
```
Now we can start generating the files. First we generate a key pair for the Certificate Authority (CA):
```
$ openssl genrsa -des3 -out ca.key 2048
```
Then generate a CA certificate:
```
$ openssl req -new -x509 -days 1826 -key ca.key -out ca.crt
```
Now make the server key pair that will be used by the broker:
```
$ openssl genrsa -out server.key 2048
```
Now we generate a Certificate Request. When entering the required details, the `Common Name` field is important here. This must be set to either the **IP Address or Hostname** of the broker machine (depending on which is used by the client to connect).
```
$ openssl req -new -out server.csr -key server.key
```
We then use the generated CA key (*ca.crt* and *ca.key*) to sign the server certificate.
```
$ openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360
```
We then copy the generated files to the correct places:
```
$ sudo cp ca.crt /etc/mosquitto/ca_certificates/
$ sudo cp server.crt /etc/mosquitto/certs/
$ sudo cp server.key /etc/mosquitto/certs/
```
Then, to configure Mosquitto to use TLS, we generate the config file `/etc/mosquitto/conf.d/mqtt-tls.conf` and add the below to it.
```
# Specify the publically available CA Certificate.
cafile /etc/mosquitto/ca_certificates/ca.crt

# Specify the file containing the Servers Private Key.
keyfile /etc/mosquitto/certs/server.key

# Specify the Servers Certificate signed by the CA.
certfile /etc/mosquitto/certs/server.crt

# Specify the version of TLS to use.
tls_version tlsv1_2
```
After a reboot, or `sudo systemctl restart mosquitto.service`, the Mosquitto broker will require the client to connect using TLS V1.2.

For testing purposes, you can disable the Mosquitto service and run the broker from the command line as below.
```
$ sudo systemctl stop mosquitto.service
$ sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
```
#### Connecting from Client
Before the client can attempt to connect to the broker over TLS it requires access to the generated *ca.crt* file. This can be copied over from the server using `scp`:
```
$ scp pi@192.168.0.200:/home/licences/mosquitto/ca.crt ./ca.crt
```
Then to subscribe to a Topic we use:
```
$ mosquitto_sub -h 192.168.0.200 --tls-version tlsv1.2 --cafile ./ca.crt -t test_topic
```
And to publish to a Topic we use:
```
$ mosquitto_pub -h 192.168.0.200 --tls-version tlsv1.2 --cafile ./ca.crt -t test_topic -m "Hello World!"
```

### Configuring Mosquitto for Client Authentication
Before configuring Mosquitto for Client Authentication you should first follow the steps to [configure Mosquitto for TLS](#configuring-mosquitto-for-tls) as usernames and passwords are transmitted in raw text and so would be clearly visable on the network without TLS transport encryption.
#### Username and Password Authentication
The first step is to create the password file that Mosquitto will use. This can be done, whilst adding the first user, using the below:
```
$ sudo mosquitto_passwd -c /etc/mosquitto/users.pass <username>
```
The script will prompt you to enter a password for the specified username. Users can then be added and deleted from the file using:
```
$ sudo mosquitto_passwd -b /etc/mosquitto/users.pass <username> <password>
$ sudo mosquitto_passwd -D /etc/mosquitto/users.pass <username>
```
Just like for TLS, we now need to configure the mosquitto configuration files to enable user authentication. Create a new configuration file called `/etc/mosquitto/conf.d/client-auth.conf` and enter:
```
# Require clients to provide identification.
allow_anonymous false

# Specify the password file.
password_file /etc/mosquitto/users.pass
```
Note that when adding users to an active password file, the MQTT broker must be restarted before the new user is made available.

We can then connect to the Brocker using the below commands.
```
$ mosquitto_sub -h 192.168.0.200 --tls-version tlsv1.2 --cafile ./ca.crt -u <username> -P <password> -t test_topic
$ mosquitto_pub -h 192.168.0.200 --tls-version tlsv1.2 --cafile ./ca.crt -u <username> -P <password> -t test_topic -m "Hello World!"
```
#### Certificate Authentication
First we must configure the MQTT broker to require Client Certificates. This can be done by replacing the Mosquitto config file */etc/mosquitto/conf.d/client-auth.conf* with the following.
```
 # Require clients to provide identification.
 allow_anonymous false

 # Configure Broker to require client certificates.
 require_certificate true

 # Pull the Client identity from the Certificate Common Name.
 use_identity_as_username true
```
The next step is to generate Certificates for all the Clients. To do this we require a Certificate Authority Key and Certificate as generated whilst [configuring the Mosquitto Broker for TLS](#configuring-the-broker).
Once this has been completed we can generate a new Public/Private key pair for the client, and use them to generate a Certificate Signing Request.
```
$ openssl genrsa -out $(hostname).key 2048
$ openssl req -new -out $(hostname).csr -key $(hostname).key
```
Whilst filling in the data required for generating the CSR, the only value that is important is the `Common Name`. This will be used in place of a username to identify the client.
We then sign the CSR using the CA Key and Certificate. In a typical setup the client wouldn't be able to do this itself as they won't have access to the CAs Private Key. 
```
$ openssl x509 -req -in $(hostname).csr -CA ca.crt -CAkey ca.key -CAcreateserial -out $(hostname).crt -days 360
```
The client can then connect to the MQTT Broker using:
```
$ mosquitto_sub -h 192.168.0.200 --tls-version tlsv1.2 --cafile ./ca.crt --cert ./$(hostname).crt --key ./$(hostname).key -t test_topic
$ mosquitto_pub -h 192.168.0.200 --tls-version tlsv1.2 --cafile ./ca.crt --cert ./$(hostname).crt --key ./$(hostname).key -t test_topic -m "Hello World!"
```
