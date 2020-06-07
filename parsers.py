from bs4 import BeautifulSoup
import re


class Parser:
    def __init__(self, html):
        self.html = html
        self.bs = BeautifulSoup(self.html, 'html.parser')

    def get_term_list(self):
        html = str(self.bs).replace("</td>", " </td>")
        html = html.replace("</a>", " </a>")

        parsed = BeautifulSoup(html, features="html.parser").get_text()
        parsed = re.sub(r'[<>|():;,]', '', parsed)

        term = ""

        frequency_list = []
        term_list = []

        for i in parsed:
            if not i.isspace():
                term += i
            else:
                if not term.isspace() and term != "" and term.isalpha():
                    term_list.append(term)
                term = ""

        checked = []
        for i in term_list:
            if i not in checked:
                checked.append(i)
                frequency_list.append((i, term_list.count(i)))

        return term_list, frequency_list

    def get_urls(self):
        urls = self.bs.find_all("a")
        parsed_urls = []

        for i in urls:
            i = str(i)

            path = i.split("href=")[1]
            path = path.split("\"")[1]

            if "/" in path and "?" not in path:
                parsed_urls.append("http://example.webscraping.com" + path)

        return parsed_urls
