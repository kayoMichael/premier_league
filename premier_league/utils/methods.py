from typing import Union


def remove_duplicates(seq) -> list: return list(dict.fromkeys(seq))


def clean_xml_text(text: Union[str, list]) -> str:
    if isinstance(text, list):
        text = "".join(text)

    return text.strip().replace("\xa0", "")