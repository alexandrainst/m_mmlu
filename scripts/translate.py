import csv
import json
from os import PathLike
from pathlib import Path
import re

import dicttoxml
import xmltodict
from xml.parsers.expat import ExpatError

from deepl.translator import Translator
from greynir_client.client import translate_en_to_is

import utils

def translate_mmlu_csv(csv_path: Path, output_path: PathLike, target_lang: str, dryrun=False, use_xml=True):

    translate_text = utils.get_translator(target_lang, dryrun)

    translated_rows = []
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            instruction, option_a, option_b, option_c, option_d, answer = row

            to_translate = {"ins": instruction, "opt_a": option_a, "opt_b": option_b, "opt_c": option_c, "opt_d": option_d}
            if use_xml:
                xml = dicttoxml.dicttoxml(to_translate, root=True, attr_type=False, return_bytes=False)
                restored = xmltodict.parse(xml)
                translated = translate_text(xml)
                try:
                    translated_dict = xmltodict.parse(translated)["root"]
                except ExpatError:
                    fixed_xml = utils.fix_xml_error(translated)
                    translated_dict = xmltodict.parse(fixed_xml)["root"]
            else:
                translated_dict = {k: translate_text(v) for k, v in to_translate.items()}

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
    #target_langs = ["nb"] #, "is"]
    target_langs = ["is"]
    source_dir = Path("data/")

    for lang in target_langs:
        out_dir = Path(f"data_{lang}")
        out_dir.mkdir(exist_ok=True)
        #for path in source_dir.glob(pattern="{dev,test,val}/**/*.csv"):
        for subset in ["dev", "test", "val"]:
            for path in (source_dir / subset).glob("*.csv"):
                rel_dir = path.relative_to(source_dir)
                output_path = (out_dir / rel_dir).with_suffix(".json")
                if output_path.exists():
                    print("skipping", path, output_path)
                else:
                    print(path, output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    if lang == "is":
                        use_xml = False
                    else:
                        use_xml = True
                    translate_mmlu_csv(path, output_path, lang, use_xml=use_xml)

if __name__ == "__main__":
    main()
