#!/usr/local/bin/python

import tail
import shlex
from httplib2 import Http
from timeit import Timer
from datetime import datetime

# global variable for server name that will be taking the traffic                                                   
server_name = "http://api-staging.pbs.org"

def print_line(txt):
    ''' Prints received text '''
    loglist = shlex.split(txt)
    req = loglist[4]
    req2 = req.split('=',1)[1]
    req3 = req2.split()[1]
    # getting the log's "process time" in seconds
    origin_resp_time = float(loglist[3].split('=')[1])/1000000.
    origin_resp_status = loglist[5].split('=')[1]
    print req3

    before = datetime.now()
    (resp, content) = Http().request("%s%s" % (server_name, req3))
    after = datetime.now()
    rtime_seconds = (after - before).total_seconds()
    print 'origin: \t%s %s' % (origin_resp_status, origin_resp_time)
    print 'staging:\t%s %s\n' % (resp.status, rtime_seconds)


t = tail.Tail('/var/log/httpd/coveapi_access.log')
t.register_callback(print_line)
t.follow(s=1)


