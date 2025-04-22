import csv
import json
import os
import re
from typing import Optional, Union


def remove_duplicates(seq) -> list:
    return list(dict.fromkeys(seq))


def clean_xml_text(text: Union[str, list]) -> str:
    if isinstance(text, list):
        text = "".join(text)

    return text.strip().replace("\xa0", "")


def is_float_string(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def require_dependency(pkg: str, extra: str):
    try:
        __import__(pkg)
    except ImportError:
        raise ImportError(
            f"Missing optional dependency '{pkg}'. Install it with:\n"
            f"    pip install premier_league[{extra}] \n Install all options with: \n "
            f"    pip install premier_league[all]"
        )


def remove_qualification_relegation_and_css(data, teams):
    potential_header = [
        "Pos",
        "Team",
        "Pld",
        "W",
        "D",
        "L",
        "GF",
        "GA",
        "GD",
        "Pts",
        "GAv",
        "GR",
        "GRA",
    ]
    result = []
    partition = []
    length = len(data)
    cycle = [
        "digit",
        "team",
        "digit",
        "digit",
        "digit",
        "digit",
        "digit",
        "digit",
        "+digit",
        "digit",
    ]
    header = []
    counter = 0
    index = 0
    for i in range(length):
        if data[i] in potential_header:
            header.append(data[i])
            index += 1
        if len(header) == 10:
            if header[8] != "GD":
                cycle[8] = "float"
            result.append(header)
            break
    for i in range(index, len(data)):
        if counter == 10:
            counter = 0
            result.append(partition)
            partition = []
        if cycle[counter] == "digit" and data[i].isdigit():
            partition.append(data[i])
            counter += 1
        elif cycle[counter] == "team" and data[i] in teams:
            partition.append(data[i])
            counter += 1
        elif cycle[counter] == "+digit" and re.match(r"[+\−\-]?\d+", data[i]):
            partition.append(data[i])
            counter += 1
        elif cycle[counter] == "float" and is_float_string(data[i]):
            partition.append(data[i])
            counter += 1

    # Final partition
    if len(partition) == 10:
        result.append(partition)
    return result


def export_to_csv(
    file_name: str,
    data: list[list],
    data_2: list[list] = None,
    header: str = None,
    header_2: str = None,
):
    os.makedirs("files", exist_ok=True)
    with open(f"files/{file_name}.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        if header:
            writer.writerow([header])
            writer.writerow([])
        writer.writerows(data)

        if data_2 and header_2:
            writer.writerow([])
            writer.writerow([header_2])
            writer.writerow([])
            writer.writerows(data_2)


def export_to_dict(
    data: list[list],
    data_2: Optional[list[list]] = None,
    header_1: Optional[str] = None,
    header_2: Optional[str] = None,
):
    keys = data[0]

    json_data = [dict(zip(keys, row)) for row in data[1:]]
    if header_1:
        json_data = {header_1: json_data}

    if data_2 and not header_2:
        raise ValueError("Header for the second data set is required.")
    elif data_2 and header_2:
        keys_2 = data_2[0]
        json_data_2 = [dict(zip(keys_2, row)) for row in data_2[1:]]
        json_data[header_2] = json_data_2

    return json_data


def export_to_json(
    file_name: str,
    data: list[list],
    data_2: list[list] = None,
    header_1: str = None,
    header_2: str = None,
):
    os.makedirs("files", exist_ok=True)
    json_data = export_to_dict(data, data_2, header_1, header_2)

    with open(f"files/{file_name}.json", "w") as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)


def extract_date_from_pattern(url, pattern):
    match = re.search(pattern, url)

    if match:
        month_name = match.group(1)
        day = match.group(2).zfill(2)
        year = match.group(3)

        month_dict = {
            "January": "01",
            "February": "02",
            "March": "03",
            "April": "04",
            "May": "05",
            "June": "06",
            "July": "07",
            "August": "08",
            "September": "09",
            "October": "10",
            "November": "11",
            "December": "12",
        }

        month = month_dict.get(month_name, "00")
        return f"{day}-{month}-{year}"

    return None


def extract_date_league_from_url(url):
    pattern = r"/(\d{4}-\d{4})/schedule/\d{4}-\d{4}-(\w+)-"

    match = re.search(pattern, url)
    if match:
        season = match.group(1)
        league = match.group(2)
        print(f"Season: {season}")
        print(f"League: {league}")

    if match:
        return match.group(1), match.group(2)

    return None, None
