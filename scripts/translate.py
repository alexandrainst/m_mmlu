import csv
import json
from os import PathLike
import pathlib
from pathlib import Path
from typing import Optional

import dicttoxml
import xmltodict

from deepl.translator import Translator


class DummyTranslator:
    def __init__(self):
        self.character_count = 0
    def translate_text(self, text):
        self.character_count += len(text)
        return text

def translate_mmlu_csv(csv_path: Path, output_path: PathLike, target_lang: str, dryrun=False):
    with open("deepl_key.txt", "r") as key_file:
        auth_key = key_file.read().strip()

    if dryrun:
        translator = DummyTranslator()
        translate_text = lambda x: translator.translate_text(x)
    else:
        translator = Translator(auth_key)
        translate_text = lambda x: translator.translate_text(x, source_lang="en", target_lang=target_lang, tag_handling="xml", preserve_formatting=True).text

    translated_rows = []
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            instruction, option_a, option_b, option_c, option_d, answer = row
            to_translate = {"ins": instruction, "opt_a": option_a, "opt_b": option_b, "opt_c": option_c, "opt_d": option_d}
            xml = dicttoxml.dicttoxml(to_translate, root=True, attr_type=False, return_bytes=False)
            restored = xmltodict.parse(xml)
            translated = translate_text(xml)
            translated_dict = xmltodict.parse(translated)["root"]
            output_dict = {
                "instruction": translated_dict["ins"],
                "option_a": translated_dict["opt_a"],
                "option_b": translated_dict["opt_b"],
                "option_c": translated_dict["opt_c"],
                "option_d": translated_dict["opt_d"],
                "answer": answer,
                "id": "/".join(["_".join(csv_path.stem.split("_")[:-1]), csv_path.parent.name, "%d" % i]),
            }
            translated_rows.append(output_dict)

    # Write to json in utf8 format
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(translated_rows, f, indent=2, ensure_ascii=False)




def main():
    target_langs = ["nb"] #, "is"]
    source_dir = Path("data/")

    for lang in target_langs:
        out_dir = Path(f"data_{lang}")
        out_dir.mkdir(exist_ok=True)
        #for path in source_dir.glob(pattern="{dev,test,val}/**/*.csv"):
        for subset in ["dev", "test", "val"]:
            for path in (source_dir / subset).glob("*.csv"):
                rel_dir = path.relative_to(source_dir)
                output_path = (out_dir / rel_dir).with_suffix(".json")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                print(path, output_path)
                translate_mmlu_csv(path, output_path, lang)

if __name__ == "__main__":
    main()
