import os

import deepl

# dangerous, remove later
try:
    auth_key = os.environ['DEEPL_API_KEY']
    translator = deepl.Translator(auth_key)
except:
    pass


def translate(input: str, targetLang: str):
    return str(translator.translate_text(input, target_lang=targetLang))
