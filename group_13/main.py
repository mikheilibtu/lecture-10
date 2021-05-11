"""
ამ პრაქტიკული ამოცანის მიზანია შევაგროვოთ ინფორმაცია გამოთქმების შესახებ შემდეგი ვებსაიტიდან - http://quotes.toscrape.com.
1. უნდა შევაგროვოთ შემდეგი ინფორმაცია:
- გამონათქვამი
- ავტორი
- ტაგები
შეგროვებული ინფორმაცია ჩავწეროთ ფაილურ სისტემაში JSON ფორმატში.

2. ინფორმაციის შეგროვების მერე დავადგინოთ სტატისტიკური მახასიათებლები ავტორების შესახებ:
- სულ რამდენი ავტორია ვებსაიტზე
- რომელ ავტორს რამდენი გამონათქვამი ეკუთვნის
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


class QuoteScraper:
    URL = "http://quotes.toscrape.com"

    def __init__(self):
        self.results = []

    def _scrape_page(self, html_text):
        html_tree = BeautifulSoup(html_text, "html.parser")
        quote_divs = html_tree.find_all("div", attrs={"class": "quote"})

        for quote_div in quote_divs:
            quote = quote_div.find("span", attrs={"class": "text"}).get_text()
            author = quote_div.small.get_text()
            tag_htmls = quote_div.find_all("a", attrs={"class": "tag"})
            tags = [tag.text for tag in tag_htmls]
            quote_dict = {
                "quote": quote,
                "author": author,
                "tags": tags
            }
            self.results.append(quote_dict)

        next_page_button = html_tree.find("li", attrs={"class": "next"})
        if next_page_button:
            next_url_suffix = next_page_button.a.attrs.get("href")
            next_page_url = urljoin(self.URL, next_url_suffix)
            print(next_page_url)
            response = requests.get(next_page_url)
            return self._scrape_page(response.text)

        print("Finished")

    def _save_to_disk(self):
        with open("result.json", "w") as file:
            json.dump(self.results, file, indent=4)

    def scrape_quotes(self):
        response = requests.get(self.URL)
        self._scrape_page(response.text)
        print(f"Count - {len(self.results)}")
        pprint(self.results)
        self._save_to_disk()


def generate_stats_about_authors(filename):
    data = load_json(filename)
    stats_dict = {}
    for quote in data:
        author_name = quote.get("author")
        if author_name in stats_dict:
            stats_dict[author_name] = stats_dict[author_name] + 1
        else:
            stats_dict[author_name] = 1
    result = {
        "authors_count": len(stats_dict.keys()),
        "author_stats": stats_dict
    }
    dump_json(result, "author_stats.json")


def dump_json(result, filename):
    with open(filename, "w") as file:
        json.dump(result, file, indent=4)


def load_json(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data


def generate_stats_about_tags(filename):
    data = load_json(filename)
    stats_dict = {}
    for quote in data:
        for tag in quote.get("tags", []):
            if tag in stats_dict:
                stats_dict[tag] = stats_dict[tag] + 1
            else:
                stats_dict[tag] = 1
    tags_count = len(stats_dict.keys())
    sorted_stats = sorted([(key, value) for key, value in stats_dict.items()], key=lambda pair: pair[1], reverse=True)
    top_5_tag = sorted_stats[:5]
    top_5_tag = [pair[0] for pair in top_5_tag]  # Extract tags
    result = {
        "tags_count": tags_count,
        "top_5_tag": top_5_tag,
        "tag_stats": stats_dict
    }
    dump_json(result, "tags_stats.json")


if __name__ == '__main__':
    quote_scraper = QuoteScraper()
    quote_scraper.scrape_quotes()
    generate_stats_about_authors("result.json")
    generate_stats_about_tags("result.json")
