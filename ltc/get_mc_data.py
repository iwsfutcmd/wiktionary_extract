import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import unicodedataplus as unicodedata

API_URL = "https://en.wiktionary.org/w/api.php"


def get_all_ltc():
    output = set()

    params = {
        "action": "query",
        "list": "embeddedin",
        "format": "json",
        "formatversion": "2",
        "eititle": "Module:ltc-pron",
        "eilimit": "max",
    }

    while True:
        r = requests.get(API_URL, params=params)
        data = r.json()
        for entry in data["query"]["embeddedin"]:
            output.add(entry["title"])
        if "continue" in data:
            params["eicontinue"] = data["continue"]["eicontinue"]
            print(params)
        else:
            break

    with open("all_ltc.json", "w") as file:
        json.dump(list(output), file)


def get_data(title, session=None):
    params = {
        "action": "parse",
        "format": "json",
        "title": title,
        "text": "{{zh-pron|mc=y|dial=n}}",
        "formatversion": "2",
        "prop": "text",
    }

    if session:
        r = session.get(API_URL, params=params)
    else:
        r = requests.get(API_URL, params=params)
    soup = BeautifulSoup(r.json()["parse"]["text"])
    try:
        initials = [
            int(re.search(r"\d+", tag.text.strip()).group())
            for tag in soup.find(string="Initial").find_parent("tr").find_all("td")
        ]
        finals = [
            int(re.search(r"\d+", tag.text.strip()).group())
            for tag in soup.find(string="Final").find_parent("tr").find_all("td")
        ]
        baxters = [
            tag.text.strip()
            for tag in soup.find(string="Baxter").find_parent("tr").find_all("td")
        ]
        cmns = [
            tag.text.strip()
            for tag in soup.find(string="Mandarin").find_parent("tr").find_all("td")
        ]
        yues = [
            tag.text.strip()
            for tag in soup.find(string="Cantonese").find_parent("tr").find_all("td")
        ]
    except AttributeError:
        initials = []
        finals = []
        baxters = []
        cmns = []
        yues = []
    return (title, list(zip(initials, finals, baxters, cmns, yues)))


def get_all_data():
    all_ltc = [
        t
        for t in json.load(open("all_ltc.json"))
        if len(t) == 1 and unicodedata.script(t) == "Han"
    ]
    output = []
    with requests.Session() as session:
        for title in tqdm(all_ltc):
            output.append(get_data(title, session))
            with open("data.json", "w") as file:
                json.dump(list(output), file)
