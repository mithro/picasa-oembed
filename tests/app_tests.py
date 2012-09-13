#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
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

"""Test module for apps.py,

You can run the test by running:
    $ python -m unittest --verbose tests
"""

__author__ = 'bayuadji@gmail.com'

import os
import json

from mock import MagicMock, patch
try:
    import unittest2 as unittest
except ImportError:
    import unittest


import searches


class TestSearches(unittest.TestCase):
    def test_albumname_only_extract(self):
        g = searches.ALBUMNAME_ONLY_EXTRACT.search(
            "http(s)://picasaweb.google.com/123/name")
        self.assertEqual(('123', 'name'), g.groups())

    def test_albumid_only_extract(self):
        g = searches.ALBUMID_ONLY_EXTRACT.search(
            "https://plus.google.com/photos/123/albums/456")
        self.assertEqual(('123', '456'), g.groups())

    def test_albumname_photo_extract(self):
        g = searches.ALBUMNAME_PHOTO_EXTRACT.search(
            "http(s)://picasaweb.google.com/123/name#789")
        self.assertEqual(('123', 'name', '789'), g.groups())

    def test_albumid_photo_extract(self):
        g = searches.ALBUMID_PHOTO_EXTRACT.search(
            "http(s)://picasaweb.google.com/.*/123/albumid/456/photoid/789")
        self.assertEquals(('123', '456', '789'), g.groups())

    def test_album_photo_extract(self):
        g = searches.ALBUMID_PHOTO_EXTRACT.search(
            "https://plus.google.com/photos/123/albums/456/789")
        self.assertEquals(('123', '456', '789'), g.groups())


class TestApps(unittest.TestCase):
    def setUp(self):
        modules = {
            'cachepy': MagicMock(),
            'google': MagicMock(),
            'google.appengine': MagicMock(),
            'google.appengine.api': MagicMock(),
            }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        self.maxDiff = None

    def tearDown(self):
        self.module_patcher.stop()

    def mock_data(self, albumid_value, file_sample_data):
        import app

        app.albumname2id = MagicMock()
        app.albumname2id.return_value = albumid_value
        app.urllib2 = MagicMock()
        urlopen_mock = MagicMock()
        app.urllib2.urlopen = urlopen_mock
        open_mock = MagicMock()
        urlopen_mock.return_value = open_mock

        open_mock.read.return_value = self.load_data(
            file_sample_data,
            'text')

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

    def test_oembed_single_picasa_photo(self):
        from app import oembed_single, albumname2id

        self.mock_data('5064748777194404225',
                       'single_picasa_photo.json')
        url_ = """https://picasaweb.google.com/111415681122206252267/Sasha02#5064749129381722546"""
        input_ = {}
        input_['userid'], input_['albumname'], input_['photoid'] = \
            searches.ALBUMNAME_PHOTO_EXTRACT.search(url_).groups()

        input_['albumid'] = albumname2id(input_)
        input_['maxwidth'] = 640
        input_['maxheight'] = 480

        self.assertEqual(oembed_single(input_),
                         self.load_data('result_single_picasa_photo.json'))

    def test_oembed_single_picasa_video(self):
        from app import oembed_single, albumname2id

        self.mock_data('5064748777194404144',
                       'single_picasa_video.json')

        url_ = """https://picasaweb.google.com/111415681122206252267/August31201202#5782876989650158754"""
        input_ = {}
        input_['userid'], input_['albumname'], input_['photoid'] = \
            searches.ALBUMNAME_PHOTO_EXTRACT.search(url_).groups()

        input_['albumid'] = albumname2id(input_)
        input_['maxwidth'] = 640
        input_['maxheight'] = 480
        self.assertEqual(oembed_single(input_),
                         self.load_data('result_single_picasa_video.json'))

    def test_oembed_single_gplus_video(self):
        from app import oembed_single
        url_ = """https://plus.google.com/photos/100642868990821651444/albums/5720909216955340593/5720909218315234178"""

        self.mock_data('5720909216955340593',
                       'single_gplus_video.json')

        input_ = {}
        input_['userid'], input_['albumid'], input_['photoid'] = \
            searches.ALBUMID_PHOTO_EXTRACT.search(url_).groups()

        input_['maxwidth'] = 640
        input_['maxheight'] = 480

        self.assertEqual(oembed_single(input_),
                         self.load_data('result_gplus_video.json'))

    def test_oembed_single_gplus_photo(self):
        from app import oembed_single

        url_ = """https://plus.google.com/photos/115212051037621986145/albums/5416758372025392817/5416759231776841970"""

        self.mock_data('5416758372025392817',
                        'single_gplus_photo.json')

        input_ = {}
        input_['userid'], input_['albumid'], input_['photoid'] = \
            searches.ALBUMID_PHOTO_EXTRACT.search(url_).groups()

        input_['maxwidth'] = 640
        input_['maxheight'] = 480

        self.assertEqual(oembed_single(input_),
                         self.load_data('result_gplus_photo.json'))

    def test_oembed_album_gplus(self):
        from app import oembed_album
        url_ = """https://plus.google.com/photos/115212051037621986145/albums/5416758372025392817"""

        self.mock_data('5064748777194404169',
                        'album_gplus.json')
        input_ = {}
        input_['userid'], input_['albumid'] = \
            searches.ALBUMID_ONLY_EXTRACT.search(url_).groups()

        input_['maxwidth'] = 640
        input_['maxheight'] = 480
        self.assertEqual(oembed_album(input_),
                         self.load_data('result_album_gplus.json'))

    def test_oembed_album_picasa(self):
        from app import oembed_album, albumname2id

        self.mock_data('5064748777194404169',
                       'album_picasa.json')

        url_ = "https://picasaweb.google.com/111415681122206252267/Sasha02"
        input_ = {}
        input_['userid'], input_['albumname'] = \
            searches.ALBUMNAME_ONLY_EXTRACT.search(url_).groups()

        input_['albumid'] = albumname2id(input_)
        input_['maxwidth'] = 640
        input_['maxheight'] = 480

        self.assertEqual(oembed_album(input_),
                         self.load_data('result_album_picasa.json'))


if __name__ == '__main__':
    unittest.main()
