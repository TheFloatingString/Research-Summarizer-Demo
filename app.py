import requests
from bs4 import BeautifulSoup
from summa import summarizer
from flask import Flask

import json

class SearchItem():

	def __init__(self):
		self.article_ids = list()
		self.soup = BeautifulSoup("", "html.parser")
		self.content_dict = dict()

	def search_term(self, term):
		count = 0
		resp = requests.get(f"https://pubmed.ncbi.nlm.nih.gov/?term={term}")
		self.soup = BeautifulSoup(resp.content, "html.parser")
		for article_id in [x.get("data-article-id") for x in self.soup.find_all("a") if x.get("data-article-id") is not None]:
			try:
				resp_article = requests.get(f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/")
				sub_soup = BeautifulSoup(resp_article.content, "html.parser")
				title = sub_soup.find(property="og:title")["content"].replace(" - PubMed", '')

				abstract = sub_soup.find(id="abstract").get_text()

				sub_dict = {}
				sub_dict["id"] = article_id
				sub_dict["title"] = title
				sub_dict["abstract"] = abstract
				sub_dict["summary"] = summarizer.summarize(abstract)
				sub_dict["tags"] = [x.get("data-ga-label") for x in sub_soup.find_all(class_="search-in-pubmed-link")]

				self.content_dict[count] = sub_dict
				count += 1
			except:
				pass

		return self.content_dict

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
	return "Home"

@app.route("/search/<search_name>", methods=["GET"])
def search(search_name):
	obj = SearchItem()
	content = obj.search_term(search_name)
	return json.dumps(content, indent=4, sort_keys=True)

if __name__ == '__main__':
	app.run(port=5000, host="0.0.0.0")