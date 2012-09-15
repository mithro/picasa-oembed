#!/usr/bin/python2.4
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

"""Test the AppEngine app which provides oEmbed endpoint for Picasa.
   Requirement:
    - Run the local server (make serve) if you want to test the local server.
"""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"

import oembed

DEBUG = True

LIVE = 'http://picasaweb-oembed.appspot.com/oembed'
LOCAL = 'http://localhost:8080/oembed'

URLS = ['http://picasaweb.google.com/*',
        'https://picasaweb.google.com/*',
        'http://plus.google.com/photos/*',
        'https://plus.google.com/photos/*']

try:
    import unittest2 as unittest
except ImportError:
    import unittest


# * http(s)://picasaweb.google.com/{userid}/{albumname}
# Outputs "rich" element which contains the Picasa album.

# * http(s)://picasaweb.google.com/{userid}/{albumname}#{photoid}
# Outputs "photo" or "video" element which contains the Photo/Video.

# * http(s)://picasaweb.google.com/.*/{userid}/albumid/{albumid}/photoid/{photoid}
# Outputs "photo" or "video" element which contains the Photo/Video.

# * https://plus.google.com/photos/{userid}/albums/{albumid}/{userid}
# Outputs "photo" or "video" element which contains the Photo/Video.

# * https://plus.google.com/photos/{userid}/albums/{albumid}
# Outputs "rich" element which contains the Picasa album.


class LiveIntegrationTest(unittest.TestCase):
    def setUp(self):
        print "Testing against: %s" % LIVE
        self.consumer = oembed.OEmbedConsumer()
        self.endpoint = oembed.OEmbedEndpoint(LIVE, URLS)
        self.consumer.addEndpoint(self.endpoint)

    def test_url(self):
        try:
            response = self.consumer.embed(
                'https://plus.google.com/photos/100642868990821651444/albums/5720909216955340593/5720909219460239298')
            import pprint
            pprint.pprint(response.getData())

            response = self.consumer.embed(
                'https://plus.google.com/photos/111415681122206252267/albums/5782876990269415361')

            pprint.pprint(response.getData())
        except IOError, e:
            print e
            print e.geturl()


class LocalIntegrationTest(unittest.TestCase):
    def setUp(self):
        print "Testing against: %s" % LOCAL
        self.consumer = oembed.OEmbedConsumer()
        self.endpoint = oembed.OEmbedEndpoint(LOCAL, URLS)
        self.consumer.addEndpoint(self.endpoint)

    def test_url(self):
        try:
            response = self.consumer.embed(
                'https://plus.google.com/photos/100642868990821651444/albums/5720909216955340593/5720909219460239298')
            import pprint
            pprint.pprint(response.getData())

            response = self.consumer.embed(
                'https://plus.google.com/photos/111415681122206252267/albums/5782876990269415361')

            pprint.pprint(response.getData())
        except IOError, e:
            print e
            print e.geturl()
