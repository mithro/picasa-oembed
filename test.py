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

import oembed

DEBUG = True

LIVE = 'http://picasaweb-oembed.appspot.com/'
LOCAL = 'http://localhost:8080/'

URLS = ['http://picasaweb.google.com/*',
        'https://picasaweb.google.com/*',
        'http://plus.google.com/photos/*',
        'https://plus.google.com/photos/*']

consumer = oembed.OEmbedConsumer()
endpoint = oembed.OEmbedEndpoint([LIVE, LOCAL][DEBUG], URLS)
consumer.addEndpoint(endpoint)

response = consumer.embed('https://plus.google.com/photos/100642868990821651444/albums/5720909216955340593/5720909219460239298')

import pprint
pprint.pprint(response.getData())
print response['url']

