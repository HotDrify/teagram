apt update
apt upgrade -y
apt install -y openssl git python3 python3-pip 
git clone https://github.com/HotDrify/teagram 
cd teagram 
pip3 install -r requirements.txt 
pip3 install -r requirements-speedup.txt 
python3 -m teagram
