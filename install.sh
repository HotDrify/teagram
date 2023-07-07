#!/bin/bash
clear
# check sudo status
if [ $EUID != 0 ]; then
    $SUDOCMD=""
else
    $SUDOCMD="sudo"

# logo
printf "                                  \n"
printf " \033[0;36m_____\033[0m                           \n"
printf "\033[0;36m|_   _|___ ___ \033[0m___ ___ ___ _____ \n"
printf "\033[0;36m  | | | -_| .'\033[0m| . |  _| .'|     |\n"
printf "\033[0;36m  |_| |___|__,\033[0m|_  |_| |__,|_|_|_|\n"
printf "\033[0;36m              \033[0m|___|              \n\n"
# install.log
echo "[INFO] starting installing" > install.log
echo "[DEBUG] SUDOCMD: $SUDOCMD" > install.log
# check os
if [[ $OSTYPE == *linux-gnu* ]]; then
    echo "[INFO] found OS type: gnu ($OSTYPE)" > install.log
    $PKGINSTALL="apt install -y"
    $UPD="apt upgrade -y"
elif [[ $OSTYPE == *linux-android.* ]]; then
    echo "[INFO] found OS type: android ($OSTYPE)" > install.log
    $PKGINSTALL="pkg install -y"
    $UPD="pkg upgrade -y"
else
    echo "[ERROR] os type not found: $OSTYPE" > install.log
    echo "[ERROR] os not found. see logs for more information."
# завтра доделаю