import json


def open_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as jsonFile:
            data = json.load(jsonFile)
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file '{file_path}'.")
        return []


def write_json_file(file_path, data):
    try:
        with open(file_path, 'w') as jsonFile:
            json.dump(data, jsonFile, indent=2)
    except json.JSONDecodeError:
        print(f"Error encoding JSON data to file '{file_path}'.")