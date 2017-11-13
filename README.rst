**Note that this project has evolved into a more complete project with multiple slaves and custom apps. You should check it out**
`https://github.com/friends-of-freeswitch/switchio
<https://github.com/friends-of-freeswitch/switchio>`_.

FreeSWITCH ESL Call Load Tester
--------------------------------

Simple ESL-based FreeSWITCH Call Load Tester

This script allows you to use a FreeSWITCH instance to load-test other equipment (including other FreeSWITCH servers)

You can specify some basic options similar to sipp (call rate, limit, max calls, duration)

When done fs_test will give you a small report of number of calls placed, failures etc

::

 # ./fs_test -h
 usage: fs_test [options]

 options:
   -h, --help            show this help message and exit
   -a AUTH, --auth=AUTH  ESL password
   -s SERVER, --server=SERVER FreeSWITCH server IP address
   -p PORT, --port=PORT  FreeSWITCH server event socket port
   -r RATE, --rate=RATE  Rate in sessions to run per second
   -l LIMIT, --limit=LIMIT Limit max number of concurrent sessions
   -d DURATION, --duration=DURATION Max duration in seconds of sessions before being hung up
   -m MAX_SESSIONS, --max-sessions=MAX_SESSIONS Max number of sessions to originate before stopping
   -o ORIGINATE_STRING, --originate-string=ORIGINATE_STRING FreeSWITCH originate string
   --debug Enable debugging
