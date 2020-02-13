# PiNet
## Table of Contents
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
    * [Configuring the Broker](#configuring-the-broker)
    * [Connecting from Client](#connecting-from-client)

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
Navigate to `Interfacing Options->SSH` and enable.
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
We then use the generated CA key (*ca.crt* and *ca.key*) to sign the server certificate.
```
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360
```
We then copy the generated files to the correct places:
```
$ sudo cp ca.crt /etc/mosquitto/ca_certificates/
$ sudo cp server.crt /etc/mosquitto/certs/
$ sudo cp server.key /etc/mosquitto/certs/
```
Then, to configure Mosquitto to use TLS, we generate the config file `/etc/mosquitto/conf.d/mqtt-tls.conf` and add the below to it.
```
port 8883

cafile /etc/mosquitto/ca_certificates/ca.crt
keyfile /etc/mosquitto/certs/server.key
certfile /etc/mosquitto/certs/server.crt
tls_version tlsv1_2
```
After a reboot, or `sudo systemctl restart mosquitto.service`, the Mosquitto broker will require the client to connect using TLS V1.2.

For testing purposes, you can disable the Mosquitto service and run the broker from the command line as below.
```
$ sudo systemctl stop mosquitto.service
$ sudo mosquitto -c /etc/mosquitto/conf.d/mqtt-tls.conf -v
```
#### Connecting from Client
Before the client can attempt to connect to the broker over TLS it requires access to the generated *ca.crt* file. This can be copied over from the server using `scp`:
```
$ scp pi@192.168.0.200:/home/licences/mosquitto/ca.crt ./ca.crt
```
Then to subscribe to a Topic we use:
```
$ mosquitto_sub -h 192.168.0.200 -p 8883 --tls-version tlsv1.2 --cafile Documents/licences/mosquitto-mqtt/ca.crt -t test_topic
```
And to publish to a Topic we use:
```
$ mosquitto_pub -h 192.168.0.200 -p 8883 --tls-version tlsv1.2 --cafile Documents/licences/mosquitto-mqtt/ca.crt -t test_topic -m "Hello World!"
```
