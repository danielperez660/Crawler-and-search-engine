import requests as r
import parsers
import time
import file_manager as fm
import operator

print("System started")
term_index = {}
url_index = {}
raw_index = {}


def robots_check(url):
    req = r.get(url + "/robots.txt").text.split("\n")
    time.sleep(5)

    disallow = []

    for ir in req:
        if "Disallow:" in str(ir):
            disallow.append(url + ir.split(": ")[1])

    return disallow


def get_info(req):
    html = req.text

    parser = parsers.Parser(html)

    term_list, freq = parser.get_term_list()
    urls = parser.get_urls()
    print("Crawling: " + req.url)

    return term_list, freq, urls


def term_search(term_input):
    if len(term_input) > 3:
        print("Too many items in your search query")
        return

    print("Searching...")
    print("Terms found in: ")

    sorted_urls = []

    if len(term_input) == 1:
        # Uses the frequency of the term * 10 / the first position of the term to create a score
        # Adds 1 to the position to avoid dividing by 0
        try:
            for documents in term_index[term_input[0]]:
                added = False

                freq = documents[1]
                position = raw_index[url_index[documents[0]]][1].index(term_input[0]) + 1
                new_score = (freq * 10) / position

                for num, val in enumerate(sorted_urls):
                    old_pos = raw_index[url_index[val[0]]][1].index(term_input[0]) + 1
                    old_score = (val[1] * 10) / old_pos

                    if new_score > old_score:
                        sorted_urls.insert(num, documents)
                        added = True
                        break

                if not added:
                    sorted_urls.append(documents)
        except KeyError:
            print("Term not found")
            return

        for urls in sorted_urls:
            print(url_index[urls[0]])
    else:
        temp = []
        shared_documents = []

        for query_term in term_input:
            try:
                temp.append(term_index[query_term])
            except KeyError:
                print("Ignoring term which was not found in any page")

        for lists in range(len(temp)):
            if (len(temp) == 2 and lists == 0) or (len(temp) == 3 and lists == 0):
                for term in temp[lists]:
                    item = []

                    for j in temp[lists + 1]:
                        item.append(j[0])

                    if term[0] in item:
                        shared_documents.append(term)

            elif len(temp) == 3 and lists == 1:
                item = []

                for j in shared_documents:
                    item.append(j[0])

                shared_documents = []

                for shared in temp[2]:
                    if shared[0] in item:
                        shared_documents.append(shared)

        frequency_counter = {}

        for urls in shared_documents:
            frequency_counter[url_index[urls[0]]] = 0

            for frequency_raw in raw_index[url_index[urls[0]]][0]:
                if frequency_raw[0] in term_input:
                    frequency_counter[url_index[urls[0]]] += int(frequency_raw[1])

        frequency_counter = sorted(frequency_counter.items(), key=operator.itemgetter(1))

        for document in range(len(frequency_counter)-1, -1, -1):
            print(frequency_counter[document][0])


while 1:
    query = input("SpiderMan:~$ ")
    command = query.split(" ")

    if "build" == command[0]:
        print("Building Inverse Index")

        url_start = "http://example.webscraping.com"

        disallow_list = robots_check(url_start)
        terms, frequency, url_list = get_info(r.get(url_start))
        time.sleep(5)

        term_index = {url_start: (frequency, terms)}

        for i in url_list:
            res = ""

            if i not in disallow_list and "?" not in i and i not in term_index:
                res = r.get(i)
                time.sleep(5)
            else:
                continue

            if res.url not in term_index and "?" not in res.url:
                site_terms, frequency, site_urls = get_info(res)
                term_index[res.url] = (frequency, site_terms)

                for new_url in site_urls:
                    if new_url not in url_list and "?" not in new_url:
                        url_list.append(new_url)

        print("Inverse Index Completed")
        fm.update_db(term_index)

    elif "load" == command[0]:
        term_index, url_index, raw_index = fm.get_db()
        print("Loaded Inverse Index")

    elif "print" == command[0]:
        if term_index == {}:
            print("Reversed Index Not Loaded")
        else:
            try:
                print(command[1], "was found in:")
                for i in term_index[command[1]]:
                    print("Document indexed at: " + str(i[0]) + ", " + str(i[1]) + " times -> " + url_index[i[0]])
            except KeyError:
                print("Term not found")

    elif "find" == command[0]:
        if term_index == {}:
            print("Reversed Index Not Loaded")
        else:
            if command[1] == "":
                print("Query Too Short")
            else:
                term_search(command[1:])

    else:
        print("Incorrect syntax \nCommands: build, load, print, find")
