from data import load_data, move_file_to_directory
import subprocess
import shutil
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

valid_queries = {
    "Unreachable code": "../queries/unreachable_code.ql",
    "Unused local variable": "../queries/unused_local_variable.ql",
    "Unused import": "../queries/unused_import.ql",
    "Module is imported more than once": "../queries/module_import_more_than_once.ql",
    "Comparison of identical values": "../queries/cmp_identical_vals.ql",
}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), organization=os.getenv("ORG_ID"))


def create_codeql_database(query_path):
    # Make a database from a single file
    path = move_file_to_directory(query_path)

    # Define the CodeQL command to create a database
    codeql_create_command = [
        "../codeql/codeql",
        "database",
        "create",
        "db",
        "--language=python",
        f"--source-root={path}",
    ]

    # Run the CodeQL command to create the database
    print("Creating database for file:", query_path)
    subprocess.run(codeql_create_command, stdout=subprocess.DEVNULL)
    print("Finished Creating Database\n\n")


def run_codeql_query(query_filename):
    query_file = valid_queries[query_filename]
    codeql_query_command = [
        "../codeql/codeql",
        "query",
        "run",
        "--database",
        "db",
        query_file,
    ]

    print("Running query: " + query_file, "on with type: " + query_filename)
    result = subprocess.run(codeql_query_command, capture_output=True, text=True)
    print("Finished Query.\n\n")
    print(result.stdout)

    # cleanup
    shutil.rmtree("db")
    shutil.rmtree("temp")


def main():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON.",
            },
            {"role": "user", "content": "Who won the world series in 2020?"},
        ],
    )

    print(response.choices[0].message.content)

    dataset = load_data()
    for row in dataset:
        if row["query_name"] == "`__eq__` not overridden when adding attributes":
            create_codeql_database(row["code_file_path"])
            run_codeql_query(row["query_name"])


if __name__ == "__main__":
    main()

