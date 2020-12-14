#!/bin/python3

from requests import get as getRequest
from xmltodict import parse
import textwrap
import os
from time import sleep


class TagesschauService:
    def __init__(self, max_link_len, n_below, n_top):
        self._url = "https://www.tagesschau.de/newsticker.rdf"
        self._max_link_len = max(max_link_len, n_below + 1)
        # number of articles below, chosen from max_link_len below top
        self._n_below = n_below
        # number of top articels, always displayed
        self._n_top = n_top
        self._shown_links = []

    def _request(self):
        try:
            rdf = getRequest(self._url)
        except:
            return []
        dic = parse(rdf.text)
        return dic["rss"]["channel"]["item"]

    def get_news(self):
        items = self._request()
        n_top = min(len(items), self._n_top)
        titles = [x["title"] for x in items[:n_top]]
        descriptions = [x["description"] for x in items[:n_top]]
        items = items[n_top:]
        link_len = min(self._max_link_len, len(items))
        if len(self._shown_links) + self._n_below > link_len:
            del self._shown_links[max(0, link_len - self._n_below) :]
        for i, link in enumerate([x["link"] for x in items[:link_len]]):
            if link not in self._shown_links and len(titles) < self._n_below + n_top:
                self._shown_links.insert(0, link)
                titles.append(items[i]["title"])
                descriptions.append(items[i]["description"])
        return titles, descriptions


if __name__ == "__main__":

    ts = TagesschauService(5, 2, 1)
    while True:
        titles, descriptions = ts.get_news()
        if len(titles) > 0:
            os.system("cls" if os.name == "nt" else "clear")
        for t, d in zip(titles, descriptions):
            print(t)
            print(textwrap.fill(d, 80, subsequent_indent="  ", initial_indent="  "))
        sleep(60)
