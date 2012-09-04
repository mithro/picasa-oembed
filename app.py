#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:
#
# Copyright (C) 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""AppEngine app which provides oEmbed endpoint for Picasa."""

import cgi
import datetime
try:
    import json
except ImportError:
    import simplejson as json

import re
import logging
import urllib2

import cachepy
import structured
import searches

from google.appengine.api import memcache



__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"


DICT_COMMON = {
    "version": "1.0",
    "provider_name": "Picasa",
    "provider_url": "http://picasaweb.google.com/",
    }


ALBUM_NAME_URL = 'https://picasaweb.google.com/%(userid)s/%(albumname)s'

ALBUM_FEED_URL = 'https://picasaweb.google.com/data/feed/tiny/user/%(userid)s/albumid/%(albumid)s?authuser=0&alt=jsonm&urlredir=1&commentreason=1&fd=shapes&thumbsize=%(maxwidth)s'
PHOTO_FEED_URL = 'https://picasaweb.google.com/data/feed/tiny/user/%(userid)s/albumid/%(albumid)s/photoid/%(photoid)s?authuser=0&alt=jsonm&urlredir=1&commentreason=1&fd=shapes&thumbsize=%(maxwidth)s&max-results=1'

ALBUMID_EXTRACT = re.compile('albumid/([0-9]+)')

TIME_FMT = "%a, %d-%b-%Y %H:%M:%S GMT"

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


def albumname2id(l):
    url = ALBUM_NAME % l
    logging.debug('Album url %r', url)
    picasa_data = urllib2.urlopen(url).read()

    possible_album_ids = ALBUMID_EXTRACT.search(picasa_data)
    return possible_album_ids.groups()[0]


def oembed_single(l):
    url = PHOTO_FEED_URL % l
    logging.debug('Album url %r', url)
    picasa_data = urllib2.urlopen(url).read()
    picasa_json = json.loads(picasa_data)['feed']

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

        for x in to_big:
            picasa_json['media']['content'].remove(x)

        picasa_json['media']['content'].sort(
            cmp=lambda a, b: cmp((a['width'], a['height']), (b['width'], b['height'])))

        r["width"] = picasa_json['media']['content'][-1]['width']
        r["height"] = picasa_json['media']['content'][-1]['height']

        r['html'] = """
<iframe src="picasaweb-oembed.appspot.com/static/embed.html#user/%(userid)s/albumid/%(albumid)s/photoid/%(photoid)s" style="width: 100%%; height: 100%%;" ></iframe>
""" % l
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


def oembed_album(l):
    url = ALBUM_FEED_URL % l
    logging.debug('Album url %r', url)
    picasa_data = urllib2.urlopen(url).read()
    picasa_json = json.loads(picasa_data)['feed']

    r = dict(DICT_COMMON)
    r["type"] = 'rich'
    r["author_name"] = picasa_json['nickname']
    r["author_url"] = "https://plus.google.com/%s/posts" % l['userid']
    r["title"] = picasa_json['title']
    r["thumbnail_url"] = picasa_json['icon']
    r['html'] = """
<embed
    type="application/x-shockwave-flash"
    src="https://picasaweb.google.com/s/c/bin/slideshow.swf"
    width="288" height="192"
    flashvars="host=picasaweb.google.com&captions=1&hl=en_US&feat=flashalbum&RGB=0x000000&feed=https%%3A%%2F%%2Fpicasaweb.google.com%%2Fdata%%2Ffeed%%2Fapi%%2Fuser%%2F%(userid)s%%2Falbumid%%2F%(albumid)s%%3Falt%%3Drss%%26kind%%3Dphoto%%26hl%%3Den_US"
    pluginspage="http://www.macromedia.com/go/getflashplayer">
</embed>
""" % l
    r["width"] = l['maxwidth']
    r["height"] = l['maxheight']
    return r


def oembed(environ, start_response):
    now = datetime.datetime.utcnow()

    d = cgi.parse_qs(environ['QUERY_STRING'])

    input = {}
    input['maxwidth'] = min(640, int(d.get('maxwidth', [2**32])[0]))
    input['maxheight'] = min(480, int(d.get('maxheight', [2**32])[0]))
    format = d.get('format', ['json'])[0]

    status = '200 OK'
    headers = []
    if format == 'json':
        headers.append(('Content-Type', 'application/json'))
    elif format == 'xml':
        headers.append(('Content-Type', 'text/xml'))
    headers.append(('Date', now.strftime(TIME_FMT)))

    input['userid'], input['albumid'], input['albumname'], input['photoid'] = None, None, None, None
    r = ''

    url = d.get('url', [''])[0]
    logging.debug('url %r', url)
    albumid_photo = searches.ALBUMID_PHOTO_EXTRACT.search(url)
    logging.debug('extracted albumid_photo %r', albumid_photo)
    albumname_photo = searches.ALBUMNAME_PHOTO_EXTRACT.search(url)
    logging.debug('extracted albumname_photo %r', albumname_photo)
    albumid_only = searches.ALBUMID_ONLY_EXTRACT.search(url)
    logging.debug('extracted albumid_only %r', albumid_photo)
    albumname_only = searches.ALBUMNAME_ONLY_EXTRACT.search(url)
    logging.debug('extracted albumname_only %r', albumname_photo)

    if albumid_photo:
        input['userid'], input['albumid'], input['photoid'] = albumid_photo.groups()

    elif albumname_photo:
        input['userid'], input['albumname'], input['photoid'] = albumname_photo.groups()

    elif albumid_only:
        input['userid'], input['albumid'] = albumid_only.groups()

    elif albumname_only:
        input['userid'], input['albumname'] = albumname_only.groups()

    # Get albumid from albumname
    if input['albumname'] and not input['albumid']:
        logging.debug('Getting albumid from name: %r', input['albumname'])
        input['albumid'] = cache(input, albumname2id)

    logging.debug(input)

    d = {}
    d['cache_age'] = 3600
    if input.get('userid', None) and input.get('albumid', None) and input.get('photoid', None):
        logging.debug('Found a single photo.')
        try:
            d.update(cache(input, oembed_single))
        except (urllib2.URLError, IOError), e:
            status = '401 Unauthorized'
            d = {}
    elif input.get('userid', None) and input.get('albumid', None):
        logging.debug('Found a whole album.')
        try:
            d.update(cache(input, oembed_album))
        except (urllib2.URLError, IOError), e:
            status = '401 Unauthorized'
            d = {}
    else:
        status = '404 Not Found'
        d = {}

    if format == 'json':
        r = json.dumps(d)
    elif format == 'xml':
        r = structured.dict2xml(d, roottag='oembed')
    else:
        raise IOError('Unknown format')

    headers.append(('Cache-Control', 'public, max-age=%i, must-revalidate' % d['cache_age']))
    headers.append(('Last-Modified', now.strftime(TIME_FMT)))
    headers.append(('Expires', (now+datetime.timedelta(seconds=d['cache_age'])).strftime(TIME_FMT)))
    headers.append(('Content-Length', str(len(r))))
    start_response(status, headers)
    return [r]
