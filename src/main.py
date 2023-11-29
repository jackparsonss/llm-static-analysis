from data import load_data, move_file_to_directory
import subprocess
import shutil
import difflib
from datetime import datetime
from gpt import query
import os

valid_queries = {
    "Unreachable code": "../queries/unreachable_code.ql",
    "Unused local variable": "../queries/unused_local_variable.ql",
    "Unused import": "../queries/unused_import.ql",
    "Module is imported more than once": "../queries/module_import_more_than_once.ql",
    "Comparison of identical values": "../queries/cmp_identical_vals.ql",
}


def make_date_folder(folder):
    current_datetime = datetime.now()
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    return "./" + datetime_str + "_" + folder


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
        relate to the problem. Name your output key of the JSON response 'modified_python_file' 
        and the value should be the python file, no nesting of JSON objects.
    """
    print("PROMPT:\n", prompt)

    print("Sending Prompt to LLM...")
    modified_python_file = query("gpt-3.5-turbo-1106", content, prompt)

    # Make directory to put new files
    output_folder = make_date_folder("output")
    original_filename = file_path.split("/")[-1]

    new_filepath = f"{output_folder}/{original_filename[0:-3]}"
    new_filename = new_filepath + f"/llm_{original_filename}"
    os.makedirs(new_filepath)

    # Write the modified python file to new directory
    with open(new_filename, "w") as edit_content_file:
        edit_content_file.write(modified_python_file)

    modified_python_file_content = read_file_content(new_filename)
    original_python_file_content = read_file_content(file_path)

    # Run Query to see if llm fixed problem
    create_codeql_database(new_filepath)
    results = run_codeql_query(query_name)

    # Copy original file into output folder
    shutil.copy(file_path, new_filepath)
    compare_content(modified_python_file_content, original_python_file_content)

    return results


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
