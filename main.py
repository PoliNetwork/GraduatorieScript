# imports
import datetime
import os
import sys
import time
import traceback
import urllib.request
from string import ascii_lowercase
from bs4 import BeautifulSoup

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

list_already_done = []
list_error_download = []
list_download_completed = []


# methods
def addLink(link):
    j = 0
    while j < len(to_download):
        url2 = to_download[j]["url"]
        if url2 == link:
            return
        j += 1

    elem2 = {"url": link}
    to_download.append(elem2)


def filterLink(soup, url):
    try:
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
    except Exception as e8:
        print("Failed to download (08) [" + url + "], " + str(e8))

    try:
        if url.endswith("_generale.html"):
            try:
                soup.select_one(".titolo").decompose()
                soup.select_one(".BoxInfoCard").decompose()
                new_soup5 = BeautifulSoup(
                    "<div style=\"padding: 1.1rem;font-weight: bold;font-size: calc(1.2rem + 0.1vw);\">"
                    "<a href=\"./../\">"
                    "🔙 Go to back homepage to see all rankings"
                    "</a>"
                    "</div>",
                    features="html.parser")
                soup.select_one(".TablePage").insert(0, new_soup5)
            except Exception as e9:
                print("Failed to download (09) [" + url + "], " + str(e9))

            pass
        elif "_indice.html" in url and "sotto_indice.html" not in url:
            return None
        elif "_sotto_" in url and "sotto_indice.html" not in url:
            try:
                # da rimuovere la colonna matricola
                tab = soup.find("table", {"class": "TableDati"})
                soup.select(".HeadColumn1")[1].decompose()
                rows = tab.select_one(".TableDati-tbody")
                for row in rows:
                    row.select(".Dati1")[1].decompose()

                return soup
            except Exception as e10:
                print("Failed to download (10) [" + url + "], " + str(e10))


        elif "_grad_" in url and "_M.html" in url:
            try:
                # da rimuovere la colonna matricola (prima colonna)
                tab = soup.find("table", {"class": "TableDati"})
                soup.select_one(".HeadColumn1").decompose()
                rows = tab.select_one(".TableDati-tbody")
                for row in rows:
                    row.select_one(".Dati1").decompose()

                return soup

            except Exception as e11:
                print("Failed to download (11) [" + url + "], " + str(e11))

        return soup

    except Exception as e7:
        print("Failed to download (07) [" + url + "], " + str(e7))

    return None


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


def downloadAndAddChildrenUrl1(i2, start2, i_url):
    global url_global
    global success_download

    try:
        elem2 = to_download[i2]
        url = elem2["url"]
        soup = None
        try:
            soup = BeautifulSoup(urllib.request.urlopen(url), features="html.parser")
        except Exception as e2:
            print("Failed to download (02) [" + url + "], " + str(e2))

        if soup is None:
            return

        try:
            soup = filterLink(soup, url)
            to_download[i2]["content"] = soup
            if i2 == 0:
                url_global[i_url]["corso"] = getCorso(soup)
                url_global[i_url]["fase"] = getFase(soup)
        except Exception as e6:
            print("Failed to download (06) [" + url + "], " + str(e6))

        if soup is None:
            return

        try:
            success_download += 1
            for link in soup.find_all('a', href=True):
                try:
                    link = urljoin(url, link["href"])
                    if link.startswith(start2):
                        addLink(link)
                    else:
                        print("Link not valid! " + link + "\n")
                except Exception as e1:
                    print("Failed to download (01) [" + url + "], " + str(e1))
        except Exception as e3:
            print("Failed to download (03) [" + url + "], " + str(e3))
    except Exception as e4:
        print("Failed to download (04) [" + i2 + "], " + str(e4))

    pass


def directoryOutput(url, base_output2, start_len2, return_first_folder):
    url2 = url[start_len2:]
    url3 = url2.split("/")

    if len(url3) == 0:
        return None

    if url3[0] is None or len(url3[0]) == 0:
        url3.pop(0)

    if len(url3) == 0:
        return None

    path2 = base_output2
    j = 0
    while j < (len(url3) - 1):
        path2 = path2 + "/" + url3[j]

        if return_first_folder:
            return path2, url3[0]

        if os.path.isdir(path2):
            pass
        else:
            os.makedirs(path2)

        j += 1

    return path2 + "/" + url3[len(url3) - 1], url3[0]


