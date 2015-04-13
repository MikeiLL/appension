#!/bin/bash
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
    if [ $DEBUG -eq 1 ]
    then
        echo "$SERVER failed"
    fi
    if [ $DEBUG = 0 ]
    then
        echo "$SERVER went down $(date)" | /usr/bin/mail -s "$SERVER went down" "$SENDEREMAIL" "$SMSEMAIL" " < error.log" 
        echo "$SERVER went down $(date)" | /usr/bin/mail -s "$SERVER went down" "$SENDEREMAIL" "$NOTIFYEMAIL" " < error.log"
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
