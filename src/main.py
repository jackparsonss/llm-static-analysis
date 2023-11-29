from data import load_data, move_file_to_directory
import subprocess
import shutil
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import difflib

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
    # Define the CodeQL command to create a database
    codeql_create_command = [
        "./codeql/codeql",
        "database",
        "create",
        "db",
        "--language=python",
        f"--source-root={query_path}",
    ]

    # Run the CodeQL command to create the database
    print("Creating database for file:", query_path)
    subprocess.run(codeql_create_command, stdout=subprocess.DEVNULL)
    print("Finished Creating Database\n\n")


def run_codeql_query(query_filename):
    query_file = valid_queries[query_filename]
    codeql_query_command = [
        "./codeql/codeql",
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

    return result.stdout


def rank_llm_output():
    pass


def fix_codeql_problem(file_path, query_name, codeql_results):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    prompt = f"""
        The following input is a python file that I have run a codeql query against
        that checks for {query_name}. This query returned this as the results \n
        {codeql_results}\n Your task is to take this codeql results alongside the type 
        of static analysis query I've run and fix this problem in the code. Do not modify,
        refactor, or change any code that does not directly relate to the issue. Retain all logic
        and output as is, do not rewrite any code even if it looks cleaner. Basically think of
        yourself as an intern developer at a big technology company, you found the problem
        and you don't want to break anything else so your only fixing the lines that directly
        relate to the problem. Name your output key of the JSON response 'modified_python_file'.
    """
    print("PROMPT:\n", prompt)

    print("Sending Prompt to LLM...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON.",
            },
            {"role": "user", "content": prompt},
            {"role": "user", "content": content},
        ],
    )

    # Write the modified python file to edit.py
    modified_python_file = json.loads(response.choices[0].message.content)[
        "modified_python_file"
    ]
    with open("./edit/edit.py", "w") as edit_content_file:
        edit_content_file.write(modified_python_file)

    modified_python_file_content = read_file_content("./edit/edit.py")
    original_python_file_content = read_file_content(file_path)

    # Stick it in seperate folders -> Maybe have folder structure thats not just edit/edit.py

    # Run Query to see if llm fixed problem
    create_codeql_database("./edit")
    results = run_codeql_query(query_name)

    compare_content(modified_python_file_content, original_python_file_content)


def compare_content(original_content, modified_content):
    d = difflib.Differ()
    diff = d.compare(original_content, modified_content)
    print("\n".join(diff))


def read_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.readlines()
    return content


def main():
    dataset = load_data()
    for row in dataset:
        if row["code_file_path"] == "n9code/pylease/tests/test_ctxmgmt.py":
            create_codeql_database(move_file_to_directory(row["code_file_path"]))

            results = run_codeql_query(row["query_name"])
            shutil.rmtree("./temp")

            fix_codeql_problem(
                "./data/" + row["code_file_path"], row["query_name"], results
            )


if __name__ == "__main__":
    main()
