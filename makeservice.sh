echo "[Unit]
Description=Infinite Glitch

[Service]
ExecStart=`which python` -m fore.server
WorkingDirectory=`cwd`
"|sudo tee /etc/systemd/system/appension.service >/dev/null
echo "Service file created. To start:"
echo sudo systemctl start appension.service
