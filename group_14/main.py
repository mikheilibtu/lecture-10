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

3. დავადგინოთ სტატისტიკური მახასიათებლები ტაგების შესახებ:
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


class DataScraper:
    URL = "http://quotes.toscrape.com"

    def __init__(self):
        pass

    def _scrape_quotes(self, html_text, result=None):
        if not result:
            result = []
        html_tree = BeautifulSoup(html_text, "html.parser")
        quote_divs = html_tree.find_all("div", attrs={"class": "quote"})
        for quote_div in quote_divs:
            quote = quote_div.find(itemprop="text").get_text()  # Extract quote
            author = quote_div.find(itemprop="author").get_text()  # Extract author
            tag_htmls = quote_div.find_all("a", attrs={"class": "tag"})  # Extract tags
            tags = [tag.get_text() for tag in tag_htmls]
            quote_dict = {
                "quote": quote,
                "author": author,
                "tags": tags
            }
            result.append(quote_dict)

        next_page_li = html_tree.find("li", attrs={"class": "next"})
        if next_page_li:
            next_page = next_page_li.a.attrs.get("href")
            next_page_url = urljoin(self.URL, next_page)
            print("Found next page - ", next_page_url)
            response = requests.get(next_page_url)
            return self._scrape_quotes(response.text, result)

        print("Paging finished")
        return result

    def _save_to_disk(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_data_to_json(self):
        response = requests.get(self.URL)
        results = self._scrape_quotes(response.text)

        self._save_to_disk("result.json", results)
        pprint(results)


def calculate_author_stats(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    authors_dict = {}
    for document in data:
        author = document.get("author")
        if author not in authors_dict:
            authors_dict[author] = 1
        else:
            authors_dict[author] = authors_dict[author] + 1
    authors_count = len(authors_dict.keys())
    result = {
        "count": authors_count,
        "stats": authors_dict
    }
    save_as_json("author_stats.json", result)


def save_as_json(fname, result):
    with open(fname, "w") as file:
        json.dump(result, file, indent=4)


def calculate_tags_stats(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    tags_dict = {}
    for document in data:
        tags = document.get("tags", [])
        for tag in tags:
            if tag in tags_dict:
                tags_dict[tag] = tags_dict[tag] + 1
            else:
                tags_dict[tag] = 1
    tags_count = len(tags_dict.keys())
    pprint(tags_dict)
    _sorted = sorted([(k, v) for k, v in tags_dict.items()], key=lambda pair: pair[1], reverse=True)
    _sorted = _sorted[:5]
    top_5 = [k for k, v in _sorted]  # 1M operation 6 GB

    result = {
        "tags_count": tags_count,
        "stats": tags_dict,
        "top_5": top_5
    }

    save_as_json("tags_stats.json", result)


if __name__ == '__main__':
    data_scraper = DataScraper()

    data_scraper.load_data_to_json()

    calculate_author_stats("result.json")
    calculate_tags_stats("result.json")
