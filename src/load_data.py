# datset: https://huggingface.co/datasets/thepurpleowl/codequeries
import datasets


def load_data():
    ds = datasets.load_dataset(
        "thepurpleowl/codequeries", "twostep", split=datasets.Split.TEST
    )

    return iter(ds)
