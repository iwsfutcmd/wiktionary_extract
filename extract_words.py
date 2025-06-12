import os

import json
from collections import Counter, defaultdict
from itertools import count
from tqdm import tqdm
import unicodedataplus as unicodedata

needed_info = ["word", "lang", "lang_code"]
# root_entries = Counter()
# translation_entries = Counter()
# sense_translation_entries = Counter()
# form_entries = Counter()
# linkage_entries = Counter()
entries = Counter()
etymology_entries = Counter()
broken_entries = []
linkages = [
    "synonyms",
    "antonyms",
    "derived words",
    "holonyms",
    "meronyms",
    "derived",
    "related",
    "coordinate_terms",
]


def extract():
    file_path = "raw-wiktextract-data.jsonl"
    file_size = os.path.getsize(file_path)
    with open(file_path) as file, tqdm(
        total=file_size, unit="B", unit_scale=True, desc="Reading file"
    ) as pbar:
        for i, line in enumerate(file):
            pbar.update(len(line.encode("utf-8")))
            # if i > 10000:
            #     break
            entry = json.loads(line)
            if "word" not in entry:
                continue
            lang = entry["lang"]
            lang_code = entry["lang_code"]
            entries[(entry["word"], lang, lang_code)] += 1
            # if "forms" in entry:
            #     for form_entry in entry["forms"]:
            #         if form_entry["form"] == "-": continue
            #         form_entries["\t".join((form_entry["form"], lang, lang_code))] += 1
            if "translations" in entry:
                for translation_entry in entry["translations"]:
                    e = extract_translation(translation_entry)
                    if e:
                        entries[e] += 1
            # if "senses" in entry:
            #     # print(f"senses found in {entry['word']} {lang} {lang_code}")
            #     for sense in entry["senses"]:
            #         if "translations" in sense:
            #             print(f"translation sense found in {entry['word']} {lang} {lang_code}")
            #             for translation_entry in sense["translations"]:
            #                 e = extract_translation(translation_entry)
            #                 if e:
            #                     sense_translation_entries[e] += 1
            # for linkage in linkages:
            #     if linkage not in sense: continue
            #     for linkage_entry in sense[linkage]:
            #         linkage_entries[(linkage_entry["word"], lang, lang_code)] += 1
            for linkage in linkages:
                if linkage not in entry:
                    continue
                for linkage_entry in entry[linkage]:
                    entries[(linkage_entry["word"], lang, lang_code)] += 1
            # if "etymology_templates" in entry:
            #     for template in entry["etymology_templates"]:
            #         name = template["name"]
            #         args = template["args"]
            #         word = ""
            #         code = ""
            #         script = ""
            #         if name == "root":
            #             for n in count(3):
            #                 string_n = str(n)
            #                 if string_n not in template:
            #                     break
            #                 word = template[string_n]
            #                 etymology_entries[(word, "", code)] += 1
            # elif name in {"inh", "inh+", "inh-lite", "inherited"}:

    # with open("root_entries.json", "w") as file:
    #     json.dump([[k, v] for k, v in root_entries.items()], file)
    # with open("translation_entries.json", "w") as file:
    #     json.dump([[k, v] for k, v in translation_entries.items()], file)
    # with open("linkage_entries.json", "w") as file:
    #     json.dump([[k, v] for k, v in linkage_entries.items()], file)
    # with open("sense_translation_entries.json", "w") as file:
    #     json.dump(sense_translation_entries, file)
    # with open("form_entries.json", "w") as file:
    #     json.dump(form_entries, file)
    with open("entries.json", "w") as file:
        json.dump([[k, v] for k, v in entries.items()], file)


def extract_translation(translation_entry):
    if "word" not in translation_entry:
        return None
    word = translation_entry["word"]
    lang = translation_entry["lang"]
    code = translation_entry.get("code", "XXXX")
    # return "\t".join([word, lang, code])
    return (word, lang, code)


def get_all_words(entries):
    output = defaultdict(set)
    for (word, _, code), _ in tqdm(entries):
        output[code].add(word)
    for code in tqdm(output):
        with open("wordlists/" + code, "w") as file:
            for word in sorted(output[code]):
                file.write(word + "\n")


