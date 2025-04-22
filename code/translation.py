from translate import Translator


def translate_text(text: str, from_lang: str, to_lang) -> str:
    """Takes in an input string and a language and translates the string 
    into that langage.
    Language codes can be found at https://en.wikipedia.org/wiki/ISO_639-1"""
    translator = Translator(to_lang=to_lang, from_lang=from_lang)
    translation = translator.translate(text)

    return translation



print(translate_text("Hello, how are you doing?", "en", "fr"))