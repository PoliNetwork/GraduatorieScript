# imports
import os
import traceback
import urllib.request
from bs4 import BeautifulSoup

try:
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urlparse import urlparse

# variables
to_download = []
success_download = 0


# methods
def addLink(link):
    j = 0
    while j < len(to_download):
        url2 = to_download[j]["url"]
        if url2 == link:
            return
        j = j + 1

    elem = {"url": link}
    to_download.append(elem)


def filterLink(soup, i, url):
    url = str(url)

    new_soup = BeautifulSoup('<link rel="stylesheet" href="%s" type="text/css">' % '../style/ateneo2014.css.jsp',
                             features="html.parser")
    soup.head.insert(0, new_soup)
    new_soup2 = BeautifulSoup('<link rel="stylesheet" href="%s" type="text/css">' % '../style/desktop.css.jsp',
                              features="html.parser")
    soup.head.insert(0, new_soup2)
    new_soup3 = BeautifulSoup('<link rel="stylesheet" href="%s" type="text/css">' % '../style/graduatorie.css',
                              features="html.parser")
    soup.head.insert(0, new_soup3)

    if url.endswith("_generale.html"):
        soup.select_one(".titolo").decompose()
        soup.select_one(".BoxInfoCard").decompose()

        pass
    elif "_indice.html" in url and "sotto_indice.html" not in url:
        return None
    elif "_sotto_" in url and "sotto_indice.html" not in url:
        # da rimuovere la colonna matricola
        tab = soup.find("table", {"class": "TableDati"})
        soup.select(".HeadColumn1")[1].decompose()
        rows = tab.select_one(".TableDati-tbody")
        for row in rows:
            row.select(".Dati1")[1].decompose()

        return soup

    elif "_grad_" in url and "_M.html" in url:
        # da rimuovere la colonna matricola (prima colonna)
        tab = soup.find("table", {"class": "TableDati"})
        soup.select_one(".HeadColumn1").decompose()
        rows = tab.select_one(".TableDati-tbody")
        for row in rows:
            row.select_one(".Dati1").decompose()

        return soup

    return soup
    pass


def downloadAndAddChildrenUrl1(i, start):
    elem = to_download[i]
    url = elem["url"]
    try:
        soup = BeautifulSoup(urllib.request.urlopen(url), features="html.parser")
        soup = filterLink(soup, i, url)
        to_download[i]["content"] = soup
        if soup is not None:
            success_download = success_download + 1
            for link in soup.find_all('a', href=True):
                link = urljoin(url, link["href"])
                if link.startswith(start):
                    addLink(link)
                else:
                    print("Link not valid! " + link + "\n")

    except Exception as e:
        print("Failed to download [" + url + "]")
    pass


def directoryOutput(i, base_output, start_len):
    url = str(to_download[i]["url"])

    url2 = url[start_len:]
    url3 = url2.split("/")

    if len(url3) == 0:
        return None

    if url3[0] is None or len(url3[0]) == 0:
        url3.pop(0)

    if len(url3) == 0:
        return None

    path = base_output
    j = 0
    while j < (len(url3) - 1):
        path = path + "/" + url3[j]
        if os.path.isdir(path):
            pass
        else:
            os.makedirs(path)

        j = j + 1

    return path + "/" + url3[len(url3) - 1]


def downloadAndAddChildrenUrl(url, start):
    elem = {"url": url}
    to_download.append(elem)

    i = 0
    while i < len(to_download):
        downloadAndAddChildrenUrl1(i, start)
        i = i + 1

    base_output = "D:\\git\\Polimi\\polinetwork.github.io\\graduatorie"

    start_len = len(start)
    i = 0
    while i < len(to_download):
        path = directoryOutput(i, base_output, start_len)
        file_to_write = None
        try:
            file_to_write = to_download[i]["content"]
        except:
            pass

        if file_to_write is not None:
            if path is not None:
                with open(path, "w") as file:
                    file.write(str(file_to_write))

        i = i + 1

        pass


# main
if __name__ == '__main__':
    start = "http://www.risultati-ammissione.polimi.it"

    url = [
        "http://www.risultati-ammissione.polimi.it/2020_20040_html/2020_20040_generale.html",
        "http://www.risultati-ammissione.polimi.it/2020_20041_html/2020_20041_generale.html",
        "http://www.risultati-ammissione.polimi.it/2020_20042_html/2020_20042_generale.html",
        "http://www.risultati-ammissione.polimi.it/2020_20008_html/2020_20008_generale.html",
        "http://www.risultati-ammissione.polimi.it/2020_20064_html/2020_20064_generale.html",
        "http://www.risultati-ammissione.polimi.it/2020_20102_html/2020_20102_generale.html",
        "http://www.risultati-ammissione.polimi.it/2020_20103_html/2020_20103_generale.html",
        "http://www.risultati-ammissione.polimi.it/2020_20091_html/2020_20091_generale.html",
        "http://www.risultati-ammissione.polimi.it/2019_20064_html/2019_20064_sotto_indice.html",
        "http://www.risultati-ammissione.polimi.it/2019_20102_html/2019_20102_sotto_indice.html",
        "http://www.risultati-ammissione.polimi.it/2019_20103_html/2019_20103_sotto_indice.html",
        "http://www.risultati-ammissione.polimi.it/2019_20091_html/2019_20091_sotto_indice.html",
        "http://www.risultati-ammissione.polimi.it/2019_20008_html/2019_20008_generale.html",
        "http://www.risultati-ammissione.polimi.it/2021_20040_htm/2021_20040_sotto_indice.html",
        "http://www.risultati-ammissione.polimi.it/2020_20041_html/2020_20041_generale.html",
        "http://www.risultati-ammissione.polimi.it/2020_20042_html/2020_20042_generale.html",
        "http://www.risultati-ammissione.polimi.it/2021_20064_html/2021_20064_generale.html",
        "http://www.risultati-ammissione.polimi.it/2021_20102_html/2021_20102_generale.html",
        "http://www.risultati-ammissione.polimi.it/2021_20103_html/2021_20103_generale.html",
        "http://www.risultati-ammissione.polimi.it/2021_20091_html/2021_20091_generale.html"
    ]

    i = 0
    while i < len(url):
        to_download = []
        success_download = 0
        try:
            downloadAndAddChildrenUrl(url[i], start)
            if success_download > 0:
                print("Done [" + url[i] + "]")
            else:
                print("Error [" + url[i] + "]")
        except Exception as e:
            print(traceback.format_exc())
            print("Error [" + url[i] + "] => " + str(e))

        i = i + 1

    print("Done [all]!")
