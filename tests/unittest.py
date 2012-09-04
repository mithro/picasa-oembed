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

"""Test the AppEngine app which provides oEmbed endpoint for Picasa."""

__author__ = "mithro@mithis.com (Tim 'mithro' Ansell)"


import sys
sys.path.append("..")

import os
os.environ['SERVER_SOFTWARE'] = 'Devel'

import searches

g = searches.ALBUMNAME_ONLY_EXTRACT.search(
  "http(s)://picasaweb.google.com/123/name")
assert g is not None, str(g)
assert g.groups() == ('123','name'), g.groups()

g = searches.ALBUMID_ONLY_EXTRACT.search(
  "https://plus.google.com/photos/123/albums/456")
assert g is not None, str(g)
assert g.groups() == ('123','456'), g.groups()

g = searches.ALBUMNAME_PHOTO_EXTRACT.search(
  "http(s)://picasaweb.google.com/123/name#789")
assert g is not None, str(g)
assert g.groups() == ('123','name','789'), g.groups()

g = searches.ALBUMID_PHOTO_EXTRACT.search(
  "http(s)://picasaweb.google.com/.*/123/albumid/456/photoid/789")
assert g is not None, str(g)
assert g.groups() == ('123','456','789'), g.groups()

g = searches.ALBUMID_PHOTO_EXTRACT.search(
  "https://plus.google.com/photos/123/albums/456/789")
assert g is not None, str(g)
assert g.groups() == ('123','456','789'), g.groups()

