# local imports
from data import load_data, move_file_to_directory
from gpt import query
from gpt import rank

# stdlib imports
import subprocess
import argparse
import shutil
import difflib
from datetime import datetime
import os

arg_mapping = {"gpt-3.5": "gpt-3.5-turbo-1106", "gpt-4": "gpt-4-1106-preview"}

parser = argparse.ArgumentParser(description="Static Analsyis With LLMs")

parser.add_argument("--test_llm", choices=["gpt-3.5", "gpt-4"])
parser.add_argument("--rank_llm", choices=["gpt-3.5", "gpt-4"])
args = parser.parse_args()

valid_queries = {
    "Unreachable code": "./queries/unreachable_code.ql",
    "Unused local variable": "./queries/unused_local_variable.ql",
    "Unused import": "./queries/unused_import.ql",
    "Module is imported more than once": "./queries/module_import_more_than_once.ql",
    "Comparison of identical values": "./queries/cmp_identical_vals.ql",
}

query_descriptions = {
    "Unused import": """
        A module is imported (using the import statement) 
        but that module is never used. This creates a dependency 
        that does not need to exist and makes the code more difficult to read.
        """,
    "Unused local variable": """
        A local variable is defined (by an assignment) but never used.
        It is sometimes necessary to have a variable which is not used. 
        These unused variables should have distinctive names, to make it 
        clear to readers of the code that they are deliberately not used. 
        The most common conventions for indicating this are to name the variable _ 
        or to start the name of the variable with unused or _unused.

        The query accepts the following names for variables that are intended to be unused:
        - Any name consisting entirely of underscores.
        - Any name containing unused.
        - The names dummy or empty.
        - Any “special” name of the form __xxx__. Variables that are defined in a group, 
          for example x, y = func() are handled collectively. If they are all unused, then 
          this is reported. Otherwise they are all treated as used.
        """,
    "Unreachable code": """
        Unreachable code makes the code more difficult to understand and may slow down loading of 
        modules.
        """,
    "Module is imported more than once": """
        Importing the same module more than once has no effect as each module is only loaded once. 
        It also confuses readers of the code.
        """,
    "Comparison of identical values": """
        When two identical expressions are compared it is typically an indication of a mistake, 
        since the Boolean value of the comparison will always be the same, 
        unless the value is the floating point value float('nan').
        """,
}

query_recommendations = {
    "Unused import": """
        Delete the import statement.
        """,
    "Unused local variable": """
        If the variable is included for documentation purposes or is otherwise intentionally unused, 
        then change its name to indicate that it is unused, otherwise delete the assignment 
        (taking care not to delete right hand side if it has side effects).
        """,
    "Unreachable code": """
        Deleting the unreachable code will make the code clearer and preserve the meaning of the code. 
        However, it is possible that the original intention was that the code should execute and that 
        it is unreachable signifies some other error.
        """,
    "Module is imported more than once": """
        Remove the second import.
        """,
    "Comparison of identical values": """
        It is not good practice to compare a value with itself, as it makes the code hard to read and can 
        hide errors with classes that do not correctly implement equality. If testing whether a 
        floating-point value is not-a-number, then use math.isnan(). If the value may be a complex number, 
        then use cmath.isnan() instead.
        """,
}


def make_date_folder(folder):
    current_datetime = datetime.now()
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    return "./" + datetime_str + "_" + folder


output_folder = make_date_folder("output")


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
    print(query_file)
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


