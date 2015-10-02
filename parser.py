#!/usr/bin/env python2.6

import tail
import shlex
from httplib2 import Http
from datetime import datetime

# global variable for server that will be taking the traffic
DITTO_TARGET = 'http://127.0.0.1/'
# used to comminucate to target which hostname to use
DITTO_TARGET_HOSTNAME = "example.com"

def get_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6

def process_log_line(txt):
    '''
        This function takes a log line from apache log lines, extracts the
        path and repeats the request to a different server
    '''

    #--------------------------------------------------
    # Parse the log line.  Right now this is hard coded to parse loglines
    # that COVE API app servers dump.   This is the config format:
    # LogFormat "%h %t process_time=%D request=\"%r\" response=%>s bytes=%b
    #   referrer=\"%{Referer}i\" user_agent=\"%{User-Agent}i\"
    #   appsvrname=\"%{X-PBS-appsvrname}o\" appsvrip=\"%{X-PBS-appsvrip}o\"
    #   host=%V xff=\"%{X-Forwarded-For}i\" session_id=%{www.apache.sid}C
    #   api_key=%{X-PBSAuth-Consumer-Key}i" combined
    #
    # Example:
    # 10.170.78.52 [30/May/2013:03:17:35 -0400] process_time=83694 request="GET /cove/v1/videos/?consumer_key=videoportal-prod-4323a5ab-82ea-43f5-b1d5-9ba36b2a95f2&fields=captions%2Cmediafiles%2Cassociated_images&filter_tp_media_object_id=2242344271&nonce=071a656a-55bb-4f78-a402-836779a2f38f&timestamp=1369898256&signature=e559c9dae3ab1146c78dffccdd4be61a9c5fbdb8 HTTP/1.1" response=200 bytes=6100 referrer="-" user_agent="Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11" appsvrname="coveapi-prod-app-2e #37" appsvrip="10.30.159.172" host=api.pbs.org xff="184.73.41.108, 10.31.197.112, 23.21.35.16" session_id=- api_key=-
    #
    loglist = shlex.split(txt)
    req = loglist[4]
    req2 = req.split('=', 1)[1]
    req3 = req2.split()[1]
    # getting the log's "process time" in seconds
    origin_resp_time = float(loglist[3].split('=')[1])/1000000.
    origin_resp_status = loglist[5].split('=')[1]
    #print req3

    #--------------------------------------------------
    # Now repeat the request to the ditto server
    #
    before = datetime.now()
    target_url = "%(server)s%(path)s" % {'server':DITTO_TARGET, 'path':req3 }
    add_headers = {'Host': DITTO_TARGET_HOSTNAME}
    # Debug turned on
    # import httplib2
    #httplib2.debuglevel=4
    (resp, content) = Http().request(target_url, headers=add_headers)
    print 'got response: %s'
    after = datetime.now()
    rtime_seconds = get_total_seconds(after - before)
    print 'origin: \t%s %s' % (origin_resp_status, origin_resp_time)
    print 'staging:\t%s %s\n' % (resp.status, rtime_seconds)


t = tail.Tail('/path/to/access.log')
t.register_callback(process_log_line)
t.follow(s=1)

