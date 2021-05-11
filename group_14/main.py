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


if __name__ == '__main__':
    data_scraper = DataScraper()
    data_scraper.load_data_to_json()
