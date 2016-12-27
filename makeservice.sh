echo "[Unit]
Description=Infinite Glitch
Requires=glitch.socket

[Service]
User=`whoami`
ExecStart=`which python` -m glitch
WorkingDirectory=`pwd`
"|sudo tee /etc/systemd/system/glitch.service >/dev/null
echo "[Socket]
ListenStream=80
"|sudo tee /etc/systemd/system/glitch.socket >/dev/null
echo "[Unit]
Description=Infinite Glitch Renderer

[Service]
User=`whoami`
ExecStart=`which python` -m glitch renderer
WorkingDirectory=`pwd`
"|sudo tee /etc/systemd/system/glitch-renderer.service >/dev/null
sudo systemctl daemon-reload
echo "Service file created. To start:"
echo sudo systemctl start glitch glitch-renderer
