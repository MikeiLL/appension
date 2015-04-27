echo "[Unit]
Description=Infinite Glitch

[Service]
ExecStart=`which python` -m fore.server
WorkingDirectory=`pwd`
"|sudo tee /etc/systemd/system/glitch.service >/dev/null
echo "Service file created. To start:"
echo sudo systemctl start glitch.service
