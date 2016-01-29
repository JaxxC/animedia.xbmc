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
parser = AnimediaParser(plugin, loader)

urls = {
    'new': 'http://online.animedia.tv/new',
    'all': 'http://online.animedia.tv/list',
    'top': 'http://online.animedia.tv',
    'full': 'http://online.animedia.tv/completed'
}


@plugin.route('/')
def main_screen():
    items = [
        {'label': u"Новые серии", 'path': plugin.url_for('catalogue', url=urls['new'], type='new')},
        {'label': u"Каталог аниме", 'path': plugin.url_for('catalogue', url=urls['all'], type='all')},
        {'label': u"ТОП", 'path': plugin.url_for('catalogue', url=urls['top'], type='top')},
        {'label': u"Завершенные Аниме", 'path': plugin.url_for('catalogue', url=urls['full'], type='full')},
        {'label': u"Аниме по жанрам", 'path': plugin.url_for('genres')}
    ]
    return items

@plugin.route('/catalogue/<url>/<type>')
def catalogue(url, type):
    page = loader.load_page(url)
    if type == 'new':
        listVideos = parser.parseNewDir(page)
        return composePlay(listVideos)
    elif type == 'top':
        listVideos = parser.parseTopDir(page)
    else:
        listVideos = parser.parseFullDir(page)
    return compose(listVideos)

@plugin.route('/genres/')
def genres():
    listVideos = parser.parseGenresDir()
    return composeGenre(listVideos)

@plugin.route('/seasons/<url>/')
def seasons(url):
    page = loader.load_page(url)
    listSeasons = parser.parseSeasonsTab(page)
    return compose(listSeasons, 'videos')

@plugin.route('/videos/<url>')
def videos(url):
    page = loader.load_page(url)
    listVideos = parser.parseVideos(page)
    return composePlay(listVideos)

def composeGenre(list):
    items = []
    for item in list:
        path = plugin.url_for('catalogue', url =item['url'], type='full')
        items.append({'label': item['title'], 'path': path, 'thumbnail': item['image']})
    return items

def compose(list, type = 'seasons'):
    items = []
    for item in list:
        path = item['_url'] if item.has_key('_url') else plugin.url_for(type, url=item['url'])
        items.append({'label': item['title'], 'path': path, 'thumbnail': item['image']})
    return items

def composePlay(list):
    items = []
    for item in list:
        items.append({'label': item['title'], 'path': item['url'], 'thumbnail': item['image'], 'is_playable': True})
    return items


if __name__ == '__main__':
    plugin.run()
    plugin.set_content('movies')

