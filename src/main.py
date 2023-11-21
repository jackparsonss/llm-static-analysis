from data import load_data
import subprocess


def create_codeql_database():
    # Define the CodeQL command to create a database
    # TODO: mv import.py -> import/import.py
    codeql_create_command = [
        "../codeql/codeql",
        "database",
        "create",
        "temp103",
        "--language=python",
        '--source-root=../data/rcbops/glance-buildpackage/glance/tests/unit/'
    ]

    # # Run the CodeQL command to create the database
    subprocess.run(codeql_create_command)


def run_codeql_query():
    # Define the CodeQL query file path
    codeql_query_file = "../queries/unused_import.ql"

    codeql_query_command = [
        "../codeql/codeql",
        "query",
        "run",
        "--database",
        "../src/temp103",
        codeql_query_file,
    ]
    result = subprocess.run(codeql_query_command, capture_output=True, text=True)
    print(result.stdout)

def main():
    dataset = load_data()

    dataset = next(dataset)
    print("Question Name:", dataset["query_name"])
    print("File Path:", dataset["code_file_path"])

    with open("../data/" + dataset["code_file_path"]) as file:
        create_codeql_database()
        run_codeql_query()


if __name__ == "__main__":
    main()