def downloadAndAddChildrenUrl(url, start2, base_output2, i_url, only_first):
    elem2 = {"url": url}
    to_download.append(elem2)

    i2 = 0
    if not only_first:
        while i2 < len(to_download):
            downloadAndAddChildrenUrl1(i2, start2, i_url)
            i2 += 1
    else:
        downloadAndAddChildrenUrl1(i2, start2, i_url)

    start_len2 = len(start2)
    i2 = 0
    while i2 < len(to_download):
        url2 = str(to_download[i2]["url"])
        path2, path_first = directoryOutput(url2, base_output2, start_len2, return_first_folder=False)
        file_to_write = None
        try:
            file_to_write = to_download[i2]["content"]
        except:
            pass

        if file_to_write is not None:
            if path2 is not None:
                with open(path2, "w", encoding='utf-8') as file:
                    file.write(str(file_to_write))

        i2 += 1

        pass


def executeDownload(url, i2, start2, base_output2, only_first):
    global to_download
    global success_download

    time.sleep(1)

    url2 = url[i2]["url"]
    if url2 == "http://www.risultati-ammissione.polimi.it/2022_20103_355c_html/2022_20103_generale.html":
        a = 0
        a = a + 1

    to_download = []
    success_download = 0
    try:
        downloadAndAddChildrenUrl(url2, start2, base_output2, i2, only_first)
        if success_download > 0:
            if not only_first:
                list_download_completed.append(url2)
            print("Done [" + url2 + "]")
            return 1
        else:
            list_error_download.append(url2)
            print("Error [" + url2 + "]")
            return 0
    except Exception as e:
        print(traceback.format_exc())
        list_error_download.append(url2)
        print("Error [" + url2 + "] => " + str(e))
        return 0

    return 0


def getYearFromString(m):
    m = str(m)
    if m.__contains__("/"):
        m3 = m.split("/")
        for m4 in m3:
            try:
                m5 = m4[0:4]
                m6 = int(m5)
                return m6
            except:
                pass

    m2 = m[0:4]
    return int(m2)
    pass


def finished(words, limit):
    for i in range(0, limit):
        if words[i] != 35:
            return False

    return True


def getWord(words):
    result = ""
    for word in words:
        if word < 26:
            result += ascii_lowercase[word]
        else:
            number = word - 26
            result += str(number)

    return result


def nextWords(words):
    i = len(words) - 1
    increasedDone = False
    riporto = False
    while i >= 0:

        if riporto:
            words[i] += 1
            if words[i] < 36:
                return words

        if words[i] < 36 and riporto == False and increasedDone == False:
            words[i] += 1
            increasedDone = True

        if words[i] == 36:
            words[i] = 0
            riporto = True

        i -= 1

    return words


def getBruteforcedList(bruteforceEnabled):
    if not bruteforceEnabled:
        return [""]

    listResult = [""]
    words = []
    limit = 4
    for i in range(0, limit):
        words.append(0)

    while not finished(words, limit):
        word = getWord(words)
        listResult.append(word + "_")
        words = nextWords(words)

    return listResult


def getIfPresent(elem2):
    global url_global

    url = str(elem2["url"])
    for item in url_global:
        url2 = str(item["url"])

        if url == url2:
            return True

    return False


global crawl_links
crawl_links = []


def crawl(start2, url="", i=0, linkStart=None):
    global url_global
    global crawl_links

    if i > 2:
        return
    if not url:
        url = "https://www.polimi.it/in-evidenza"

    url = urljoin(linkStart, url)

    if crawl_links.__contains__(url):
        return

    if linkStart is not None:
        if not str(url).startswith(linkStart):
            return

    crawl_links.append(url)

    try:
        soup = BeautifulSoup(urllib.request.urlopen(url), features="html.parser")

        links = []
        for link in soup.findAll('a'):
            links.append(link.get('href'))

        for link in links:
            crawl(start2, link, i + 1, url)

            if str(link).startswith(start2):
                elem2 = {"url": link, "year": getYearFromString(link)}
                isPresent = getIfPresent(elem2)
                if not isPresent:
                    url_global.append(elem2)
    except:
        pass

    pass


