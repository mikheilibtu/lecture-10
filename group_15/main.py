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
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class DataScraper:
    URL = "http://quotes.toscrape.com"

    def __init__(self):
        self.results = []

    def _parse_quotes(self, html_text):
        html_tree = BeautifulSoup(html_text, "html.parser")

        quote_divs = html_tree.find_all("div", attrs={"class": "quote"})
        for quote_div in quote_divs:
            quote = quote_div.find("span", attrs={"class": "text"}).get_text()
            quote = quote[1:-1]
            author = quote_div.find("small").get_text()
            tag_htmls = quote_div.find_all(attrs={"class": "tag"})
            tags = [tag.get_text() for tag in tag_htmls]
            quote_dict = {
                "quote": quote,
                "author": author,
                "tags": tags
            }

            self.results.append(quote_dict)
        next_page_button = html_tree.find("li", attrs={"class": "next"})
        if next_page_button:
            href = next_page_button.a.attrs.get("href")
            next_page_url = urljoin(self.URL, href)
            print(next_page_url)
            response = requests.get(next_page_url)
            return self._parse_quotes(response.text)
        print("Finished")

    def _save_to_disk(self, filename):
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=4)

    def load_data(self):
        response = requests.get(self.URL)
        self._parse_quotes(response.text)
        print("Loaded - ", len(self.results))
        self._save_to_disk("result.json")
        # pprint(self.results)


def load_json(fname):
    with open(fname, "r") as file:
        return json.load(file)


def dump_json(fname, data):
    with open(fname, "w") as file:
        json.dump(data, file, indent=4)


def generate_author_stats(filename):
    data = load_json(filename)
    authors_dict = dict()
    for doc in data:
        author = doc.get("author")
        if author in authors_dict:
            authors_dict[author] = authors_dict[author] + 1
        else:
            authors_dict[author] = 1
    result = {
        "author_count": len(authors_dict.keys()),
        "stats": authors_dict
    }
    dump_json("authors_stats.json", result)


def generate_tags_stats(filename):
    data = load_json(filename)
    tags_dict = dict()
    for doc in data:
        tags = doc.get("tags", [])
        for tag in tags:
            if tag in tags_dict:
                tags_dict[tag] += 1
            else:
                tags_dict[tag] = 1
    tag_count = len(tags_dict.keys())

    sorted_dict = sorted(tags_dict.items(), key=lambda item: item[1], reverse=True)
    top_5 = sorted_dict[:5]
    top_5 = [k for k, _ in top_5]

    result = {
        "tag_count": tag_count,
        "stats": tags_dict,
        "top_5_tag": top_5
    }

    dump_json("tags_stats.json", result)


if __name__ == '__main__':
    data_scraper = DataScraper()
    data_scraper.load_data()
    generate_author_stats("result.json")
    generate_tags_stats("result.json")
