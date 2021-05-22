"""
ამ პრაქტიკული ამოცანის მიზანია შევაგროვოთ ინფორმაცია გამოთქმების შესახებ შემდეგი ვებსაიტიდან - http://quotes.toscrape.com.
1. უნდა შევაგროვოთ შემდეგი ინფორმაცია:
- გამონათქვამი
- ავტორი
- ტაგები
შეგროვებული ინფორმაცია ჩავწეროთ ფაილურ სისტემაში JSON ფორმატში.

2. ინფორმაციის შეგროვების მერე დავადგინოთ სტატისტიკური მახასიათებლები ავტორების შესახებ:
- სულ რამდენი ავტორია ვებსაიტზე
- რომელ ავტორის რამდენი გამონათქვამი ეკუთვნის
    დამუშავებული ინფორმაცია ჩავწეროთ ფაილურ სისტემაში JSON ფორმატში.

3. დავადგინოთ სტატისტიკური მახასიათებლები ტააგების შესახებ:
- სულ რამდენი ტაგი შეგვხვდა ვებსაიტზე
- თითოეული ტაგი რამდენჯერ გვხვდება
- 5 ყველაზე პოპულარული ტაგი
    დამუშავებული ინფორმაცია ჩავწეროთ ფაილურ სისტემაში JSON ფორმატში.
"""
import json
from pprint import pprint
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class Quote:
    def __init__(self, quote, author, tags):
        self.quote = quote
        self.author = author
        self.tags = tags

    def to_dict(self):
        return {
            "quote": self.quote,
            "author": self.author,
            "tags": self.tags
        }

    def __str__(self):
        return f"{self.author} \n {self.quote}"

    def __repr__(self):
        return str(self)


class DataScraper:
    URL = "http://quotes.toscrape.com"

    def __init__(self, filename):
        self.filename = filename
        self.results = []

    def _parse_quotes(self, html_text):

        html_tree = BeautifulSoup(html_text, "html.parser")
        quote_divs = html_tree.find_all(attrs={"class": "quote"})

        for quote_div in quote_divs:
            quote = quote_div.find("span", attrs={"class": "text"}).text
            quote = quote[1:-1]
            author = quote_div.find("small").text
            tag_htmls = quote_div.find_all("a", attrs={"class": "tag"})
            tags = [tag.text for tag in tag_htmls]

            q = Quote(quote, author, tags)
            self.results.append(q)

        next_page_button = html_tree.find("li", attrs={"class": "next"})
        if next_page_button:
            next_url = next_page_button.a.attrs.get("href")
            next_page_url = urljoin(self.URL, next_url)
            print(next_page_url)
            response = requests.get(next_page_url)
            return self._parse_quotes(response.text)
        print("Finished")

    def _save_to_disk(self):
        data = [q.to_dict() for q in self.results]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        response = requests.get(self.URL)
        self._parse_quotes(response.text)
        print("Count -", len(self.results))
        pprint(self.results)
        self._save_to_disk()
        return self.results


def load_json(fname):
    with open(fname, "r") as file:
        return json.load(file)


def dump_json(fname, data):
    with open(fname, "w") as file:
        json.dump(data, file, indent=4)


def create_authors_stats(filename):
    data = load_json(filename)
    authors_dict = dict()
    for document in data:
        author = document.get("author")
        if author not in authors_dict:
            authors_dict[author] = 1
        else:
            authors_dict[author] = authors_dict[author] + 1
    author_count = len(authors_dict.keys())
    result = {
        "author_count": author_count,
        "stats": authors_dict
    }
    dump_json("author_stats.json", result)


def create_tags_stats(filename):
    data = load_json(filename)
    stats_dict = {}
    for document in data:
        tags = document.get("tags", [])
        for tag in tags:
            if tag in stats_dict:
                stats_dict[tag] += 1
            else:
                stats_dict[tag] = 1
    tags_count = len(stats_dict.keys())

    sorted_tags = sorted(stats_dict.items(), key=lambda item: item[1], reverse=True)
    top_5 = sorted_tags[:5]
    top_5 = [k for k, _ in top_5]

    result = {
        "tags_count": tags_count,
        "stats": stats_dict,
        "top_5_tag": top_5
    }
    dump_json("tags_stats.json", result)


if __name__ == '__main__':
    data_scraper = DataScraper("result.json")
    data_scraper.load_data()
    create_authors_stats("result.json")
    create_tags_stats("result.json")