def rank_llm_output(
    file_path, file_path_original, file_path_modified, query_name, codeql_results
):
    with open(file_path_original, "r", encoding="utf-8") as file:
        original_file = file.read()
    with open(file_path_modified, "r", encoding="utf-8") as file:
        modified_file = file.read()

    prompt = f"""
    You are an expert developer. You are verifying the code generated by LLM to fix the warning
    titled {query_name} which has the following description:
    \n{query_descriptions[query_name]}\n

    The recommended ways to fix this code flagged for this warning are
    \n{query_recommendations[query_name]}


    Score 0, if the patch has changes unrelated and unnecessary to fixing the warning (Strong Reject).
    Score 1, if the patch has a few correct fixes, but still modifies the original snippet unnecessarily (Weak Reject).
    Score 2, if the patch has mostly correct fixes but is still not ideal (Weak Accept).
    Score 3, if the patch only makes edits that fix the warning with least impact on any unrelated
    segments of the original snippet (Strong Accept).
    If you find additions or deletions of code snippets that are unrelated to the desired fixes (think
    LLM hallucinations), it can be categorically scored 0 (Strong Reject). That said, you can make
    exceptions in very specific cases where you are sure that the additions or deletions do not alter
    the functional correctness of the code, as outlined next.
    Allowed Exceptions:
    The following (unrelated) code changes in the diff file can be considered okay and need not
    come in the way of labeling an otherwise correct code change as accept (score 2 or 3). This list
    is not exhaustive, but you should get the idea
    (a) deleting comments is okay,
    (b) rewriting a = a + 1 as a += 1 is okay, even though it may not have anything to do with
    the warning of interest,
    (c) making version specific changes is okay, say changing print ("hello") to print "hello".
    The following (unrelated) code changes in the diff file are NOT considered okay, and you
    should label the diff file as reject (score 0 or 1) even if it is otherwise correct for the query.
    This list is not exhaustive, but you should get the idea
    (a) deleting or adding a print statement,
    (b) optimizing a computation,
    (c) changing variable names or introducing typos.
    The following is the original file and the modified file with the fix to the problem.
    Output only the reason and score for the patch below. Do not output anything else.
    Name your output key of the JSON response 'ranking' and the value should be a string
    """

    print("PROMPT:\n", prompt)
    print("Sending Prompt to LLM...")

    ranking = rank(arg_mapping[args.test_llm], original_file, modified_file, prompt)
    # write output to filepath .txt
    with open(file_path + "ranking.txt", "w", encoding="utf-8") as file:
        file.write(ranking)


def fix_codeql_problem(file_path, query_name, codeql_results):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # STILL NEED TO MAYBE GIVE IT LINES OF INTEREST??
    prompt = f"""
        We are fixing code that has been flagged for the CodeQL warning titled "{query_name}" 
        which has the following description: \n {query_descriptions[query_name]} \n
        
        The recommended way to fix code flagged by this warning is \n {query_recommendations[query_name]} \n

        Modify the Buggy code below to fix the CodeQL warning(s). Output the entire code block
        with appropriate changes. Do not remove any section of the code unrelated to the desired fix.

        The CodeQL warning(s) for the buggy code is: \n {codeql_results} \n

        The following input is the Python file containing the buggy code.

        Name your output key of the JSON response 'modified_python_file' and the value should be the 
        python file, no nesting of JSON objects. Ensure that the output follows the same formatting 
        and indentation conventions as the input code.
    """
    print("PROMPT:\n", prompt)

    print("Sending Prompt to LLM...")
    modified_python_file = query(arg_mapping[args.test_llm], content, prompt)

    # Make directory to put new files
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
    original_filename = shutil.copy(file_path, new_filepath)

    rank_llm_output(
        new_filepath, original_filename, new_filename, query_name, codeql_results
    )

    compare_content(
        modified_python_file_content, original_python_file_content, new_filepath
    )

    return results


def compare_content(original_content, modified_content, file_path):
    d = difflib.Differ()
    diff = d.compare(original_content, modified_content)
    difference = "\n".join(diff)
    with open(file_path + "difference.txt", "w", encoding="utf-8") as file:
        file.write(difference)


def read_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.readlines()
    return content


def main():
    dataset = load_data()
    for row in dataset:
        # if row["code_file_path"] == "rcbops/glance-buildpackage/glance/tests/unit/test_db.py":
        create_codeql_database(move_file_to_directory(row["code_file_path"]))

        results = run_codeql_query(row["query_name"])
        shutil.rmtree("./temp")

        fix_codeql_problem(
            "./data/" + row["code_file_path"], row["query_name"], results
        )


if __name__ == "__main__":
    main()
