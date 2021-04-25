import re

from lxml import etree

from avdc.model.metadata import Metadata
from avdc.provider import NotFound
from avdc.utility.httpclient import get_html


def getTitle(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result = html.xpath('/html/head/title/text()')[0]
    return result


def getActresses(text: str) -> list[str]:
    _ = text
    return []  # fc2 no actresses


def getStudio(text: str) -> str:  # 获取厂商
    html = etree.fromstring(text, etree.HTMLParser())
    return str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()')).strip(" ['']")


def getVID(text: str) -> str:  # 获取番号
    html = etree.fromstring(text, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result


def getRelease(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/div[2]/p/text()')).strip(
        " ['Sale Day : 販売日 : ']").replace('/', '-')
    return result


def getCover(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[1]/span/img/@src')).strip(" ['']")
    return 'http:' + result


def getGenres(number: str) -> list[str]:
    text = str(bytes(get_html('http://adult.contents.fc2.com/api/v4/article/' + number + '/tag?'), 'utf-8').decode(
        'unicode-escape'))
    result = re.findall('"tag":"(.*?)"', text)
    return result


def getImages(text: str) -> list[str]:  # 获取剧照
    hr = re.compile(r'<ul class=\"items_article_SampleImagesArea\"[\s\S]*?</ul>')
    html = hr.search(text)
    if html:
        html = html.group()
        hf = re.compile(r'<a href=\"(.*?)\"')
        return hf.findall(html)
    return []


def main(keyword: str) -> Metadata:
    keyword = keyword.upper().replace('FC2-', '').replace('FC2PPV-', '')

    url = f'https://adult.contents.fc2.com/article/{keyword}/'
    text = get_html(url)

    if 'The product you were looking for was not found.' in text \
            or 'ご指定のファイルが見つかりませんでした' in text:
        raise NotFound(f'fc2: {keyword} not found')

    return Metadata(**{
        'title': getTitle(text),
        'studio': getStudio(text),
        'overview': '',  # getOverview(text),
        'runtime': 0,
        'director': getStudio(text),
        'actresses': getActresses(text),
        'release': getRelease(text),
        'vid': 'FC2-' + keyword,
        'label': '',
        'cover': getCover(text),
        'images': getImages(text),
        'genres': getGenres(keyword),
        'source': url,
        'provider': 'fc2',
        'series': '',
    })


if __name__ == '__main__':
    # print(main('FC2-1603395'))
    print(main('FC2PPV-1734831'))