import subprocess
import os
import sys
import argparse

parser = argparse.ArgumentParser(description="Sets up codeql")
parser.add_argument("--os", choices=["osx", "linux", "win"])
args = parser.parse_args()

zip_filename = f"codeql-{args.os}64.zip"


def download_data():
    if not os.path.exists("codeql"):
        print("Setting Up CodeQL...")
        subprocess.run(
            [
                "curl",
                "-LO",
                f"https://github.com/github/codeql-cli-binaries/releases/download/v2.15.3/{zip_filename}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        subprocess.run(["unzip", zip_filename])
        subprocess.run(["rm", zip_filename])

    if not os.path.exists("codeql"):
        print("Failed to setup CodeQL", file=sys.stderr)

        exit(1)

    print("CodeQL has been setup into codeql/")


if __name__ == "__main__":
    download_data()