def generateUrl(start2, bruteforceEnableLocal):
    global url_global

    url_global = []

    # CHECK COMMON LINKS
    now = datetime.datetime.now()
    year = int(now.year)
    kl = [2, 5, 6, 7, 8, 40, 41, 42, 45, 54, 60, 64, 69, 91, 102, 103, 104]
    # kl = range(500,1000) #todo: remove later

    bruteforce = getBruteforcedList(bruteforceEnableLocal)

    for b in bruteforce:
        for k in kl:
            ks = (str(k)).zfill(3)
            ks2 = str(year) + "_" + "20" + str(ks) + "_"
            single = start2 + "/" + ks2 + b + "html" + "/" + ks2 + "generale.html"

            elem2 = {"url": single, "year": year}
            url_global.append(elem2)

    # MANUAL URLS
    manual_urls = [
        "2022_20002_46h3_html/2022_20002_generale.html",
        "2022_20102_ab23_html/2022_20102_generale.html",
        "2022_20103_355c_html/2022_20103_generale.html"
    ]

    for m in manual_urls:
        single = start2 + "/" + m
        elem2 = {"url": single, "year": getYearFromString(m)}
        url_global.append(elem2)

    # CRAWL LINKS FROM POLIMI WEBSITE
    print("Number of URLs before crawl: " + str(len(url_global)))
    crawl(start2)
    print("Number of URLs after crawl: " + str(len(url_global)))

    # PRINT URL TO DOWNLOAD
    print("starting printing url to download")
    for url2 in url_global:
        print(url2)
    print("finishing printing url to download")

    pass


def write_html(html, base_output2):
    path2 = base_output2 + "/index.html"
    with open(path2, "w", encoding='utf-8') as file:
        file.write(str(html))
    pass


def alreadyPresent(item, list_index):
    pass
    link = item.attrs['href']
    link = str(link)[1:]
    for item2 in list_index:
        link2 = item2['url']
        if str(link2).endswith(link):
            return True

    return False


def write_index(index_links2, base_output2, index_previous_links):
    # sort
    index_links2.sort(key=lambda x: x["year"], reverse=True)

    i2 = 0
    j = 0
    while i2 < len(index_links2):

        while j < (len(index_links2) - 1):

            str1 = None
            str2 = None

            if "fase" in index_links2[j]:
                str1 = str(index_links2[j]["fase"]).lower()

            if "fase" in index_links2[j + 1]:
                str2 = str(index_links2[j + 1]["fase"]).lower()

            if str1 is None and str2 is None:
                pass
            elif str2 is None:
                pass
            elif str1 is None or str1 > str2:
                temp = index_links2[j]
                index_links2[j] = index_links2[j + 1]
                index_links2[j + 1] = temp
            else:
                pass

            j += 1

        i2 += 1

    index_links2.sort(key=lambda x: x["year"], reverse=True)

    # write
    html = "<html>\n"
    html += "<head>\n"
    html += "<meta charset='UTF-8'>\n"
    html += "<meta name='description' content='Graduatorie degli anni passati per le matricole del Politecnico di " \
            "Milano, archiviate by PoliNetwork Rankings'>\n "
    html += "<meta name='keywords' content='Graduatorie, Rankings, Polimi, Matricole, Politecnico, Milano, " \
            "PoliNetwork'>\n "
    html += "<style>" \
            " li { padding:0.5rem;border: 1px solid;margin: 1rem;border-radius: 1rem; } " \
            "ul{padding-left: 0.1rem;}" \
            " body{overflow: auto;padding:0.5rem;}" \
            " h1{overflow: auto;font-size: calc(1.25rem + 1.25vw);}" \
            "h4{overflow:auto;}" \
            "</style>\n"
    html += "</head>\n"
    html += "<body>\n"
    html += "<h1>\n"
    html += "Graduatorie/Rankings\n"
    html += "</h1>\n"
    html += "<div>\n"
    html += "<br /><p>Recent rankings:</p><br />\n"
    html += "<ul>\n"
    for item in index_links2:
        html += "<li>\n"
        link = "." + item["path"]
        html += "<a href='" + link + "'>\n"
        if "corso" in item:
            html += str(item["year"]) + " " + str(item["corso"]) + " " + str(item["fase"]) + "\n"
        else:
            html += str(item["year"]) + "\n"
        html += "</a>\n"
        html += "</li>\n"
        pass
    html += "</ul>\n"
    html += "<br /><p>Previous rankings:</p><br />\n"
    html += "<ul>\n"
    print("len(index_previous_links):")
    print(len(index_previous_links))
    for item in index_previous_links:
        if not alreadyPresent(item, index_links2):
            html += "<li>\n"
            htmls = str(item)
            html += htmls
            html += "</li>\n"
    html += "</ul>\n"
    html += "</div>\n"
    html += "<br />\n"
    html += "<h4>\n"
    html += "Website by "
    html += "<a href='https://polinetwork.org/'>"
    html += "PoliNetwork"
    html += "</a>\n"
    html += "</h4>\n"
    html += "</body>\n</html>\n"

    write_html(html, base_output2)

    pass


def selectWorkingBaseOutput(base_output_2):
    if base_output_2 is None:
        return None

    if len(base_output_2) == 0:
        return None

    if len(base_output_2) == 1:
        return base_output_2[0]

    if len(base_output_2) > 1:
        for b in base_output_2:
            if os.path.exists(b):
                return b

    return None
    pass


