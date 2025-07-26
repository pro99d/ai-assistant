import wikipedia


def get_summary(content: str, lang: str="en"):
    wikipedia.set_lang(lang)
    return wikipedia.summary(content)
