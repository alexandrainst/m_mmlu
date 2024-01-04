from typing import Callable

from deepl.translator import Translator
from greynir_client.client import translate_en_to_is
import unidecode

class DummyTranslator:
    def __init__(self):
        self.character_count = 0
    def translate_text(self, text):
        self.character_count += len(text)
        return text

def get_translator(target_lang, dryrun:bool = False) -> Callable:
    if dryrun:
        translator = DummyTranslator()
        translate_text = lambda x: translator.translate_text(x)
    else:
        if target_lang == "is":
            with open("greynir_apikey.txt", "r") as f:
                greynir_key = f.read().strip()
            translate_text = lambda x: translate_en_to_is(greynir_key, [unidecode.unidecode(x)]).translations[0]["translatedText"]
        else:
            with open("deepl_key.txt", "r") as key_file:
                auth_key = key_file.read().strip()
            translator = Translator(auth_key)
            translate_text = lambda x: translator.translate_text(x, source_lang="en", target_lang=target_lang, tag_handling="xml", preserve_formatting=True).text
    return translate_text
