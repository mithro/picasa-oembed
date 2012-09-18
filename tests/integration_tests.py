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

import os
import oembed
import json

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

DEBUG = True

LIVE = 'http://picasaweb-oembed.appspot.com/oembed'
LOCAL = 'http://localhost:8080/oembed'

URLS = ['http://picasaweb.google.com/*',
        'https://picasaweb.google.com/*',
        'http://plus.google.com/photos/*',
        'https://plus.google.com/photos/*']


URL_RESULTS = [
	('https://plus.google.com/photos/100642868990821651444/albums/5720909216955340593/5720909219460239298',
         'result_integration_plus_photo.json'),
	('https://plus.google.com/photos/111415681122206252267/albums/5782876990269415361',
         'result_integration_plus_album.json'),
	('https://picasaweb.google.com/111415681122206252267/August31201202#5782876989650158754',
         'result_integration_picasa_photo.json'),
	('https://picasaweb.google.com/111415681122206252267/August31201202',
         'result_integration_picasa_album.json')
]


class LiveIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.consumer = oembed.OEmbedConsumer()
        self.endpoint = oembed.OEmbedEndpoint(LIVE, URLS)
        self.consumer.addEndpoint(self.endpoint)

    def load_data(self, filename, type_data='json'):
        """
        Load file data.
        """
        file_ = open(os.path.join(
            os.path.dirname(__file__),
            "test_documents", filename))

        content = file_.read()
        file_.close()

        if type_data == 'json':
            return json.loads(content)

        return content

    def test_url(self):
        try:
            for url in URL_RESULTS:
                response = self.consumer.embed(url[0])
                data = response.getData()
                self.assertEqual(data,
                                 self.load_data(url[1]))
        except IOError, e:
            print e
            self.fail("%s - %s" % (url, str(e)))


class LocalIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.consumer = oembed.OEmbedConsumer()
        self.endpoint = oembed.OEmbedEndpoint(LOCAL, URLS)
        self.consumer.addEndpoint(self.endpoint)

    def load_data(self, filename, type_data='json'):
        """
        Load file data.
        """
        file_ = open(os.path.join(
            os.path.dirname(__file__),
            "test_documents", filename))

        content = file_.read()
        file_.close()

        if type_data == 'json':
            return json.loads(content)

        return content

    def test_url(self):
        try:
            for url in URL_RESULTS:
                response = self.consumer.embed(url[0])
                data = response.getData()
                self.assertEqual(data,
                                 self.load_data(url[1]))
        except IOError, e:
            print e
            self.fail("%s - %s" % (url, str(e)))
