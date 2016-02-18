#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup

URL_NEW = 'http://online.animedia.tv/new'
URL_ALL = 'http://online.animedia.tv/list'
URL_TOP = 'http://online.animedia.tv'
URL_COMPLETED = 'http://online.animedia.tv/completed'
URL_GENRE = 'http://online.animedia.tv/category/'


class AnimediaParser():
    def __init__(self, plugin, loader):
        self.plugin = plugin
        self.loader = loader
        self.genres = {
            'martial-arts': u"Боевые искусства",
            'vampires': u"Вампиры",
            'war': u"Война",
            'detective': u"Детектив",
            'dzesey': u"ДзёСэй",
            'dorams': u"Дорамы",
            'drama': u"Драма",
            'historical': u"Исторический",
            'history': u"История",
            'cyberpunk': u"Киберпанк",
            'comedy': u"Комедия",
            'crime': u"Криминал",
            'live': u"Лайв-экшн",
            'magicalgirl': u"Махо-сёдзё",
            'medicine': u"Медицина",
            'mecha': u"Меха",
            'mistery': u"Мистика",
            'music': u"Музыка",
            'parody': u"Пародия",
            'slice-of-Life': u"Повседневность",
            'postapokaliptika': u"Постапокалиптика",
            'advanture': u"Приключения",
            'psychology': u"Психология",
            'romance': u"Романтика",
            'samurai-action': u"Самурайский боевик",
            'shoujo': u"Сёдзе",
            'sedze-ai': u"Сёдзё-Ай",
            'shounen': u"Сёнэн",
            'shounen-ai': u"Сёнэн-Ай",
            'sport': u"Спорт",
            'seinen': u"Сэйнэн",
            'thriller': u"Триллер",
            'horror': u"Ужасы",
            'fantastika': u"Фантастика",
            'fantasy': u"Фэнтези",
            'school': u"Школа",
            'ecchi': u"Этти"
        }
        self.paths = plugin.get_storage('paths')

    def parseGenresDir(self):
        listGenres = []
        for listItem in self.genres:
            listGenres.append({
                'image': '',
                'title': self.genres[listItem],
                'url': URL_GENRE + listItem,
            })

        return listGenres

    def parseNewDir(self, page):
        beautifulSoup = BeautifulSoup(page, "html.parser")
        listVideos = []
        listA = beautifulSoup.findAll('div', attrs={'class': 'new-series'})

        for listItem in listA:
            img = listItem.find('img')
            a = listItem.find('a', attrs={'class': 'h4 widget__new-series__item__title'})
            sn = listItem.find('div', attrs={'class': 'new-series_info'}).find(text=True, recursive=False)
            anime = a['href'].split('/')[2]
            path = self.getVideoPath(a['href'], anime)
            hash = re.findall('http://online.animedia.tv/screens/(.*)_med', img['src'])[0]
            if a:
                listVideos.append({
                    'title': '[' + sn.replace(u' Серия', '').strip() + ']' + a.text,
                    'url': self.getNoHLS(path, hash),
                    'image': img['src']
                })
        return listVideos

    def parseTopDir(self, page):
        beautifulSoup = BeautifulSoup(page, "html.parser")
        listVideos = []
        listA = beautifulSoup.findAll('div', attrs={'class': 'widget__most-popular__item widget__item'})
        for listItem in listA:
            a = listItem.find('a', attrs={'class': 'h4 widget__most-popular__item__title'})
            if a:
                listVideos.append({
                    'title': '[' + listItem.find('div', attrs={
                        'class': 'widget__most-popular__item__rating'}).text + ']' + a.text,
                    'url': a.get('href').encode('utf-8', 'replace'),
                    'image': ''
                })

        return listVideos

    def parseFullDir(self, page):
        beautifulSoup = BeautifulSoup(page, "html.parser")
        listVideos = []
        listA = beautifulSoup.find('div', attrs={'class': 'ads-list'}).findAll('div', attrs={'class': 'ads-list__item'})

        for listItem in listA:
            img = listItem.find('img')
            a = listItem.find('a', attrs={'class': 'h3 ads-list__item__title'})
            if a:
                listVideos.append({
                    'title': a.text + '/' + listItem.find('div', attrs={'class': 'original-title'}).text,
                    'url': a['href'],
                    'image': self.getImgThumb(img['src'])
                })

        return self.nextPageDir(listVideos, beautifulSoup)

    def nextPageDir(self, listVideos, bsPage):
        pagination = bsPage.find('div', attrs={'class': 'pagination'})
        if (pagination):
            nextPage = pagination.find('li', attrs={'class': 'pagination__list__item active'}).find_next_sibling()
            if (nextPage):
                nextPage = nextPage.find('a')
                listVideos.append({
                    'title': u'Следующая страница',
                    '_url': self.plugin.url_for('catalogue', url=nextPage['href'], type='all'),
                    'image': ''
                })
        return listVideos

    def parseSeasonsTab(self, page):
        beautifulSoup = BeautifulSoup(page, "html.parser")
        listSeasons = []
        seasons = beautifulSoup.findAll('a', attrs={'role': 'tab'})
        image = beautifulSoup.find('div', attrs={'class': 'widget__post-info__poster'}).find('img')
        entry = beautifulSoup.find('ul', attrs={'class': 'media__tabs__nav nav-tabs'})
        entry_id = entry['data-entry_id']
        for season in seasons:
            listSeasons.append({
                'title': season.text,
                'url': 'http://online.animedia.tv/ajax/episodes/' + entry_id + '/' + str(
                    int(season['href'].replace('#tab', '')) + 1),
                'image': self.getImgThumb(image['src'])
            })

        return listSeasons

    def parseVideos(self, page):
        beautifulSoup = BeautifulSoup(page, "html.parser")
        name = re.findall('media__tabs__series__list__item"><a href="/anime/([^/]+)/', page)
        videos = beautifulSoup.findAll('div', attrs={'class': 'media__tabs__series__list__item'})
        first = videos[0].find('a');
        path = self.getVideoPath(first['href'], name[0])
        return self.getVideos(videos, path)

    def getVideos(self, videos, path):
        listVideos = []
        for video in videos:
            url = video.find('img')
            stream = url['data-layzr'].replace('http://online.animedia.tv/screens/', '').replace('_min.jpg', '')
            listVideos.append({
                'title': video.text,
                'url': self.getNoHLS(path, stream),
                'image': url['data-layzr']
            })
        return listVideos

    def getVideoPath(self, href, anime):
        if anime in self.paths:
            return self.paths[anime]
        else:
            videopage = self.loader.load_page(URL_TOP + href)
            split = re.findall('((http.*/(video)/.*/)smil:)', videopage)
            self.paths[anime] = split[0][1]

        return split[0][1]

    def getNoHLS(self, path, hash):
        return path + hash + '.mp4'

    def getHLS(self, path, hash):
        return path + 'smil:' + hash + '.smil/playlist.m3u8'

    def getImgThumb(self, image):
        imagename = re.findall('.*/(.*)\.jpg', image)
        return 'http://online.animedia.tv/images/made/images/uploads/'+imagename[0].replace('_280_385', '')+'_280_385.jpg'
