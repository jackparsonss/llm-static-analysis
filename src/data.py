# datset: https://huggingface.co/datasets/thepurpleowl/codequeries
import datasets

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


def filter_data():
    ds = datasets.load_dataset(
        "thepurpleowl/codequeries", "twostep", split=datasets.Split.TRAIN
    )

    ds = ds.filter(lambda row: row["query_name"] in valid_queries)
    ds.save_to_disk("filtered_data")

    return ds


def load_data():
    ds = datasets.load_from_disk("filtered_data")
    return iter(ds)


if __name__ == "__main__":
    filter_data()
