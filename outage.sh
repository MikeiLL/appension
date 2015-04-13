#!/bin/bash
# Run with Sudo
NOTIFYEMAIL=mike@mzoo.org
SMSEMAIL=2016794168@pm.sprint.com
SENDEREMAIL=mikekilmer@infiniteglitch.net
SERVER=http://infiniteglitch.net/
PAUSE=60
FAILED=0
DEBUG=0

while true 
do
/usr/bin/curl -sSf $SERVER > /dev/null 2>&1
CS=$?
# For debugging purposes
if [ $DEBUG -eq 1 ]
then
    echo "STATUS = $CS"
    echo "FAILED = $FAILED"
    if [ $CS -ne 0 ]
    then
        echo "$SERVER is down"

    elif [ $CS -eq 0 ]
    then
        echo "$SERVER is up"
    fi
fi

# If the server is down and no alert is sent - alert
if [ $CS -ne 0 ] && [ $FAILED -eq 0 ]
then
    FAILED=1
    PID=`ps -eaf | grep 'python -m fore.server' | grep -v grep | awk '{print $2}'`
    if [ $DEBUG -eq 1 ]
    then
    	if [[ "" !=  "$PID" ]]
        then
        	echo "$SERVER failed. Killing Process..."
        	kill -9 $PID
        	echo "Starting the server..."
        	python -m fore.server
        else
        	echo "No Such Process Running Locally."
        fi
    fi
    if [ $DEBUG = 0 ]
    then
        echo "$SERVER went down $(date)" | /usr/bin/mail -s "$SERVER went down" "$SENDEREMAIL" "$SMSEMAIL" " < error.log" 
        echo "$SERVER went down $(date)" | /usr/bin/mail -s "$SERVER went down" "$SENDEREMAIL" "$NOTIFYEMAIL" " < error.log"
        if [[ "" !=  "$PID" ]]
        then
        	kill -9 $PID
        	python -m fore.server
        fi
    fi

# If the server is back up and no alert is sent - alert
elif [ $CS -eq 0 ] && [ $FAILED -eq 1 ]
then
    FAILED=0
    if [ $DEBUG -eq 1 ]
    then
        echo "$SERVER is back up"
    fi
    if [ $DEBUG = 0 ]
    then
        echo "$SERVER is back up $(date)" | /usr/bin/mail -s "$SERVER is back up again" "$SENDEREMAIL" "$SMSEMAIL" " < error.log"
        echo "$SERVER is back up $(date)" | /usr/bin/mail -s "$SERVER is back up again" "$SENDEREMAIL" "$NOTIFYEMAIL" " < error.log"
    fi
fi
sleep $PAUSE
done
