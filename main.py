# imports
import os
import time
import traceback
import urllib.request
from bs4 import BeautifulSoup
import datetime
import codecs
import sys

try:
    from urllib.parse import urlparse, urljoin
except ImportError:
    try:
        from urlparse import urlparse
    except Exception as e_import:
        print(e_import)

# variables
to_download = []
success_download = 0
global url_global


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


def filterLink(soup, url):
    url = str(url)

    new_soup = BeautifulSoup('<link rel="stylesheet" href="%s" type="text/css">' % '../style/ateneo2014.css',
                             features="html.parser")
    soup.head.insert(0, new_soup)
    new_soup2 = BeautifulSoup('<link rel="stylesheet" href="%s" type="text/css">' % '../style/desktop.css',
                              features="html.parser")
    soup.head.insert(0, new_soup2)
    new_soup3 = BeautifulSoup('<link rel="stylesheet" href="%s" type="text/css">' % '../style/graduatorie.css',
                              features="html.parser")
    soup.head.insert(0, new_soup3)
    new_soup4 = BeautifulSoup("<meta charset='UTF-8'>",
                              features="html.parser")
    soup.head.insert(0, new_soup4)

    if url.endswith("_generale.html"):
        soup.select_one(".titolo").decompose()
        soup.select_one(".BoxInfoCard").decompose()
        new_soup5 = BeautifulSoup("<a href='./../'>Go to homepage</a>",
                                  features="html.parser")
        soup.select_one(".TablePage").insert(0, new_soup5)

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


def getCorso(soup):
    if soup is None:
        return None

    item = soup.select(".intestazione")[2]
    return item

    pass


def getFase(soup):
    if soup is None:
        return None

    item = soup.select(".intestazione")[3]
    return item
    pass


def downloadAndAddChildrenUrl1(i, start, i_url):
    global url_global
    global success_download

    elem = to_download[i]
    url = elem["url"]
    try:
        soup = BeautifulSoup(urllib.request.urlopen(url), features="html.parser")
        soup = filterLink(soup, url)
        to_download[i]["content"] = soup
        if i == 0:
            url_global[i_url]["corso"] = getCorso(soup)
            url_global[i_url]["fase"] = getFase(soup)

        if soup is not None:
            success_download += 1
            for link in soup.find_all('a', href=True):
                link = urljoin(url, link["href"])
                if link.startswith(start):
                    addLink(link)
                else:
                    print("Link not valid! " + link + "\n")

    except Exception as e:
        print("Failed to download [" + url + "]")
    pass


def directoryOutput(url, base_output, start_len, return_first_folder):
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

        if return_first_folder:
            return path, url3[0]

        if os.path.isdir(path):
            pass
        else:
            os.makedirs(path)

        j = j + 1

    return path + "/" + url3[len(url3) - 1], url3[0]


def downloadAndAddChildrenUrl(url, start, base_output, i_url, only_first):
    elem = {"url": url}
    to_download.append(elem)

    i = 0
    if not only_first:
        while i < len(to_download):
            downloadAndAddChildrenUrl1(i, start, i_url)
            i = i + 1
    else:
        downloadAndAddChildrenUrl1(i, start, i_url)

    start_len = len(start)
    i = 0
    while i < len(to_download):
        url2 = str(to_download[i]["url"])
        path, path_first = directoryOutput(url2, base_output, start_len, return_first_folder=False)
        file_to_write = None
        try:
            file_to_write = to_download[i]["content"]
        except:
            pass

        if file_to_write is not None:
            if path is not None:
                with open(path, "w", encoding='utf-8') as file:
                    file.write(str(file_to_write))

        i = i + 1

        pass


def executeDownload(url, i, start, base_output, only_first):
    global to_download
    global success_download

    time.sleep(1)

    to_download = []
    success_download = 0
    try:
        downloadAndAddChildrenUrl(url[i]["url"], start, base_output, i, only_first)
        if success_download > 0:
            print("Done [" + url[i]["url"] + "]")
            return 1
        else:
            print("Error [" + url[i]["url"] + "]")
            return 0
    except Exception as e:
        print(traceback.format_exc())
        print("Error [" + url[i]["url"] + "] => " + str(e))
        return 0

    return 0


