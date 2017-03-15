#!/bin/bash

set -x

get_default_message(){
    message="Command $task finished with status $exit_status"
}

OPTIND=1 #reset the counter just in case

VIRTUAL_ENV="~/.virtualenvs/fcm_sender/bin/python"
SENDER_PATH="~/vamk/sep/fcm_notifications_sender/fcm_sender"

topic="global"
USAGE="Usage: $0 [-t <topic>] [-m <message>] <command-to-execute> [<command-arg1> ...]"

if [ "$#" -lt 1 ]; then
    echo $USAGE
    exit 1
fi
while getopts ":t:m:" opt; do

    case $opt in
        t)
            topic=$OPTARG
            ;;
        m)
            message=$OPTARG
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            echo $USAGE
            exit 1
            ;;
        :)
            echo "Option: -$OPTARG needs an argument"
            exit 1
            ;;
    esac
done

task=${@:$OPTIND}

if [ -z "$task" ]; then
    echo "No command found."
    echo $USAGE
    exit 1
fi

eval $task
exit_status=$?

if [ -z "$message" ]; then
    get_default_message
fi

echo "Topic: $topic";
echo "Message: $message"
echo "Command: $task"

eval "$VIRTUAL_ENV $SENDER_PATH -t $topic \"$message\""
