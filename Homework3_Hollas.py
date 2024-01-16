import requests
import json
import re
from nltk import PorterStemmer

stemmer = PorterStemmer()

url = 'https://poetrydb.org/author,title/Shakespeare;Sonnet'
response = requests.get(url)
data = json.loads(response.text)
# print(data)


class Document:
    def __init__(self, lines):
        self.lines = lines

    def tokenize(self) -> list[str]:
        tokens = []
        punctuation = '.,"\'!;:?'
        for line in self.lines:
            line = line.lower().strip()
            for character in punctuation:
                line = line.replace(character, '')
            tokenized_line = line.split()
            stemmed_tokens = [stemmer.stem(token) for token in tokenized_line]
            tokens.extend(stemmed_tokens)
        return tokens


class Query(Document):
    def __init__(self, query: str):
        super().__init__([query])


class Sonnet(Document):
    def __init__(self, title, lines):
        super().__init__(lines)
        self.id = None
        self.title = None
        self.sonnet_details(title)

    def sonnet_details(self, title):
        details = re.match(r'Sonnet (\d+): (.+)', title)
        self.id = int(details.group(1))
        self.title = details.group(2)

    def __str__(self):
        sonnet_text = f"\nSonnet {self.id}: {self.title}\n"
        sonnet_text += "\n".join(self.lines)
        return sonnet_text

    def __repr__(self):
        return f"Sonnet(id={self.id}, title='{self.title}', lines={self.lines})"


class Index(dict[str, set[int]]):
    def __init__(self, documents: list[Sonnet]):
        super().__init__()
        self.documents = documents
        self.add(documents)

    def add(self, documents: list[Sonnet]):
        for document in documents:
            stemmed_tokens = document.tokenize()
            for token in stemmed_tokens:
                if token not in self.keys():
                    self[token] = set()
                self[token].add(document.id)

    def search(self, query: Query) -> list[Sonnet]:
        # document ids that match the query
        tokenized_query = query.tokenize()
        matching_document_ids = set.intersection(*(self[token] for token in tokenized_query))
        # document ids to a list of corresponding sonnets
        matching_sonnets = [sonnet for sonnet in self.documents if sonnet.id in matching_document_ids]

        return matching_sonnets


# list of dictionaries to a list of Sonnet instances
sonnets = [Sonnet(sonnet_data.get('title', ''), sonnet_data.get('lines', [])) for sonnet_data in data]

# instance of the Index class and passing the list of sonnets to it
index = Index(sonnets)


def display_sonnets(sonnets):
    if not sonnets:
        print("No matching sonnets found.")
        return

    print(f"Your search for '{user_input}' matched {len(sonnets)} sonnets:")
    for sonnet in sonnets:
        print(sonnet)


while True:
    user_input = input("Search for sonnets ('q' to quit)> ")
    if user_input.lower() == 'q':
        break

    query = Query(user_input)
    matching_sonnets = index.search(query)

    matching_ids = [sonnet.id for sonnet in matching_sonnets]
    print(f"Matching Sonnet IDs: {matching_ids}")

    display_sonnets(matching_sonnets)
