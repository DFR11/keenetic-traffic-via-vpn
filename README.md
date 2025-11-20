This project allows you to redirect traffic for individual resources to a VPN tunnel on [Keenetic](https://keenetic.ru/) routers using the [Entware](https://entware.net/) repository.

## Installation
The installation script requires [curl](https://curl.se/) to download and run. If not, install with the command:

```shell
opkg install curl
```

To start the installation process, run the command:

```shell
curl -sfL [https://raw.githubusercontent.com/rustrict/keenetic-traffic-via-vpn/main/install.sh](https://raw.githubusercontent.com/DFR11/keenetic-traffic-via-vpn/refs/heads/main/install.sh) | sh
```

The installer will create a directory `/opt/etc/unblock` (if it does not exist) and place the necessary files in it. Two symlinks will also be created to monitor the state of the VPN tunnel and automatically update routes once a day. The `parser.sh` script requires `bind-dig`, `cron` and `grep` to work - they will be installed if missing.

After installation is complete you will need:
- Edit the `/opt/etc/unblock/config` file, specifying the name of the VPN interface in the `IFACE` variable, which can be seen in the output of the `ip address show` or `ifconfig` command. For example, `ovpn_br0` (=`OpenVPN0`) or `nwg0` (=`Wireguard0`);
- Fill the file `/opt/etc/unblock/unblock-list.txt` with domains and (or) IPv4 addresses (both with and without a prefix) of the resources to which you want to send traffic through the VPN;
- Start the VPN connection (or restart if it was started before installation).

### Examples of filling out config
For an OpenVPN tunnel:

```shell
# Название интерфейса VPN-туннеля из ifconfig или ip address show
IFACE="ovpn_br0"

# Расположение файла с адресами и доменами
FILE="/opt/etc/unblock/unblock-list.txt"
```

For WireGuard tunnel:

```shell
# Название интерфейса VPN-туннеля из ifconfig или ip address show
IFACE="nwg0"

# Расположение файла с адресами и доменами
FILE="/opt/etc/unblock/unblock-list.txt"
```

### Example of filling unblock-list.txt
```
example.com
1.1.1.1
93.184.220.0/24
```

## Comment
Please note that by default, traffic is redirected only for devices from the Home Network segment (Bridge0). When trying to access directly from the router, the traffic will not be sent to the VPN tunnel. If you are not satisfied with this, run the following three commands in sequence:

```shell
ip rule del priority 1995 2>/dev/null
ip rule add table 1000 priority 1995
sed -i 's/iif br0 //' /opt/etc/unblock/start-stop.sh
```

After this, all devices, including the router itself, will be redirected.

## Removal
To remove, run the command:

```shell
/opt/etc/unblock/uninstall.sh
```

**all** files downloaded and created by the installer will be deleted, as well as the `/opt/etc/unblock` directory, if there is nothing foreign in it.
