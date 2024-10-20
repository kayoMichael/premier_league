from typing import Union
import csv
import json


def remove_duplicates(seq) -> list: return list(dict.fromkeys(seq))


def clean_xml_text(text: Union[str, list]) -> str:
    if isinstance(text, list):
        text = "".join(text)

    return text.strip().replace("\xa0", "")


def remove_qualification_and_relegation(data):
    result = []
    skip_next = False
    counter = 0

    for i, item in enumerate(data):
        if skip_next and not item.isdigit():
            skip_next = False
            continue
        skip_next = False

        if isinstance(item, str) and (item.startswith("Qualification") or item.startswith("Relegation")):
            skip_next = True
            continue
        if item == "(C)" or item == "(R)":
            continue

        if isinstance(item, str) and len(item) == 1 and not item.isdigit() and counter > 10:
            continue

        result.append(item)
        counter += 1

    return result


def export_to_csv(file_name: str, data: list[list], header: str = None):
    with open(f"{file_name}.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        if header:
            writer.writerow([header])
            writer.writerow([])
        writer.writerows(data)


def export_to_json(file_name: str, data: list[list], data_2: list[list] = None, header_1: str = None, header_2: str = None):
    keys = data[0]

    json_data = [dict(zip(keys, row)) for row in data[1:]]
    if header_1:
        json_data = {
            header_1: json_data
        }

    if data_2 and not header_2:
        raise ValueError("Header for the second data set is required.")
    elif data_2 and header_2:
        keys_2 = data_2[0]
        json_data_2 = [dict(zip(keys_2, row)) for row in data_2[1:]]
        json_data[header_2] = json_data_2

    with open(f'{file_name}.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)
