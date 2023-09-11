import json
from collections import Counter, defaultdict
from itertools import count
from tqdm import tqdm
needed_info = ["word", "lang", "lang_code"]
# root_entries = Counter()
# translation_entries = Counter()
# sense_translation_entries = Counter()
# form_entries = Counter()
# linkage_entries = Counter()
entries = Counter()
etymology_entries = Counter()
broken_entries = []
linkages = ["synonyms", "antonyms", "derived words", "holonyms", "meronyms", "derived", "related", "coordinate_terms"]
def extract():
    with open("raw-wiktextract-data.json") as file:
        for i, line in tqdm(enumerate(file)):
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
                if linkage not in entry: continue
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
    code = translation_entry["code"]
    if not code:
        code = "XXXX"
    # return "\t".join([word, lang, code])
    return (word, lang, code)

def get_all_words(entries):
    output = defaultdict(set)
    for word, _, code in entries:
        output[code].add(word)
    for code in output:
        with open("wordlists/" + code + ".txt", "w") as file:
            for word in output[code]:
                file.write(word + "\n")

def find_entry(identifier):
    with open("raw-wiktextract-data.json") as file:
        for line in file:
            entry = json.loads(line)
            if "word" not in entry:
                continue
            word = entry["word"]
            lang = entry["lang"]
            lang_code = entry["lang_code"]
            if (word, lang, lang_code) == identifier:
                return entry
