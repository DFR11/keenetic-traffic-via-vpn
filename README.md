Данный проект позволяет перенаправлять трафик для отдельных ресурсов в VPN-туннель на роутерах [Keenetic](https://keenetic.ru/) с использованием репозитория [Entware](https://entware.net/).

## Installation
Для загрузки и работы установочного скрипта требуется [curl](https://curl.se/). При отсутствии — установить командой:

```shell
opkg install curl
```

To start the installation process, run the command:

```shell
curl -sfL https://raw.githubusercontent.com/DFR11/keenetic-traffic-via-vpn/main/install.sh | sh
```

Установщик создаст каталог `/opt/etc/unblock` (если такой не существует) и поместит в него необходимые файлы. Также будут созданы два симлинка для отслеживания состояния VPN-туннеля и автоматического обновления маршрутов раз в сутки. Для работы скрипта `parser.sh` требуются `bind-dig`, `cron` и `grep` — они будут установлены при отсутствии.

After installation is complete you will need:
- Отредактировать файл `/opt/etc/unblock/config`, указав в переменной `IFACE` название интерфейса VPN, которое можно увидеть в выводе команды `ip address show` или `ifconfig`. Например, `ovpn_br0` (=`OpenVPN0`) или `nwg0` (=`Wireguard0`);
- Заполнить файл `/opt/etc/unblock/unblock-list.txt` доменами и (или) IPv4-адресами (как с префиксом, так и без) ресурсов, трафик до которых вы хотите пустить через VPN;
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

Будут удалены **все** скаченные и созданные установщиком файлы, а также каталог `/opt/etc/unblock`, если в нём не окажется ничего постороннего.
