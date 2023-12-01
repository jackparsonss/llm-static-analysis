# datset: https://huggingface.co/datasets/thepurpleowl/codequeries
import os
import datasets
from collections import defaultdict
import shutil

counter = defaultdict(int)
seen = set()

valid_queries = [
    "Unreachable code",
    "Unused local variable",
    "Unused import",
    "Module is imported more than once",
    "Comparison of identical values",
]


def filter(row):
    name = row["query_name"]
    is_valid = name in valid_queries


    if not is_valid or row["code_file_path"] == "saltstack/salt/salt/modules/lxc.py" or row["code_file_path"] == "pydata/pandas/pandas/stats/plm.py":
        return False

    # remove dups
    pair = (name, row["code_file_path"])
    if pair in seen:
        return False

    # limit to 3
    counter[name] += 1
    if counter[name] > 3:
        return False

    seen.add(pair)
    return True


def filter_data():
    ds = datasets.load_dataset(
        "thepurpleowl/codequeries", "twostep", split=datasets.Split.TEST
    )
    cols_to_remove = [
        "context_block",
        "answer_spans",
        "supporting_fact_spans",
        "example_type",
        "single_hop",
        "subtokenized_input_sequence",
        "label_sequence",
    ]
    ds = ds.remove_columns(cols_to_remove)

    ds = ds.filter(filter)
    ds.save_to_disk("./filtered_data")

    return ds


def load_data():
    ds = datasets.load_from_disk("./filtered_data")
    return iter(ds)


def move_file_to_directory(file_path):
    os.makedirs("./temp")
    shutil.copy("./data/" + file_path, "./temp")
    return "./temp"


if __name__ == "__main__":
    filter_data()
