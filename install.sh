#!/usr/bin/env bash

REPO="https://github.com/HotDrify/teagram.git"

SUDO_CMD=""
if [ ! x"$SUDO_USER" = x"" ]; then
	if command -v sudo >/dev/null; then
		SUDO_CMD="sudo -u $SUDO_USER "
	fi
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
    echo "[INFO] found OS type: gnu ($OSTYPE)" >> install.log
    PKGINSTALL="apt install -y"
    UPD="apt upgrade -y"
if [[ $OSTYPE == *linux-gnu* ]]; then
    echo "[INFO] Found OS type: GNU/Linux ($OSTYPE)" >> install.log
    PKGINSTALL="apt install -y"
    UPD="apt update && apt upgrade -y"
elif [[ $OSTYPE == *linux-android* ]]; then
    echo "[INFO] Found OS type: Android ($OSTYPE)" >> install.log
    PKGINSTALL="pkg install -y"
    UPD="pkg update && pkg upgrade -y"
else
    echo "[ERROR] OS type not found: $OSTYPE" >> install.log
    echo "[ERROR] OS not found. See logs for more information."
    exit 1
fi

echo "[INFO] updated and upgrading all packages..." >> install.log
echo "[INFO] updating..."
eval "$SUDOCMD $UPD"
echo "[INFO] install packages..." >> install.log
if command -v python3 &>/dev/null; then
    echo "[INFO] installing python3..."
    eval "$SUDOCMD $PKGINSTALL python3"
else
    echo "python3 is installed."

if command -v 
echo "[INFO] install packages..."
eval "$SUDOCMD $PKGINSTALL git openssl python python3-pip"
if [[ -d "teagram" ]]; then 
    cd teagram
else
    echo "[INFO] cloning repo $REPO" > install.log
    echo "[INFO] cloning repository..."
    eval "git clone $REPO"
    eval "cd teagram"
fi

if [[ -f "teagram.session" ]]; then
    echo "teagram userbot is already installed. exit..."
    exit
fi


echo "[INFO] installing requirements.txt.." >> install.log
echo "[INFO] installing libraries..."
eval "pip3 install -r requirements.txt"
echo "[INFO] installing requirements-speedup.txt..." >> install.log
echo "[INFO] installing speed libraries..."
eval "pip3 install -r requirements-speedup.txt"
echo "[INFO] first start teagram..." >> install.log
echo "[INFO] first start..."
clear
eval "python3 -m teagram"
