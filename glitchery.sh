#/bin/bash
echo "Starting InfiniteGlitch."
until python -m fore.server 2>&1 | tee error.log; do
echo "Server 'python -m fore.server 2>&1 | tee error.log' crashed with exit code $?. Respawning.." >&2
sleep 1
mail -s "server crashed and restarted" mike@madhappy.com < error.log
done

