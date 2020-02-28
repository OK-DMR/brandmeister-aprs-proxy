# BrandMeister to APRS gateway


```
cd /opt
git clone https://github.com/smarek/brandmeister-aprs-proxy APRSProxy
apt-get install python3 python3-paho-mqtt python3-pip
pip3 install -r requirements.txt
cp settings.ini.default settings.ini
// update settings.ini with required configuration
// required connection user/pass for mysql and tarantool, aprs call and mqtt channel identification
cp aprs.service /lib/systemd/system/aprs.service
systemctl enable aprs
systemctl start aprs
```

