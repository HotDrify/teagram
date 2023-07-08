#!/bin/bash

clear

if sudo -v >/dev/null 2>&1; then
    SUDOCMD="sudo"
else
    SUDOCMD=""
    
fi
printf "                                  \n"
printf " \033[0;36m_____\033[0m                           \n"
printf "\033[0;36m|_   _|___ ___ \033[0m___ ___ ___ _____ \n"
printf "\033[0;36m  | | | -_| .'\033[0m| . |  _| .'|     |\n"
printf "\033[0;36m  |_| |___|__,\033[0m|_  |_| |__,|_|_|_|\n"
printf "\033[0;36m              \033[0m|___|              \n\n"

echo "[INFO] starting installing" > install.log
echo "[DEBUG] SUDOCMD: $SUDOCMD" > install.log

if [[ $OSTYPE == *linux-gnu* ]]; then
    echo "[INFO] found OS type: gnu ($OSTYPE)" > install.log
    PKGINSTALL="apt install -y"
    UPD="apt upgrade -y"
elif [[ $OSTYPE == *linux-android* ]]; then
    echo "[INFO] found OS type: android ($OSTYPE)" > install.log
    PKGINSTALL="pkg install -y"
    UPD="pkg upgrade -y"
else
    echo "[ERROR] os type not found: $OSTYPE" > install.log
    echo "[ERROR] os not found. see logs for more information."
    exit 1
fi
echo "[INFO] updated and upgrading all packages..." > install.log
echo "[INFO] updating..."
eval "$SUDOCMD $UPD"
echo "[INFO] install 4 packages..." > install.log
echo "[INFO] install packages..."
eval "$SUDOCMD $PKGINSTALL git openssl python3 python3-pip"
echo "[INFO] cloning https://github.com/HotDrify/teagram..." > install.log
echo "[INFO] cloning repository..."
eval "git clone https://github.com/HotDrify/teagram"
eval "cd teagram"
echo "[INFO] installing requirements.txt.." > install.log
echo "[INFO] installing libraries..."
eval "pip3 install -r requirements.txt"
echo "[INFO] installing requirements-speedup.txt..." > install.log
echo "[INFO] installing speed libraries..."
eval "pip3 install -r requirements-speedup.txt"
echo "[INFO] first start teagram..." > install.log
echo "[INFO] first start..."
clear
eval "python3 -m teagram"