def find_entry(identifier):
    with open("raw-wiktextract-data.jsonl") as file:
        for line in tqdm(file):
            entry = json.loads(line)
            if "word" not in entry:
                continue
            word = entry["word"]
            lang = entry["lang"]
            lang_code = entry["lang_code"]
            if (word, lang, lang_code) == identifier:
                return entry


def get_pronunciations():
    entries = {}
    file_path = "raw-wiktextract-data.jsonl"
    file_size = os.path.getsize(file_path)
    with open(file_path) as file, tqdm(
        total=file_size, unit="B", unit_scale=True, desc="Reading file"
    ) as pbar:
        for i, line in enumerate(file):
            pbar.update(len(line.encode("utf-8")))
            # if i > 50000:
            #     break
            entry = json.loads(line)
            if "word" not in entry:
                continue
            if "sounds" not in entry:
                continue
            if entry["lang_code"] not in entries:
                entries[entry["lang_code"]] = []
            for sound in entry["sounds"]:
                if "ipa" in sound:
                    entries[entry["lang_code"]].append([entry["word"], sound["ipa"]])
    with open("pronuciations.json", "w") as file:
        json.dump(entries, file, ensure_ascii=False)


def normalize_latin(s):
    return (
        unicodedata.normalize("NFD", s.lower())
        .replace("\u0304", "")
        .replace("æ", "ae")
        .replace("œ", "oe")
    )


def normalize_ipa(s):
    return s.replace(".", "").replace("ˈ", "").replace("ˌ", "")


def correlate_latin_prons():
    latin_words = [word.strip() for word in open("wordlists/la").readlines()]
    eng_prons = json.load(open("pronuciations.json"))["en"]
    eng_pron_dict = defaultdict(list)
    for word, pron in tqdm(eng_prons):
        if pron.startswith("/") and pron.endswith("/"):
            eng_pron_dict[normalize_latin(word)].append(normalize_ipa(pron).strip("/"))
    output = defaultdict(list)
    for word in tqdm(latin_words):
        nword = normalize_latin(word)
        if nword in eng_pron_dict:
            output[word].extend(eng_pron_dict[nword])
    with open("latin_eng_prons.json", "w") as file:
        json.dump(output, file, ensure_ascii=False)


def tag_string(tags):
    return json.dumps(sorted(tags))

def form_tags(sound):
    return tag_string(sound.get("tags", []) + sound.get("raw_tags", []))


def extract_chinese_data():
    chinese_data = {}
    file_path = "raw-wiktextract-data.jsonl"
    file_size = os.path.getsize(file_path)
    with open(file_path) as file, tqdm(
        total=file_size, unit="B", unit_scale=True, desc="Reading file"
    ) as pbar:
        for i, line in enumerate(file):
            pbar.update(len(line.encode("utf-8")))
            # if i > 100000: break
            entry = json.loads(line)
            if (
                "word" not in entry
                or "lang_code" not in entry
                or entry["lang_code"] != "zh"
                or "sounds" not in entry
            ):
                continue
            
            for sound in entry["sounds"]:
                tags = form_tags(sound)
                if tags not in chinese_data:
                    chinese_data[tags] = {}
                if entry["word"] not in chinese_data[tags]:
                    chinese_data[tags][entry["word"]] = []
                if "ipa" in sound:
                    chinese_data[tags][entry["word"]].append(sound["ipa"])
                if "zh-pron" in sound:
                    chinese_data[tags][entry["word"]].append(sound["zh-pron"])
    with open("chinese_data.json", "w") as file:
        json.dump(chinese_data, file, ensure_ascii=False)
    return chinese_data

registered_tags = {
    tag_string(["Cantonese", "Jyutping"]): "JyutPing",
    tag_string(["Mandarin", "Pinyin"]): "PinYin",
    tag_string(["Hokkien", "Min-Nan", "POJ"]): "PehOeJi",
    tag_string(["Middle-Chinese"]): "Baxter",
    tag_string(["Northern", "Wu", "Wugniu"]): "WuGniu",
    tag_string(["Baxter-Sagart", "Old-Chinese"]): "Baxter-Sagart",
    tag_string(["Hagfa-Pinyim", "Hakka", "Miaoli", "Neipu", "Sixian"]): "HagfaPinyim",
}

def dump_chinese_data(chinese_data):
    for tag, name in registered_tags.items():
        with open(f"zh-pron/{name}.wiktionary.json", "w") as file:
            json.dump(chinese_data[tag], file, ensure_ascii=False)

