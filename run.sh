#!/bin/sh

# ./fs_test -h
#usage: fs_test [options]
#
#options:
#  -h, --help            show this help message and exit
#  -a AUTH, --auth=AUTH  ESL password
#  -s SERVER, --server=SERVER
#                        FreeSWITCH server IP address
#  -p PORT, --port=PORT  FreeSWITCH server event socket port
#  -r RATE, --rate=RATE  Rate in sessions to run per second
#  -l LIMIT, --limit=LIMIT
#                        Limit max number of concurrent sessions
#  -d DURATION, --duration=DURATION
#                        Max duration in seconds of sessions before being hung
#                        up
#  -m MAX_SESSIONS, --max-sessions=MAX_SESSIONS
#                        Max number of sessions to originate before stopping
#  -o ORIGINATE_STRING, --originate-string=ORIGINATE_STRING
#                        FreeSWITCH originate string
#  --debug               Enable debugging
#

to_ip=10.10.2.64
to_did=9199
orig_did=9199
from_did=1234
duration=60
limit=1
rate=1
max=1
debug=
verify=

while [ $1 ]
do
	echo "arg=$1"
	if [ $1 = "-to_ip" ];then
		shift
		if [ -z $1 ]; then
			echo "Error in to_ip arg"
			exit 1
		fi
		to_ip=$1
	elif [ $1 = "-to_did" ];then
		shift
		if [ -z $1 ]; then
			echo "Error in to_did arg"
			exit 1
		fi
		to_did=$1
	elif [ $1 = "-orig_did" ];then
		shift
		if [ -z $1 ]; then
			echo "Error in orig_did arg"
			exit 1
		fi
		orig_did=$1
	elif [ $1 = "-d" ];then
		shift
		if [ -z $1 ]; then
			echo "Error in -d arg"
			exit 1
		fi
		duration=$1
	elif [ $1 = "-l" ];then
		shift
		if [ -z $1 ]; then
			echo "Error in -l arg"
			exit 1
		fi
		limit=$1
	elif [ $1 = "-r" ];then
		shift
		if [ -z $1 ]; then
			echo "Error in -r arg"
			exit 1
		fi
		rate=$1
	elif [ $1 = "-m" ];then
		shift
		if [ -z $1 ]; then
			echo "Error in -m arg"
			exit 1
		fi
		max=$1
	elif [ $1 = "-debug" ];then
		debug="--debug"
	elif [ $1 = "-t" ];then
		verify="true"
	fi
	shift
done

cmd="./fs_test -d $duration -l $limit -r $rate -m $max $debug -o \"{absolute_codec_string=PCMU,origination_caller_id_name='Sangoma Technologies',origination_caller_id_number=$from_did}sofia/internal/$to_did@$to_ip $orig_did XML default\""
echo $cmd

if [ "$verify" = "true" ]; then
	exit 0
fi

eval $cmd
 



