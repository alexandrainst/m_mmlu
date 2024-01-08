import csv
import json
from os import PathLike
from pathlib import Path

import dicttoxml
import xmltodict
from xml.parsers.expat import ExpatError

import utils

def normalise_label(label: str):
    try:
        intrepr = int(label)
        normalised_label = "Xabcde"[intrepr]
    except ValueError:
        normalised_label = label.lower()
    assert normalised_label in "abcde"

    return normalised_label

replacements = {
    "\x02": "" # Start of text unicode character causes problems for xml encoding
}

def normalise_text(text):
    for key, val in replacements.items():
        text = text.replace(key, val)
    return text


def translate_arc(jsonlpath: Path, output_path: PathLike, target_lang: str, dryrun=False, use_xml=True):

    translate_text = utils.get_translator(target_lang, dryrun)

    translated_rows = []
    with open(jsonlpath, "r") as f:
        for row in f:
            js = json.loads(row)

            to_translate = {
                "instruction":   normalise_text(js["question"]["stem"]),
            }
            for choice in js["question"]["choices"]:
                label = normalise_label(choice["label"])
                to_translate[f"option_{label}"] = choice["text"]

            answer = normalise_label(js["answerKey"])
            parts = jsonlpath.stem.split("-")
            idname = f"{parts[0]}-{parts[1]}/{parts[2].lower().replace('dev','validation')}/{js['id']}"

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
                "id": idname,
                "answer": answer,
            }
            output_dict.update(translated_dict)
            translated_rows.append(output_dict)

    # Write to json in utf8 format
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(translated_rows, f, indent=2, ensure_ascii=False)




def main():
    #target_langs = ["nb"] #, "is"]
    target_langs = ["nb", "is"]
    source_dir = Path("ARC-V1-Feb2018-2/ARC-Challenge/")

    for lang in target_langs:
        out_dir = Path(f"data_arc")
        out_dir.mkdir(exist_ok=True)
        #for path in source_dir.glob(pattern="{dev,test,val}/**/*.csv"):
        for subset in ["dev", "test", "train"]:
            path = source_dir / f"ARC-Challenge-{subset.title()}.jsonl"
            rel_dir = path.relative_to(source_dir)
            output_path = out_dir / f"{lang}_{subset.replace('dev','validation')}.json"
            if output_path.exists():
                print("skipping", path, output_path)
            else:
                print(path, output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if lang == "is":
                    use_xml = False
                else:
                    use_xml = True
                translate_arc(path, output_path, lang, use_xml=use_xml, dryrun=False)

if __name__ == "__main__":
    main()
