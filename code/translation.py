from translate import Translator


def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """Takes in an input string and a language and translates the string 
    into that langage.
    Language codes can be found at https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes"""
    translator = Translator(to_lang=to_lang, from_lang=from_lang)
    translation = translator.translate(text)

    # Remove any special character whitespace
    translation = translation.replace("\xa0", "")

    return translation
