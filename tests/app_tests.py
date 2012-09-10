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

if __name__ == '__main__':
    unittest.main()
