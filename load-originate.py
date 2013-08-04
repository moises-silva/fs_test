#!/usr/bin/env python
# vim: tabstop=4 softtabstop=4 shiftwidth=4 textwidth=80 smarttab expandtab
import sys
import os
import time
import threading
import ESL
import logging
from optparse import OptionParser

"""
TODO
- Implement -timeout (global timeout, we need to hupall all of our calls and exit)
- Implement -sleep to sleep x seconds at startup
- Implement fancy rate logic from sipp
- Implement sipp -trace-err option
- Implement sipp return codes (0 for success, 1 call failed, etc etc)
"""

class Session(object):
    def __init__(self, uuid):
        self.uuid = uuid

class SessionManager(object):
    def __init__(self):
        self.sessions = {}
        self.hangup_causes = {}
        self.rate = 1
        self.limit = 1
        self.max_sessions = 1
        self.total_originated_sessions = 0
        self.con = None
        self.timer = None
        self.originate_string = None
        self.terminate = False
        self.ev_handlers = {
            'CHANNEL_ORIGINATE': self.handle_originate,
            'CHANNEL_ANSWER': self.handle_answer,
            'CHANNEL_HANGUP': self.handle_hangup,
        }

    def originate_session(self):
        if self.total_originated_sessions >= self.max_sessions:
            print 'Done originating'
            return
        sesscnt = len(self.sessions)
        for i in range(0, self.rate):
            if sesscnt >= self.limit:
                break
            self.con.api('bgapi originate %s' % (self.originate_string))
            sesscnt = sesscnt + 1

        # Schedule the timer again
        # In theory we should measure the time it took us to execute this # function and then wait (1 - elapsed)
        self.timer = threading.Timer(1, SessionManager.originate_session, [self])
        self.timer.start()

    def process_event(self, e):
        evname = e.getHeader('Event-Name')
        if evname in self.ev_handlers:
            try:
                self.ev_handlers[evname](e)
                # When a new session is created that belongs to us, we can 
                # call sched_hangup to hangup the session at x interval
            except Exception, ex:
                print 'Failed to process event %s: %s' % (e, ex)
        else:
                print 'Unknown event %s' % (e)

    def handle_originate(self, e):
        uuid = e.getHeader('Channel-Call-UUID')
        dir = e.getHeader('Call-Direction')
        if dir != 'outbound':
            # Ignore non-outbound calls (allows looping calls back on the DUT)
            print 'Originated session %s direction is %s' % (uuid, dir)
            return
        print 'Originated session %s' % uuid
        if uuid in self.sessions:
            print 'WTF?'
            return
        self.sessions[uuid] = Session(uuid)
        self.total_originated_sessions = self.total_originated_sessions + 1
        self.con.api('sched_hangup +%d %s NORMAL_CLEARING' % (self.duration, uuid))

    def handle_answer(self, e):
        uuid = e.getHeader('Channel-Call-UUID')
        if uuid not in self.sessions:
            return
        print 'Answered session %s' % uuid

    def handle_hangup(self, e):
        uuid = e.getHeader('Channel-Call-UUID')
        if uuid not in self.sessions:
            return
        cause = e.getHeader('Hangup-Cause')
        if cause not in self.hangup_causes:
            self.hangup_causes[cause] = 1
        else:
            self.hangup_causes[cause] = self.hangup_causes[cause] + 1
        del self.sessions[uuid]
        print 'Hung up session %s' % uuid
        if (self.total_originated_sessions >= self.max_sessions \
            and len(self.sessions) == 0):
            self.terminate = True

def main(argv):

    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    logger = logging.getLogger(os.path.basename(sys.argv[0]))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    sm = SessionManager()

    # Try to emulate sipp options (-r, -l, -d, -m)
    parser = OptionParser()
    parser.add_option("-a", "--auth", dest="auth", default="ClueCon",
                    help="ESL password")
    parser.add_option("-s", "--server", dest="server", default="127.0.0.1",
                    help="FreeSWITCH server IP address")
    parser.add_option("-p", "--port", dest="port", default="8021",
                    help="FreeSWITCH server event socket port")
    parser.add_option("-r", "--rate", dest="rate", default=1,
                    help="Rate in sessions to run per second")
    parser.add_option("-l", "--limit", dest="limit", default=1,
                    help="Limit max number of concurrent sessions")
    parser.add_option("-d", "--duration", dest="duration", default=60,
                    help="Max duration in seconds of sessions before being hung up")
    parser.add_option("-m", "--max-sessions", dest="max_sessions", default=1,
                    help="Max number of sessions to originate before stopping")
    parser.add_option("-o", "--originate-string", dest="originate_string",
                    help="FreeSWITCH originate string")

    (options, args) = parser.parse_args()

    if not options.originate_string:
        print '-o is mandatory'
        sys.exit(1)

    sm.rate = int(options.rate)
    sm.limit = int(options.limit)
    sm.duration = int(options.duration)
    sm.max_sessions = int(options.max_sessions)
    sm.originate_string = options.originate_string
    sm.con = ESL.ESLconnection(options.server, options.port, options.auth)
    if not sm.con.connected():
        print 'Failed to connect!'
        sys.exit(1)

    # Raise the sps and max_sessions limit to make sure they do not obstruct our test
    sm.con.api('fsctl sps %d' % (sm.rate * 10))
    sm.con.api('fsctl max_sessions %d' % (sm.limit * 10))

    # Reduce logging level to avoid much output in console/logfile
    sm.con.api('fsctl loglevel warning')

    sm.con.events('plain', 'CHANNEL_ORIGINATE CHANNEL_ANSWER CHANNEL_HANGUP')
    sm.timer = threading.Timer(1, SessionManager.originate_session, [sm])
    sm.timer.start()
    try:
        while True:
            e = sm.con.recvEventTimed(100)
            if not e:
                continue
            sm.process_event(e)
            if sm.terminate:
                break
    except KeyboardInterrupt:
        sm.timer.cancel()

    print 'Total originated sessions: %d' % sm.total_originated_sessions
    for cause, count in sm.hangup_causes.iteritems():
        print '%s = %d' % (cause, count)
    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])

