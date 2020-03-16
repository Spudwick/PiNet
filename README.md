# PiNet
## About
This repository is for all things related to my RPi based home network. The aim of this project is to explore Networking concepts and system design whilst building a small *"IoT Smart Home"* system. The details laid out below are mainly for me to keep track of stuff I've done/learnt, take everything with a grain of salt as I'm learning as I go myself!

## Table of Contents
* [About](#about)
* [RPi Setup](#rpi-setup)
  * [Formatting SD Card](#formatting-sd-card)
  * [Installing BerryBoot and Raspbian](#installing-berryboot-and-raspbian)
    * [Booting From USB Drive with BerryBoot](#booting-from-usb-drive-with-berryboot)
  * [Basic Raspbian Setup](#basic-raspbian-setup)
    * [Enabling SSH](#enabling-ssh)
    * [Customising Bash Prompt](#customising-bash-prompt)
    * [Changing Hostname](#changing-hostname)
    * [Setting Static IP Address](#setting-static-ip-address)
* [GitHub](#github)
  * [Purging Sensitive Files](#purging-sensitive-files)
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
* [Node-Red](#node-red)
  * [Installing Node-Red](#installing-node-red)
  * [Securing Node-Red](#securing-node-red)
    * [Configuring TLS](#configuring-tls)
    * [Flow Editor Username and Password Authentication](#flow-editor-username-and-password-authentication)
  * [Node-Red Dashboard](#node-red-dashboard)
    * [Installing the Dashboard](#installing-the-dashboard)
    * [Dashboard Username and Password Authentication](#dashboard-username-and-password-authentication)
* [MariaDB](#mariadb)
  * [Configuring MariaDB](#configuring-mariadb)
    * [Configuring Interfaces](#configuring-interfaces)
    * [Changing Database Storage Location](#changing-database-storage-location)
    * [Configuring MariaDB to use TLS](#configuring-mariadb-to-use-tls)
  * [Using MariaDB](#using-mariadb)
    * [Managing Users and Permissions](#managing-users-and-permissions)
    * [Managing Databases and Tables](#managing-databases-and-tables)
* [ESP32 Boards](#esp32-boards)
  * [Setting up Arduino IDE](#setting-up-arduino-ide)
  * [Installing MQTT Client Library](#installing-mqtt-client-library)
* [Useful Commands](#useful-commands)
    
## RPi Setup
### Formatting SD Card
Use `fdisk` to delete all existing partitions and format for FAT32.
Use `fdisk -l` to identify device. Then use following commands to delete partitions and format card.
```
$ sudo fdisk /dev/mmcblk0
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
#### Booting From USB Drive with BerryBoot
The simplist way to configure BerryBoot to boot from a USB attached drive is to just have it connected when you first boot BerryBoot. You can then select it as the target drive. This does have the downside that the entire drive is used for the *Boot* and *Data* partitions.

After some research I came across this post by [Norbert](https://www.raspberrypi.org/forums/viewtopic.php?t=238792) where he describes how to reconfigure BerryBoot after installation to boot the OS from a partition on a USB attached drive. The bootloader still lives and runs from the SD card however.
First we must create the new partition and format it ready for BerryBoot to use. We can follow the same basic steps as when [formatting the SD card to install BerryBoot](#formatting-sd-card) with a few alterations. First we select the USB Drive as the `fdisk` target rather than the SD card.
```
$ sudo fdisk /dev/sda
```
```
Command (m for help): d
Selected partition 1
Partition 1 has been deleted.
```
Then we create a limited size partition, I used 30GB as this was the same size as the SD card partition I'm replacing.
```
Command (m for help): n
Partition type
   p   primary (0 primary, 0 extended, 4 free)
   e   extended (container for logical partitions)
Select (default p): p
Partition number (1-4, default 1): 1
First sector (2048-31116287, default 2048): 
Last sector, +sectors or +size{K,M,G,T,P} (2048-31116287, default 31116287): +30G

Created a new partition 1 of type 'Linux' and of size 30 GiB.
```
And we set it's type to *Linux* to be formated as `ext4`.
```
Command (m for help): t
Selected partition 1
Partition type (type L to list all types): 83
Changed type of partition 'Linux' to 'Linux'.
```
And finally write the partition to the disk.
```
Command (m for help): w
The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.
```
Now we can format the partion as `ext4` using `mkfs`.
```
$ sudo mkfs.ext4 /dev/sda1
```
Finally we can give the partition a meaningful *Label* using:
```
$ sudo e2label /dev/sda1 berryboot_HDD
```
Now the partition should show up under `lsblk` and running `blkid` should show something like below.
```
$ sudo blkid /dev/sda1
/dev/sda1: LABEL="berryboot_HDD" UUID="42a9ceda-a391-41fe-b861-3334426d08b8" TYPE="ext4" PARTUUID="278eb1e0-01"
```
We then need to copy the contents of the `mmcblk0p2` partition into out new `sda1` partition. This can be done using `rsync` as below.
```
$ sudo mkdir /mnt/berryboot_SD
$ sudo mount /dev/mmcblk0p2 /mnt/berryboot_SD
$ sudo mkdir /mnt/berryboot_HDD
$ sudo mount /dev/sda1 /mnt/berryboot_HDD
$ sudo rsync -ax --delete /mnt/berryboot_SD/ /mnt/berryboot_HDD/
```
The final step is to configure BerryBoot to use the new HDD partition rather than the old SD card partition. This is done by modifying the */boot/cmdline.txt* file, changing the `datadev` item as below.
```
datadev=/dev/sda1
```
The RPi can then be rebooted and BerryBoot should boot the OS from the HDD.

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

## GitHub
### Purging Sensitive Files
The following instructions are taken from GitHubs [BFG information](https://help.github.com/en/github/authenticating-to-github/removing-sensitive-data-from-a-repository). 

First of all, make a commit to the Repo that contains the relevant files in a format that you want to keep going forward. Either delete the file completely or replace sensitive information. After this commit the repository files should be as you want it, but the commit history will still show the sensitive data.
Once this is done you need to download the BFG jar file from the [BFG website](https://rtyley.github.io/bfg-repo-cleaner/) and then checkout a seperate copy of the raw GitHub repository. This can be done as below.
```
$ git clone --mirror https://github.com/Spudwick/PiNet/
```
Now we have the raw repository it is time to purge. To do this we run the below, replacing *<filename>* with the name of the file to delete. Bear in mind that this matches against the name not a full path!
 ```
 $ java -jar ~/Downloads/bfg.jar --delete-files <filename> PiNet.git
 ```
 Then run the below to purge all the history logs and check back into the remote repository.
 ```
 $ git reflog expire --expire=now --all && git gc --prune=now --aggressive
 $ git push
 ```
Before you can continue working in any old working copys **YOU MUST BRING IT INLINE WITH THE NEW REMOTE**! This can either be done by deleting and re-cloning the local working copy or by using the below. If you don't do this, when you come to push changes back to the remote wou will push back all the old commits containing the deleted files. This will result in commits being duplicated, one with the file and one without. 
 ```
 $ cd <working_copy>
 $ git fetch origin
 $ git reset --hard origin/master
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

## Node-Red
### Installing Node-Red
The [Node-Red website](https://nodered.org/docs/getting-started/raspberrypi) has specific instructions for installing Node-Red on an RPi.

Node-Red and it's dependancies can be installed by running the following.
```
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```
Once everything has downloaded and installed successfully, the service needs to be enabled (to run on boot) and started as below.
```
$ sudo systemctl enable nodered.service
$ sudo systemctl start nodered.service
```
The Node-Red editor should now be accessable by navigating to `http://<hostname>:1880` in a web browser.
### Securing Node-Red
#### Configuring TLS
Node-Red can be configured to use TLS. To enable this I followed instructions laid out by [Steves Internet Guide](http://www.steves-internet-guide.com/securing-node-red-ssl/) again.

To start we must create the required TLS private key and certificate. Node-Red requires `.pem` files which can be generated in a similar way as we have done before. A signing request is generated as below, noting again that the **Common Name** field must match the **IP Address** or **Hostname** used to access the server.
```
$ openssl genrsa -out node-red-tls-key.pem 2048
$ openssl req -new -sha256 -key node-red-tls-key.pem -out node-red-tls-csr.pem
```
We then sign it using the same CA generated whilst [configuring the Mosquitto Broker for TLS](#configuring-the-broker).
```
$ openssl x509 -req -in node-red-tls-csr.pem -CA ca.crt -CAkey ca.key -CAcreateserial -out node-red-tls-CA-crt.pem -days 360
```
The Key and Certificate files can then be copied into a new folder under the *~/.node-red/* directory.

We then need to actually configure Node-Red to use TLS. This is done by modifying the Node-Red configuration file found at *~/.node-red/settings.js*.
First we must uncomment the below code segments.
```
// The `https` setting requires the `fs` module. Uncomment the following
// to make it available:
var fs = require("fs");
```
```
// The following property can be used to enable HTTPS
// See http://nodejs.org/api/https.html#https_https_createserver_options_requestlistener
// for details on its contents.
// See the comment at the top of this file on how to load the `fs` module used by
// this setting.
//
https: {
   key: fs.readFileSync('privatekey.pem'),
   cert: fs.readFileSync('certificate.pem')
},
```
And modify the `fs.readFileSync('...')` lines to point to our newly generated Private Key and Certificate.

To test you can then stop the running instance of the Node-Red service and run manually using the below. `node-red-log` can also be used to attach to the running Node-Red service's log output.
```
$ sudo systemctl stop nodered.service
$ node-red -s settings.js
```
You should now only be able to connect to the Node-Red server using `https://192.168.0.200:1880`. Upon connecting you should get a warning about **Your connection to this website isn't secure**. This is because your browser doesn't recognise the CA used to sign the TLS Certificate.
#### Flow Editor Username and Password Authentication
Requiring a user to sign in to access the flow editor is again a simple task of modifying some fields in the *settings.js* file. This time we need to uncomment the below segment.
```
// To password protect the Node-RED editor and admin API, the following
// property can be used. See http://nodered.org/docs/security.html for details.
adminAuth: {
   type: "credentials",
   users: [{
      username: "admin",
      password: "$2a$08$BHUlBwB9FpqNwtKwf3A8zONkn1NS0vzb702YV5cLquOMo0Wfo57im",
      permissions: "*"
   }]
},
```
To generate a new password for the *admin* account use the `node-red-admin` utility.
```
$ node-red-admin hash-pw
```
This will generate a new password hash that can be copied into the `password` field in the *settings.js* file.
Additional users can be added by appending them to the `users` list.

### Node-Red Dashboard
#### Installing the Dashboard
Complete instructions for Node-Red dashboard can be found on the [Node-Red website](https://flows.nodered.org/node/node-red-dashboard).

Node-Red modules are installed through *menu->Manage pallete*. To install the Dashboard module, search for `node-red-dashboard` and install. It can also be installed through the command line by running the below in the *~/.node-red/* directory.
```
$ npm i node-red-dashboard
```
#### Dashboard Username and Password Authentication
To require usert ot login when accessing the Dashboard page, the below segment of the *settings.js* file must be uncommented.
```
// To password protect the node-defined HTTP endpoints (httpNodeRoot), or
// the static content (httpStatic), the following properties can be used.
// The pass field is a bcrypt hash of the password.
// See http://nodered.org/docs/security.html#generating-the-password-hash
httpNodeAuth: {user:"user",pass:"$2a$08$zZWtXTja0fB1pzD4sHCMyOCMYz2Z6dNbM6tl8sJogENOMcxWV9DN."},
```
Again, the password hash is generated using `node-red-admin hash-pw`. Note that in this case only a single user account is allowed.

## MariaDB
MariaDB is a database system very much related to mySQL. It is meant to be more efficient hence me choosing to use it. It can be installed simply using:
```
$ sudo apt-get install mariadb-server
$ sudo mysql_secure_installation
```
The `mysql_secure_installation` configures the servers security options. I found it asked for root credentials on logging in, which I hadn't been able to set yet. Running the script without `sudo` always resulted in **ERROR 1698 (28000): Access denied for user 'root'@'localhost'** whether I entered a password or not. Running with `sudo` allowed me to login without a password and then set one as part of the secure install script.

You can then test the install by running the below.
```
$ sudo mysql -u root -p
```
### Configuring MariaDB
#### Configuring Interfaces
Initially MariaDB is only configured to listen on `localhost`. This can be changed by editing the line below in */etc/mysql/mariadb.conf.d/50-server.cnf* and restarting the service. `0.0.0.0` can be used to listen on all interfaces and more than one `bind-address` line can be used to specify a selection of interfaces.
```
# Instead of skip-networking the default is now to listen only on
# localhost which is more compatible and is not less secure.
bind-address            = 127.0.0.1
```
MariaDB (and mySQL) listens on port `3306` by default. This can be changed too by editing the below in the same file as above.
```
#
# * Basic Settings
#
...
#port                   = 3306
...
```
Assuming you have a User configured with the correct permissions, local and remote clients should be able to connect as below.
```
$ sudo mysql -P <port> -u <username> -p
$ sudo mysql -h <host> -P <port> -u <username> -p
```
The setup of databases and tables is handled within the client using specific commands. Some are gone through here, but [this page](http://g2pc1.bu.edu/~qzpeng/manual/MySQL%20Commands.htm) contains a list of some helpfull ones.
#### Changing Database Storage Location
As part of the PiNet project, I want to store the databases files on a partition on an exernal hard drive mounted to the the RPi. This is auto-mounted to */mnt/db_store/* by adding the following to */etc/fstab*.
```
LABEL=db_store  /mnt/db_store   ext4    defaults          0       2
```
The folder which will be used to store the database must have owners and permissions matching that of the default Data Directory used by MariaDB.
```
$ ls -al /var/lib/mysql
drwxr-xr-x  5 mysql mysql     4096 Mar 15 16:08 .
```
Once this is setup, we need to configure MariaDB to use the new directory. First, stop the MariaDB service, using `sudo systemctl stop mariadb.service`, and then modify the `datadir` feild in */etc/mysql/mariadb.conf.d/50-server.cnf* to point to our new directory.
```
#
# * Basic Settings
#
...
datadir                 = /mnt/db_store/mariadb
...
```
Finally we must initialise the new database directory, restart the MariaDB service and re-run the secure install proccess.
```
$ sudo mysql_install_db
$ sudo systemctl start mariadb.service
$ sudo mysql_secure_installation
```
#### Configuring MariaDB to use TLS
Helpfull instruction for configuring TLS can be found on the [MariaDB webiste](https://mariadb.com/kb/en/securing-connections-for-client-and-server/).

First we need to generate a Server Key Pair and Certificate just as when [configuring Mosquitto to use TLS](#configuring-the-broker). Note that these need to be in the `.pem` format. It is also important to ensure that the `mysql` user has permissions to read the files.

We then configure MariaDB to use TLS by specifying the paths to the files generated above in the */etc/mysql/mariadb.conf.d/50-server.cnf* config file.
```
#
# * Security Features
#
# Read the manual, too, if you want chroot!
#chroot = /var/lib/mysql/
#
# For generating SSL certificates you can use for example the GUI tool "tinyca".
#
ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/mariadb-svr-crt.pem
ssl-key = /etc/mysql/certs/mariadb-svr-key.pem
#
# Accept only connections using the latest and most secure TLS protocol version.
# ..when MariaDB is compiled with OpenSSL:
#ssl-cipher = TLSv1.2
# ..when MariaDB is compiled with YaSSL (default in Debian):
ssl = on
```
As my version of MariaDB uses *YaSSL* I used the `ssl` option. Some other versions of MariaDB may need you to use `ssl-cipher` instead.

Restart the MariaDB service using `sudo systemctl restart mariadb.service` and login to the server using the root user to check that *TLS* was configured successfully.
```
MariaDB> SHOW GLOBAL VARIABLES LIKE 'have_ssl';
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| have_ssl      | YES   |
+---------------+-------+
```
If this is still returning *Disabled*, check the MariaDB log files to ensure there were no errors whilst setting up *TLS*. I found setting the, in my case, un-needed `ssl-cipher` option caused errors that prevented *TLS* being setup but didn't prevent the service from starting.

Now to connect to the server from a remote client using *TLS* we can run:
```
$ sudo mysql --ssl-ca=ca.crt --ssl-verify-server-cert -h <host> -u <username> -p
```
The server can be configured to require a specific user to connect using *TLS*, [amongst other things](https://mariadb.com/kb/en/securing-connections-for-client-and-server/#requiring-tls), by doing the following. `%` can be used as a wildcard in the host field.
```
MariaDB> ALTER USER '<username>'@'<host>' REQUIRE SSL;
```
### Using MariaDB
#### Managing Users and Permissions
As part of the `mysql_secure_installation` script, you can disable remote access for the `root` user. In this case you won't be able to login to the server remotely until you create a new User. To do this you need to login to the server locally using root, as below.
```
$ sudo mysql -u root -p
```
Then, the SQL command to add a user is:
```
MariaDB> GRANT ALL PRIVILEGES ON <database>.<table> TO '<username>'@'<host>' IDENTIFIED BY '<password>' WITH GRANT OPTION;
```
With regards to the **database** and **table** fields, `*` can be used to indicate *all*. Likewise `%` can be used as a wildcard for the **host** field. Thus, to give a user **Read Only** access to all tables in a specific database you would use:
```
MariaDB> GRANT SELECT ON test_database.* TO 'test'@'192.168.0.%' IDENTIFIED BY 'test_password' WITH GRANT OPTION;
```
Or to grant a user **All Priviledges** to all databases and tables from any host, you would use:
```
MariaDB> GRANT ALL PRIVILEGES ON *.* TO 'test'@'%' IDENTIFIED BY 'test_password' WITH GRANT OPTION;
```
To list a users priviledges you can use the below. The **host** field can be omitted to list permissions from all hosts.
```
MariaDB> SHOW GRANTS FOR '<username>'@'<host>';
```
And to revoke all permissions for a user you would use:
```
MariaDB> REVOKE ALL PRIVILEGES, GRANT OPTION FROM '<username>'@'%';
```
It is worth noting that this doesn't actually remove the User, just their permissions. They will still be able to log into the server. To completely remove the user you would use:
```
MariaDB> DROP USER <username>;
```
#### Managing Databases and Tables
A new database can be added using the command below.
```
MariaDB> CREATE DATABASE <database>;
```
A table is then added to a database using:
```
MariaDB> USE <database>;
MariaDB> CREATE TABLE <table> (
    -> <column> <data_type>,
    -> ...
    ->);
```
[W3 Schools](https://www.w3schools.com/sql/sql_datatypes.asp) has a very helpfull page that lists all the possible datatypes.

New tables can also be made using Sub-Sets of an existing table using the below.
```
MariaDB> USE <database>;
MariaDB> CREATE TABLE <dest_table> AS SELECT <src_column>, ... FROM <src_table>;
```
Tables and Databases can then be deleted using the following.
```
MariaDB> USE <database>;
MariaDB> DROP TABLE <table>;
```
```
MariaDB> DROP DATABASE <database>;
```

## ESP32 Boards
### Setting up Arduino IDE
The Arduino IDE doesn't support the ESP32 based boards out of the box, it needs to be configured as in [Espressif's instructions](https://github.com/espressif/arduino-esp32/blob/master/docs/arduino-ide/boards_manager.md).
First, the Espressif source needs to be added to the package manager by adding `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json` to the *Additional Boards Manager URLs* under *File->Preferences*.
Once this has been added, you should be able to find the `esp32` package under the Package Manager.

To test, select the `DOIT ESP32 DEVKIT V1` board and try programming one of the test sketches installed alongside the esp32 boards. A good one to try is the `WiFiScan` sketch. This should work, however I got **"No module named serial"** errors whilst attempting to connect to the board. These turned out to be because I didn't have *pyserial* installed. This can be installed as below.
```
$ sudo python -m pip install pyserial
```
### Installing MQTT Client Library
For this project I will be using the [PubSubClient library](https://github.com/knolleary/pubsubclient) by Knolleary. To install, download the *.zip* from GitHub. This then needs to be extracted to your Arduino installations library folder. For a Linux install this is likely to be something like `~/Documents/Arduino/Library`. Once this has been completed you should be able to access the library by adding the below to the top of your source file.
```
#include <PubSubClient.h>
```

## Useful Commands
* `sudo systemctl [start|stop|restart] <service>` - Start, Stop or Restart a service.
* `sudo systemctl --type=service --state=running` - List all running services.
* `openssl x509 -in cert.crt -out cert.pem` - Convert `.crt` file to `.pem` file.
* `git update-index --skip-worktree <path>` - Keep file in Repo but don't track changes **(Only effects local working branch)**.
* `git update-index --no-skip-worktree <path>` - Resume tracking for file in Repo **(Only effects local working branch)**.
