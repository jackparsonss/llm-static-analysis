# datset: https://huggingface.co/datasets/thepurpleowl/codequeries
import datasets
from collections import defaultdict

counter = defaultdict(int)
seen = set()

valid_queries = [
    "Unnecessary pass",
    "Unreachable `except` block",
    "Unreachable code",
    "Unused import",
    "`__eq__` not overridden when adding attributes",
    "Module is imported more than once",
    "`break` or `return` statement in finally",
    "Unnecessary `else` clause in loop",
    "Use of `return` or `yield` outside a function",
    "`__init__` method returns a value",
]


def filter(row):
    name = row["query_name"]
    is_valid = name in valid_queries

    if not is_valid:
        return False

    # remove dups
    pair = (name, row["code_file_path"])
    if pair in seen:
        return False

    # limit to 5
    counter[name] += 1
    if counter[name] > 5:
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
    ds.save_to_disk("filtered_data")

    return ds


def load_data():
    ds = datasets.load_from_disk("filtered_data")
    return iter(ds)


if __name__ == "__main__":
    filter_data()
