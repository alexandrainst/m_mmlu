from collections import Counter
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


def translate_hellaswag(jsonlpath: Path, output_path: PathLike, target_lang: str, dryrun=False, use_xml=True):

    translate_text = utils.get_translator(target_lang, dryrun)

    translated_rows = []
    with open(jsonlpath, "r") as f:
        for row in f:
            js = json.loads(row)

            # Translate context
            ctx_a = translate_text(js["ctx_a"])
            if use_xml:
                if len(js["ctx_b"]) > 0:
                    ctx_b = translate_text(js["ctx_b"], context=ctx_a)
                else:
                    ctx_b = ""
            else:
                if len(js["ctx_b"]) > 0:
                    ctx_b = translate_text(js["ctx_b"])
                else:
                    ctx_b = ""

            # Translate every ending given the context
            translated_endings = []
            for end in js["ending_options"]:
                if use_xml:
                    translated_endings.append(translate_text(end, context=js["ctx"]))
                else:
                    translated_endings.append(translate_text(end))

            output_dict = js
            output_dict["ctx_a"] = ctx_a
            output_dict["ctx_b"] = ctx_b
            output_dict["ctx"] = output_dict["ctx_a"] + " " + output_dict["ctx_b"]
            output_dict["ending_options"] = translated_endings

            translated_rows.append(output_dict)

        # Write to json in utf8 format
        with open(output_path, "w", encoding="utf8") as f:
            json.dump(translated_rows, f, indent=2, ensure_ascii=False)


def main():
    target_langs = ["nb", "is"]
    #target_langs = ["en"]
    source_dir = Path("hellaswag-train-dev/")

    for lang in target_langs:
        out_dir = Path(f"data_hellaswag")
        out_dir.mkdir(exist_ok=True)
        #for path in source_dir.glob(pattern="{dev,test,val}/**/*.csv"):
        for subset in ["valid"]:
            path = source_dir / f"{subset}.jsonl"
            output_path = out_dir / f"{lang}_{subset}.json"
            if output_path.exists():
                print("skipping", path, output_path)
            else:
                print(path, output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if lang == "is":
                    use_xml = False
                else:
                    use_xml = True
                translate_hellaswag(path, output_path, lang, use_xml=use_xml, dryrun=False)

if __name__ == "__main__":
    main()
