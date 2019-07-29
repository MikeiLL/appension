echo "[Unit]
Description=Infinite Glitch
Requires=glitch.socket

[Install]
WantedBy=multi-user.target

[Service]
User=`whoami`
ExecStart=`which gunicorn` glitch.server:app
WorkingDirectory=`pwd`
"|sudo tee /etc/systemd/system/glitch.service >/dev/null
echo "[Socket]
ListenStream=80
"|sudo tee /etc/systemd/system/glitch.socket >/dev/null
echo "[Unit]
Description=Infinite Glitch Renderer
Requires=glitch-renderer.socket

[Install]
WantedBy=multi-user.target

[Service]
User=`whoami`
ExecStart=`which python` -m glitch renderer
WorkingDirectory=`pwd`
"|sudo tee /etc/systemd/system/glitch-renderer.service >/dev/null
echo "[Socket]
ListenStream=0.0.0.0:81
"|sudo tee /etc/systemd/system/glitch-renderer.socket >/dev/null
sudo systemctl daemon-reload
echo "Service file created. To start:"
echo sudo systemctl start glitch glitch-renderer


