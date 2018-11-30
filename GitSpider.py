from urllib.parse import urlparse

import requests
import scrapy


def has_directory(url, directory='.git'):
    full_url = '%s/%s/' % (url, directory)

    r = requests.get('%s' % full_url)

    valid_codes = [
        200
    ]

    return r.status_code in valid_codes, full_url


def get_ext(path):
    if not '.' in path:
        return None

    path = path.split('.')

    return path[len(path) - 1]


class GitSpider(scrapy.Spider):
    name = 'gitspider'

    excluded_extensions = [
        'png',
        'jpg',
        'jpeg',
        'bmp',
        'zip',
        'rar',
        'exe',
        'pdf',
        'txt',
        'doc',
        'docx'
    ]

    allowed_schemes = [
        'http',
        'https'
    ]

    def __init__(self, **kwargs):
        super().__init__(self.name, **kwargs)

        starting_url = self.url

        if not starting_url.startswith('http://') and not starting_url.startswith('https://'):
            starting_url = 'https://' + starting_url

        print('Starting url: %s' % starting_url)

        self.start_urls = ['%s' % starting_url]

    def parse(self, response):

        print('Response URL: %s' % (response.url))

        resp_urlp = urlparse(response.url)

        hd, git_path = has_directory('%s://%s' % (resp_urlp.scheme, resp_urlp.netloc))

        if hd:
            print('Has .git directory: %s' % git_path)

        for url in response.xpath('//a/@href').extract():
            urlp = urlparse(url)

            if len(urlp.scheme) == 0 or len(urlp.netloc) == 0:
                continue

            url = '%s://%s' % (urlp.scheme, urlp.netloc)

            if resp_urlp.netloc is urlp.netloc:
                continue

            if urlp.scheme not in self.allowed_schemes:
                continue

            #if len(urlp.path) != 0 and get_ext(urlp.path) in self.excluded_extensions:
            #    continue

            yield scrapy.Request(url, callback=self.parse)
