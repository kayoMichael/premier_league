from typing import Union


def remove_duplicates(seq) -> list: return list(dict.fromkeys(seq))


def clean_xml_text(text: Union[str, list]) -> str:
    if isinstance(text, list):
        text = "".join(text)

    return text.strip().replace("\xa0", "")


def remove_qualification_and_relegation(data):
    result = []
    skip_next = False

    for i, item in enumerate(data):
        if skip_next and not item.isdigit():
            skip_next = False
            continue
        skip_next = False

        if isinstance(item, str) and (item.startswith("Qualification") or item.startswith("Relegation")):
            skip_next = True
            continue

        result.append(item)

    return result