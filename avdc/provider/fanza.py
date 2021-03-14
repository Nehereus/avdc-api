import re
from urllib.parse import urlencode

from lxml import etree
from requests import HTTPError

from avdc.utility.httpclient import get_html
from avdc.utility.metadata import toMetadata


def getTitle(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result = html.xpath('//*[starts-with(@id, "title")]/text()')[0]
    return result


def getStars(text: str) -> str:
    # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(text, etree.HTMLParser())
    result = (
        str(
            html.xpath(
                "//td[contains(text(),'出演者')]/following-sibling::td/span/a/text()"
            )
        ).strip(" ['']").replace("', '", ",")
    )
    return result


def getStudio(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'メーカー')]/following-sibling::td/a/text()"
        )[0]
    except:
        result = html.xpath(
            "//td[contains(text(),'メーカー')]/following-sibling::td/text()"
        )[0]
    return result


def getRuntime(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath("//td[contains(text(),'収録時間')]/following-sibling::td/text()")[0]
    return re.search(r"\d+", str(result)).group()


def getLabel(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'レーベル：')]/following-sibling::td/a/text()"
        )[0]
    except:
        result = html.xpath(
            "//td[contains(text(),'レーベル：')]/following-sibling::td/text()"
        )[0]
    return result


def getID(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'品番：')]/following-sibling::td/a/text()"
        )[0]
    except:
        result = html.xpath(
            "//td[contains(text(),'品番：')]/following-sibling::td/text()"
        )[0]
    return result


def getRelease(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'発売日：')]/following-sibling::td/a/text()"
        )[0].lstrip("\n")
    except:
        try:
            result = html.xpath(
                "//td[contains(text(),'発売日：')]/following-sibling::td/text()"
            )[0].lstrip("\n")
        except:
            result = "----"
    if result == "----":
        try:
            result = html.xpath(
                "//td[contains(text(),'配信開始日：')]/following-sibling::td/a/text()"
            )[0].lstrip("\n")
        except:
            try:
                result = html.xpath(
                    "//td[contains(text(),'配信開始日：')]/following-sibling::td/text()"
                )[0].lstrip("\n")
            except:
                pass
    return result.replace("/", "-")


def getTags(text: str) -> list[str]:
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath("//td[contains(text(),'ジャンル：')]/following-sibling::td/a/text()")
    except:
        result = html.xpath("//td[contains(text(),'ジャンル：')]/following-sibling::td/text()")
    return result


def getCover(text: str, number: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    cover_number = number
    try:
        result = html.xpath('//*[@id="' + cover_number + '"]/@href')[0]
    except:
        # sometimes fanza modify _ to \u0005f for image id
        if "_" in cover_number:
            cover_number = cover_number.replace("_", r"\u005f")
        try:
            result = html.xpath('//*[@id="' + cover_number + '"]/@href')[0]
        except:
            # (TODO) handle more edge case
            # print(html)
            # raise exception here, same behavior as before
            # people's major requirement is fetching the picture
            raise ValueError("can not find image")
    return result


def getDirector(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'監督：')]/following-sibling::td/a/text()"
        )[0]
    except:
        result = html.xpath(
            "//td[contains(text(),'監督：')]/following-sibling::td/text()"
        )[0]
    return result


def getOverview(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    try:
        result = str(html.xpath("//div[@class='mg-b20 lh4']/text()")[0]).replace(
            "\n", ""
        )
        if result == "":
            result = str(html.xpath("//div[@class='mg-b20 lh4']//p/text()")[0]).replace(
                "\n", ""
            )
    except:
        # (TODO) handle more edge case
        # print(html)
        return ""
    return result


def getSeries(text: str) -> str:
    try:
        html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        try:
            result = html.xpath(
                "//td[contains(text(),'シリーズ：')]/following-sibling::td/a/text()"
            )[0]
        except:
            result = html.xpath(
                "//td[contains(text(),'シリーズ：')]/following-sibling::td/text()"
            )[0]
        return result
    except:
        return ""


def getImages(content: str) -> list[str]:  # 获取剧照
    hr = re.compile(r'<div id=\"sample-image-block\"[\s\S]*?<br></div></div>')
    html = hr.search(content)
    if html:
        html = html.group()
        hf = re.compile(r'<img.*?src=\"(.*?)\"')
        images = hf.findall(html)
        if images:
            s = []
            for img_url in images:
                img_urls = img_url.rsplit('-', 1)
                img_url = img_urls[0] + 'jp-' + img_urls[1]
                s.append(img_url)
            return s
    return []


@toMetadata
def main(number: str) -> dict:
    # fanza allow letter + number + underscore, normalize the input here
    # @note: I only find the usage of underscore as h_test123456789
    fanza_search_number = number
    # AV_Data_Capture.py.getIDber() over format the input, restore the h_ prefix
    if fanza_search_number.startswith("h-"):
        fanza_search_number = fanza_search_number.replace("h-", "h_")

    fanza_search_number = re.sub(r"[^0-9a-zA-Z_]", "", fanza_search_number).lower()

    fanza_urls = [
        "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=",
        "https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=",
        "https://www.dmm.co.jp/digital/anime/-/detail/=/cid=",
        "https://www.dmm.co.jp/mono/anime/-/detail/=/cid=",
        "https://www.dmm.co.jp/digital/videoc/-/detail/=/cid=",
        "https://www.dmm.co.jp/digital/nikkatsu/-/detail/=/cid=",
        "https://www.dmm.co.jp/rental/-/detail/=/cid=",
    ]
    chosen_url = ""

    content = None
    for url in fanza_urls:
        chosen_url = url + fanza_search_number
        try:
            content = get_html(
                "https://www.dmm.co.jp/age_check/=/declared=yes/?{}".format(
                    urlencode({"rurl": chosen_url})
                )
            )
        except HTTPError:
            continue
        else:
            break

    if content is None:
        return {}

    # for some old page, the input number does not match the page
    # for example, the url will be cid=test012
    # but the hinban on the page is test00012
    # so get the hinban first, and then pass it to following functions
    fanza_hinban = getID(content)
    metadata = {
        "title": getTitle(content).strip(),
        "studio": getStudio(content),
        "overview": getOverview(content),
        "runtime": getRuntime(content),
        "director": getDirector(content) if "anime" not in chosen_url else "",
        "stars": getStars(content) if "anime" not in chosen_url else "",
        "release": getRelease(content),
        "id": fanza_hinban,
        "cover": getCover(content, fanza_hinban),
        "tags": getTags(content),
        "images": getImages(content),
        "label": getLabel(content),
        # "star_photos": "",
        "website": chosen_url,
        "source": "fanza",
        "series": getSeries(content),
    }
    print(metadata)
    return metadata


if __name__ == "__main__":
    # print(main("DV-1562"))
    # print(main("96fad1217"))
    # print(main("pred00251"))
    print(main("118ABP115"))