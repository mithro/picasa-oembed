#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import cgi
import re
import logging
import simplejson
import urllib2

import cachepy
from google.appengine.api import memcache


DICT_COMMON = {
    "version": "1.0",
    "provider_name": "Picasa",
    "provider_url": "http://picasaweb.google.com/",
    }

BASIC_EXTRACT = re.compile('/([0-9]+)/.*?([0-9]+)/.*?([0-9]+)')
ALBUM_EXTRACT = re.compile('/([0-9]+)/([^#]+)#([0-9]+)')
PICASA_FEED_URL = 'https://picasaweb.google.com/data/feed/tiny/user/%(userid)s/albumid/%(albumid)s/photoid/%(photoid)s?authuser=0&alt=jsonm&urlredir=1&commentreason=1&fd=shapes&thumbsize=%(maxwidth)s&max-results=1'


def cache(key, func, expire=3600):
    skey = str(key)

    result = cachepy.get(skey)
    if result is not None:
        return result

    result = memcache.get(skey)
    if result is not None:
        cachepy.set(skey, result)
        return result

    result = func(key)

    cachepy.set(skey, result, expiry=expire)
    memcache.set(skey, result, time=expire)
    return result


def oembed_dict(l):
    url = PICASA_FEED_URL % l
    logging.info(url)
    picasa_data = urllib2.urlopen(url).read()
    logging.info(picasa_data)
    picasa_json = simplejson.loads(picasa_data)['feed']
    logging.info(picasa_json)

    r = dict(DICT_COMMON)
    r["author_name"] = picasa_json['author'][0]['name']
    r["author_url"] = picasa_json['author'][0]['uri']
    r["title"] = picasa_json['title']
    r["thumbnail_url"] = picasa_json['media']['thumbnail'][0]['url']
    r["thumbnail_width"] = picasa_json['media']['thumbnail'][0]['width']
    r["thumbnail_height"] = picasa_json['media']['thumbnail'][0]['height']

    if 'originalVideo' in picasa_json:
        r["type"] = "video"

        to_big = []
        for media in picasa_json['media']['content']:
            if media['height'] > l['maxheight'] or media['width'] > l['maxwidth']:
                to_big.append(media)

        picasa_json['media']['content'].remove(to_big)
        picasa_json['media']['content'].sort(
            cmp=lambda a, b: cmp((a['width'], a['height']), (b['width'], b['height'])))

        r["width"] = picasa_json['media']['content'][-1]['width']
        r["height"] = picasa_json['media']['content'][-1]['height']

        r['html'] = """
<iframe src="/static/embed.html#user/%(userid)s/albumid/%(albumid)s/photoid/%(photoid)s" style="width: 100%; height: 100%;" ></iframe>
"""
        # Only cache for 1 hour due to the expiring auth keys
        r["cache_age"] = 3600
    else:
        r["type"] = "photo"
        r["url"] = r['thumbnail_url']
        r["width"] = r['thumbnail_width']
        r["height"] = r['thumbnail_height']
        # Cache for 24 hours
        r["cache_age"] = 3600*24
    return r


def oembed(environ, start_response):

    d = cgi.parse_qs(environ['QUERY_STRING'])

    input = {}
    input['maxwidth'] = min(640, int(d.get('maxwidth', [2**32])[0]))
    input['maxheight'] = min(480, int(d.get('maxheight', [2**32])[0]))
    format = d.get('format', ['json'])[0]

    status = '200 OK'
    headers = []
    if format == 'json':
        headers.append(('Content-Type', 'text/json'))
    elif format == 'xml':
        headers.append(('Content-Type', 'text/xml'))

    userid, albumid, photoid = None, None, None
    r = ''

    m = BASIC_EXTRACT.search(d.get('url', [''])[0])
    if m:
        input['userid'], input['albumid'], input['photoid'] = m.groups()
    else:
        status = '404 Not Found'

    if input.get('userid', None) and input.get('albumid', None) and input.get('photoid', None):
        try:
            d = cache(input, oembed_dict)

            if format == 'json':
                r = simplejson.dumps(d)
            elif format == 'xml':
                r = '<xml></xml>'
            else:
                raise IOError('Unknown format')
        except (urllib2.URLError, IOError), e:
            status = '401 Unauthorized'

    headers.append(('Content-Length', str(len(r))))
    start_response(status, headers)
    return [r]
