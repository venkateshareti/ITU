#stop apache server
systemctl stop httpd
# removing the existing code
rm -rf /opt/ITU_ENV
# created new environment
mkdir /opt/ITU_ENV
# creating virtual environment
python3 -m virtualenv /opt/ituvenv
cd /opt/ITU_ENV
cp -r /opt/latest_code/ITU .
source /opt/ituvenv/bin/activate
echo "virtual environment activated"
cd /opt/ITU_ENV/ITU
pip install -r requirements.txt

systemctl start httpd
echo "apache server running"
echo "Deployment Done"
