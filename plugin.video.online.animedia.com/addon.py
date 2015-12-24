#!/usr/bin/python
# -*- coding: utf-8 -*-

from xbmcswift2 import Plugin
from resources.lib.loader import WebLoader
from resources.lib.parser import AnimediaParser
import os


plugin = Plugin()
if __name__ == '__main__':
    _cookie_dir = os.path.dirname(__file__)
else:
    _cookie_dir = plugin.storage_path

loader = WebLoader(_cookie_dir)
parser = AnimediaParser()

urls = {
    'new': 'http://online.animedia.tv/new',
    'all': 'http://online.animedia.tv/list',
    'top': 'http://online.animedia.tv',
    'full': 'http://online.animedia.tv/completed'
}


@plugin.route('/')
def main_screen():
    items = [
        {'label': u"Новые серии", 'path': plugin.url_for('catalogue', type='new')},
        {'label': u"Каталог аниме", 'path': plugin.url_for('catalogue', type='all')},
        {'label': u"ТОП", 'path': plugin.url_for('catalogue', type='top')},
        {'label': u"Завершенные Аниме", 'path': plugin.url_for('catalogue', type='full')},
        {'label': u"Аниме по жанрам", 'path': plugin.url_for('genres')}
    ]
    return items

@plugin.route('/catalogue/<type>/')
def catalogue(type):
    page = loader.load_page(urls[type])
    if type == 'new':
        listVideos = parser.parseNewDir(page)
    elif type == 'top':
        listVideos = parser.parseTopDir(page)
    elif type == 'full' or type == 'all':
        listVideos = parser.parseFullDir(page)
    return compose(listVideos)

@plugin.route('/genres/')
def genres():
    listVideos = parser.parseGenresDir()
    return compose(listVideos)

@plugin.route('/seasons/<url>/')
def seasons(url):
    page = loader.load_page(url)
    listSeasons = parser.parseSeasonsTab(page)
    return compose(listSeasons, 'videos')

@plugin.route('/videos/<url>')
def videos(url):
    page = loader.load_page(url)
    listVideos = parser.parseVideos(page, loader)
    return composePlay(listVideos)

def compose(list, type = 'seasons'):
    items = []
    for item in list:
        items.append({'label': item['title'], 'path': plugin.url_for(type, url=item['url']), 'thumbnail': item['image']})
    return items

def composePlay(list):
    items = []
    for item in list:
        print item
        items.append({'label': item['title'], 'path': item['url'], 'thumbnail': item['image'], 'is_playable': True})
    return items


if __name__ == '__main__':
    plugin.run()
    plugin.set_content('movies')

