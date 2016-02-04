#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import urllib2, gzip
import socket
import cookielib
from StringIO import StringIO


class WebLoader():
    def __init__(self,cookie_dir):
        self.cookie_file = os.path.join(cookie_dir, '.cookies')
        self.cookie_jar = cookielib.LWPCookieJar(self.cookie_file)
        if not os.path.exists(self.cookie_file):
            self.cookie_jar.save()
        self.cookie_jar.revert()
        self.opener = Opener(handler=urllib2.HTTPCookieProcessor(self.cookie_jar))

    def load_page(self, url, data=None):
        self.cookie_jar.load()
        web_page = self.opener.get_page(url, data)
        self.cookie_jar.save()
        return web_page


class Opener(object):
    headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0'),
        ('Accept-Charset', 'UTF-8'),
        ('Accept', 'text/html'),
        ('Connection', 'keep-alive')]

    def __init__(self, handler=urllib2.BaseHandler(), host='http://online.animedia.tv'):
        self.opener = urllib2.build_opener(handler)
        self.headers.append(('Host', host))
        self.headers.append(('Accept-encoding', 'gzip'))
        self.opener.addheaders = self.headers

    def open(self, url, data=None):
        return self.opener.open(url, data)

    def get_page(self, url, data=None):
        try:
            session = self.opener.open(url, data)
        except (urllib2.URLError, socket.timeout) as ex:
            web_page = ''
        else:
            gzip_page = session.read()
            session.close()
            g = gzip.GzipFile(fileobj=StringIO(gzip_page))
            web_page = g.read()

        return web_page