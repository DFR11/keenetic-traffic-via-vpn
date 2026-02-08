
该项目允许在 [Keenetic](https://keenetic.ru/) 路由器上，借助 [Entware](https://entware.net/) 仓库，将**指定资源的流量重定向到 VPN 隧道**中。

## 安装（Installation）

下载安装脚本并正常运行需要 [curl](https://curl.se/)。如果系统中尚未安装，请先执行：

```shell
opkg install curl
```

要开始安装过程，请运行以下命令：

```shell
curl -sfL https://raw.githubusercontent.com/DFR11/keenetic-traffic-via-vpn/main/install.sh | sh
```

安装程序将创建目录 `/opt/etc/unblock`（如果该目录不存在），并将所需文件放入其中。同时还会创建两个符号链接，用于：

* 监控 VPN 隧道状态
* 每天自动更新路由规则

脚本 `parser.sh` 运行时需要 `bind-dig`、`cron` 和 `grep`，如果系统中不存在，这些组件将被自动安装。

---

## 安装完成后需要做的操作

安装完成后，你需要：

* 编辑文件 `/opt/etc/unblock/config`，在变量 `IFACE` 中指定 VPN 接口名称。
  接口名称可通过命令 `ip address show` 或 `ifconfig` 查看，例如：

  * `ovpn_br0`（=`OpenVPN0`）
  * `nwg0`（=`WireGuard0`）
* 编辑文件 `/opt/etc/unblock/unblock-list.txt`，填写需要**通过 VPN 访问的资源**，可以是：

  * 域名
  * IPv4 地址（可带前缀或不带前缀）
* 启动 VPN 连接（如果 VPN 在安装前已启动，则需要重启）

---

## config 文件填写示例

### OpenVPN 隧道示例

```shell
# VPN 隧道接口名称（来自 ifconfig 或 ip address show）
IFACE="ovpn_br0"

# 存放域名和 IP 地址的文件路径
FILE="/opt/etc/unblock/unblock-list.txt"
```

### WireGuard 隧道示例

```shell
# VPN 隧道接口名称（来自 ifconfig 或 ip address show）
IFACE="nwg0"

# 存放域名和 IP 地址的文件路径
FILE="/opt/etc/unblock/unblock-list.txt"
```

---

## unblock-list.txt 填写示例

```
example.com
1.1.1.1
93.184.220.0/24
```

---

## 说明（Comment）

请注意：
**默认情况下，只有来自家庭网络（Bridge0 / br0）中的设备流量才会被重定向到 VPN。**

如果直接在路由器本机上访问资源，流量**不会**通过 VPN 隧道。

如果你希望 **包括路由器本机在内的所有流量** 都通过 VPN，请依次执行以下三条命令：

```shell
ip rule del priority 1995 2>/dev/null
ip rule add table 1000 priority 1995
sed -i 's/iif br0 //' /opt/etc/unblock/start-stop.sh
```

执行后，所有设备（包括路由器自身）的流量都会被重定向。

---

## 卸载（Removal）

要卸载该项目，请运行：

```shell
/opt/etc/unblock/uninstall.sh
```

卸载过程将删除：

* **所有**由安装程序下载和创建的文件
* 目录 `/opt/etc/unblock`（前提是该目录中不存在其他无关文件）

---

如你需要，我也可以：

* 将其整理成 **中文 README**
* 添加 **中文注释版脚本**
* 或结合 Keenetic / Zapret / XKeen 的实际使用场景给出配置建议
