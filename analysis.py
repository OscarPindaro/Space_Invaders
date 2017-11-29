import csv
import sys
import json
import os

def get_average(data):
    return sum(d["score"] for d in data) / len(data)

def get_top(data):
    return sorted(data, key=lambda k: k["score"], reverse=True)[0]["score"]

def process_data(folder_path):
    processed_data = []
    generation = 0

    for data_file in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, data_file)
        with open(file_path, "r") as curr_file:
            curr_data = json.load(curr_file)

        processed_data.append(
            dict([("generation", generation), ("average", get_average(curr_data)), ("top", get_top(curr_data))]))

        generation += 1

    return processed_data

def write_csv(data, filename):
    keys = data[0].keys()

    with open(filename, "w") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main(argv):
    folder_path = "verboseDataRandom"
    csv_filename = "random.csv"

    processed_data = process_data(folder_path)
    write_csv(processed_data, csv_filename)
    print("done...")

if __name__ == "__main__":
    main(sys.argv)