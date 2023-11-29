import subprocess
import os
import sys


def download_data():
    if not os.path.exists("data"):
        print("Downloading data...")
        subprocess.run(
            [
                "curl",
                "-LO",
                "files.srl.inf.ethz.ch/data/py150_files.tar.gz",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        subprocess.run(["tar", "-xzvf", "py150_files.tar.gz"])

        print("Unpacking Data...")
        subprocess.run(["tar", "-xzvf", "data.tar.gz"])

        subprocess.run(
            [
                "rm",
                "github_repos.txt",
                "py150_files.tar.gz",
                "python100k_train.txt",
                "python50k_eval.txt",
                "README.md",
                "data.tar.gz",
            ]
        )

    if not os.path.exists("data"):
        print("Failed to download data", file=sys.stderr)

        exit(1)

    print("Data has been dowloaded into data/")


if __name__ == "__main__":
    download_data()