def generateUrl(start):
    global url_global

    url_global = []
    now = datetime.datetime.now()
    year = int(now.year)
    kl = [8, 40, 41, 42, 64, 91, 102, 103]
    kl = range(0,201) #todo: remove later

    i = 2018
    while i <= year:

        j = 0  # j = 0 => html, j = 1 => htm
        while j < 2:

            js = ""
            if j == 0:
                js = "html"
            else:
                js = "htm"

            k = 0
            while k < len(kl):
                ks = (str(kl[k])).zfill(3)
                ks2 = str(i) + "_" + "20" + str(ks) + "_"
                single = start + "/" + ks2 + js + "/" + ks2 + "generale.html"

                elem = {"url": single, "year": i}
                url_global.append(elem)

                k = k + 1

            j = j + 1

        i += 1

    pass


def write_html(html, base_output):
    path = base_output + "/index.html"
    with open(path, "w", encoding='utf-8') as file:
        file.write(str(html))
    pass


def write_index(index_links, base_output):
    #     elem = {"url": url[i]["url"], "index": folder, "folder": folder_first, "year": url[i]["year"]}
    index_links.sort(key=lambda x: x["year"], reverse=True)

    a = 0
    a = a + 1

    html = "<html>\n"
    html += "<head>\n"
    html += "<meta charset='UTF-8'>\n"
    html += "<style> li { padding:0.5rem; } </style>\n"
    html += "</head>\n"
    html += "<body style='padding:1rem;'>\n"
    html += "<h1>\n"
    html += "Graduatorie\n"
    html += "</h1>\n"
    html += "<div>\n"
    html += "<ul>\n"
    for item in index_links:
        html += "<li>\n"
        link = "." + item["path"]
        html += "<a href='" + link + "'>\n"
        html += str(item["year"]) + " - " + str(item["corso"]) + " " + str(item["fase"]) + "\n"
        html += "</a>\n"
        html += "</li>\n"
        pass
    html += "</ul>\n"
    html += "</div>\n"
    html += "<h4>\n"
    html += "Sito by "
    html += "<a href='./../'>"
    html += "PoliNetwork"
    html += "</a>\n"
    html += "</h4>\n"
    html += "</body>\n</html>\n"

    write_html(html, base_output)

    pass


# main
if __name__ == '__main__':

    global url_global

    start = "http://www.risultati-ammissione.polimi.it"
    base_output = ""
    if sys.argv is None or len(sys.argv) < 2 or sys.argv[1] is None:
        base_output = "D:\\git\\Polimi\\polinetwork.github.io\\graduatorie"
    else:
        base_output = sys.argv[1]
    start_len = len(start)

    generateUrl(start)

    index_links = []

    i = 0
    while i < len(url_global):

        success = -1
        folder, folder_first = directoryOutput(url_global[i]["url"], base_output, start_len, return_first_folder=True)
        if os.path.isdir(folder):
            files = os.listdir(folder)
            if files is None or len(files) == 0:
                success = executeDownload(url_global, i, start, base_output, only_first=False)
            else:
                print("Already done [" + url_global[i]["url"] + "]")
                executeDownload(url_global, i, start, base_output, only_first=True)
                success = 2
        else:
            success = executeDownload(url_global, i, start, base_output, only_first=False)

        if success == 1 or success == 2:
            path = url_global[i]["url"][start_len:]
            elem = {"url": url_global[i]["url"], "index": folder, "folder": folder_first, "year": url_global[i]["year"],
                    "path": path, "corso": url_global[i]["corso"], "fase": url_global[i]["fase"]}
            index_links.append(elem)
            pass

        i = i + 1

    print("Download done [all]!")

    write_index(index_links, base_output)

    exit(0)
