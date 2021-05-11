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


if __name__ == '__main__':
    data_scraper = DataScraper()
    data_scraper.load_data()
