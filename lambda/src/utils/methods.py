import csv
import json


def export_to_csv(file_name: str, data: list[list], data_2: list[list] = None, header: str = None, header_2: str = None):
    with open(f"tmp/{file_name}.csv", mode='w', newline='') as file:
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


def export_to_dict(data: list[list], data_2: list[list] = None, header_1: str = None, header_2: str = None):
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

    return json_data


def export_to_json(file_name: str, data: list[list], data_2: list[list] = None, header_1: str = None, header_2: str = None):
    json_data = export_to_dict(data, data_2, header_1, header_2)

    with open(f'tmp/{file_name}.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)