def getPath(param, param1):
    pass

    p2 = param1.split("/")

    return param + "/" + p2[2]


def getCorsoFase(elem2):
    path_2 = getPath(elem2["index"], elem2["path"])
    if path_2 is None:
        return None, None

    path_2 = str(path_2)

    with open(path_2, 'r') as f:
        contents = f.read()

        soup = BeautifulSoup(contents, features="html.parser")

        return getCorso(soup), getFase(soup)

    return None, None


def printResults():
    print("\n")
    print("Results:")
    print("Total = " + str(len(list_error_download) + len(list_download_completed) + len(list_already_done)))
    print("Download errors = " + str(len(list_error_download)))
    print("Download completed = " + str(len(list_download_completed)))
    print("Already done = " + str(len(list_already_done)))
    if len(list_download_completed) > 0:
        print("Completed download:")
        for i in list_download_completed:
            print(i)
    pass


def find_index(soup):
    results = []
    try:
        for item in soup.find_all('li', ):
            pass
            for item2 in item.contents:
                try:
                    pass
                    link = item2.attrs['href']
                    print(link)
                    results.append(item2)

                except:
                    pass
    except:
        pass
    return results


def getLinksIndex(base_output):
    print("Already in index [start]")

    try:
        with open(base_output + "\\index.html") as fp:
            soup = BeautifulSoup(fp, 'html.parser')

        return find_index(soup)

    except Exception as e:
        print(e)
        pass
    pass

    try:
        opener = urllib.request.FancyURLopener({})
        url = "https://raw.githubusercontent.com/PoliNetworkOrg/Rankings/main/docs/index.html"
        f = opener.open(url)
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')

        return find_index(soup)

    except Exception as e:
        print(e)
        pass
    pass

    print("Already in index [end]")


# main
if __name__ == '__main__':

    version = 7
    print("starting. version: " + str(version))

    global url_global

    start = "http://www.risultati-ammissione.polimi.it"
    base_output = []
    if sys.argv is None or len(sys.argv) < 2 or sys.argv[1] is None:
        base_output.append("D:\\git\\Polimi\\polinetwork.github.io\\graduatorie")
        base_output.append("C:\\git\\polinetwork.github.io\\graduatorie")
        base_output.append("D:\\git\\PoliNetwork\\Rankings\\docs")
    else:
        base_output.append(sys.argv[1])
    start_len = len(start)

    base_output = selectWorkingBaseOutput(base_output)

    if base_output is None:
        print("Base output error!")
        exit(-2)

    base_output = str(base_output)
    print("Chosen base output: " + base_output)

    index_previous_links = getLinksIndex(base_output)

    currentMonth = int(datetime.datetime.now().month)
    bruteforceEnabled = False
    # if currentMonth == 8:  # august
    #    bruteforceEnabled = True

    generateUrl(start, bruteforceEnabled)

    index_links = []

    redo = True
    print("Redo: " + str(redo))

    i = 0
    while i < len(url_global):

        url_global_item = url_global[i]

        success = -1
        folder, folder_first = directoryOutput(url_global_item["url"], base_output, start_len, return_first_folder=True)
        if os.path.isdir(folder):
            files = os.listdir(folder)
            if (files is None or len(files) == 0) or redo == True:
                success = executeDownload(url_global, i, start, base_output, only_first=False)
            else:
                list_already_done.append(url_global_item["url"])
                print("Already done [" + url_global_item["url"] + "]")
                executeDownload(url_global, i, start, base_output, only_first=True)
                success = 2
        else:
            success = executeDownload(url_global, i, start, base_output, only_first=False)

        if success == 1 or success == 2:
            path = url_global_item["url"][start_len:]
            if "corso" in url_global_item:
                elem = {
                    "url": url_global_item["url"],
                    "index": folder,
                    "folder": folder_first,
                    "year": url_global_item["year"],
                    "path": path,
                    "corso": url_global_item["corso"],
                    "fase": url_global_item["fase"]
                }
                index_links.append(elem)
            else:
                if success == 1:
                    pass
                elif success == 2:
                    elem = {
                        "url": url_global_item["url"],
                        "index": folder,
                        "folder": folder_first,
                        "year": url_global_item["year"],
                        "path": path
                    }

                    corso, fase = getCorsoFase(elem)

                    elem["corso"] = corso
                    elem["fase"] = fase
                    elem["delete"] = True

                    index_links.append(elem)
            pass

        i += 1

    print("Download done [all]!")

    write_index(index_links, base_output, index_previous_links)

    printResults()

    exit(0)
