echo "[Unit]
Description=Infinite Glitch

[Service]
ExecStart=`which python` -m glitch
WorkingDirectory=`pwd`
"|sudo tee /etc/systemd/system/glitch.service >/dev/null
echo "[Unit]
Description=Infinite Glitch Renderer

[Service]
ExecStart=`which python` -m glitch renderer
WorkingDirectory=`pwd`
"|sudo tee /etc/systemd/system/glitch-renderer.service >/dev/null
echo "Service file created. To start:"
echo sudo systemctl start glitch glitch-renderer
