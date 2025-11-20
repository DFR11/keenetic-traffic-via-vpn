#!/bin/sh

check_command() {
  command -v "$1" >/dev/null 2>&1
}

msg() {
  printf "%s\n" "$1"
}

error_msg() {
  printf "[!] %s\n" "$1"
}

failure() {
  error_msg "$1"
  exit 1
}

pkg_install() {
  msg "Installing the package\"${1}\"..."
  if opkg install "$1" >/dev/null 2>&1; then
    msg "Plastic bag \"${1}\"installed."
  else
    failure "Error installing package\"${1}\"."
  fi
}

download() {
  check_command curl || failure "Curl is required to download files."
  if curl -sfL --connect-timeout 7 "$1" -o "$2"; then
    msg "File\"${2##*/}\"jumped."
  else
    failure "Failed to download file\"${2##*/}\"."
  fi
}

mk_file_exec() {
  check_command chmod || failure "Changing file permissions requires chmod."
  if chmod +x "$1" 2>/dev/null; then
    msg "Execution rights have been set for the file\"${1}\"."
  else
    failure "Failed to set execution rights for file\"${1}\"."
  fi
}

crt_symlink() {
  check_command ln || failure "To create symlinks, ln is required."
  if ln -sf "$1" "$2" 2>/dev/null; then
    msg "In the directory \"${2%/*}\"symlink created\"${2##*/}\"."
  else
    failure "Failed to create symlink\"${2##*/}\"."
fi
}

msg "Installing keenetic-traffic-via-vpn..."

INSTALL_DIR="/opt/etc/unblock"
REPO_URL="https://raw.githubusercontent.com/rustrict/keenetic-traffic-via-vpn/main"

check_command opkg || failure "Opkg is required to install packages."
opkg update >/dev/null 2>&1 || failure "Failed to update Entware package list."

for pkg in bind-dig cron grep; do
  [ -n "$(opkg status ${pkg})" ] && continue

  pkg_install "$pkg"
  sleep 1

  if [ "$pkg" = "cron" ]; then
    sed -i 's/^ARGS="-s"$/ARGS=""/' /opt/etc/init.d/S10cron && \
    msg "Cron flooding is disabled in the router log."
    /opt/etc/init.d/S10cron restart >/dev/null
  fi
done

if [ ! -d "$INSTALL_DIR" ]; then
  if mkdir -p "$INSTALL_DIR"; then
    msg "Catalog\"${INSTALL_DIR}\"created."
  else
    failure "Failed to create directory \"${INSTALL_DIR}\"."
  fi
fi

[ ! -f "${INSTALL_DIR}/config" ] && download "${REPO_URL}/config" "${INSTALL_DIR}/config"

for _file in parser.sh start-stop.sh uninstall.sh; do
  download "${REPO_URL}/${_file}" "${INSTALL_DIR}/${_file}"
  mk_file_exec "${INSTALL_DIR}/${_file}"
done

crt_symlink "${INSTALL_DIR}/parser.sh" "/opt/etc/cron.daily/routing_table_update"
crt_symlink "${INSTALL_DIR}/start-stop.sh" "/opt/etc/ndm/ifstatechanged.d/ip_rule_switch"

if [ ! -f "${INSTALL_DIR}/unblock-list.txt" ]; then
  if touch "${INSTALL_DIR}/unblock-list.txt" 2>/dev/null; then
    msg "File\"${INSTALL_DIR}/unblock-list.txt\"created."
  else
    error_msg "Failed to create file\"${INSTALL_DIR}/unblock-list.txt\"."
  fi
fi

printf "%s\n" "---" "Installation is complete."
msg "Don't forget to enter the name of the VPN interface in the config file, and also fill out the unblock-list.txt file."

exit 0
