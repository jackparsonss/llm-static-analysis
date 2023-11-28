from data import load_data, move_file_to_directory
import subprocess
import shutil
from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken
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

def fix_codeql_problem():

    pass


def rank_llm_code():
    pass


def read_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content

def blabla(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.readlines()
    return content



def main():
    dataset = load_data()
    for row in dataset:
        if (row["code_file_path"] == "n9code/pylease/tests/test_ctxmgmt.py"):
            create_codeql_database(row["code_file_path"])
            run_codeql_query(row["query_name"])
            content = read_file_content("../data/" + row["code_file_path"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant designed to output JSON.",
                    },
                    {"role": "user", "content": 
                        '''The following input is a python file that I have ran a codeql
                            query against that contains an unused local variable static analysis
                            problem. Please do not touch anything that doesn't relate to this problem
                            and output the same python file with a fix that does not contain an unused local variable. 
                            name your output key of json response 'modified_python_file'
                        '''
                    },
                    {"role": "user", "content": content},
                ],
            )
            python_file_fix = json.loads(response.choices[0].message.content)["modified_python_file"]
            print(python_file_fix)
            original_content = blabla("../data/" + row["code_file_path"])
            with open("edit.py", "w") as edit_content_file:
                edit_content_file.write(python_file_fix)
            
            fix_content = blabla("edit.py")
            d = difflib.Differ()
            diff = d.compare(original_content, fix_content)

            print('\n'.join(diff))

        # print("-----------")
        # print("File: " + row["code_file_path"])
        # print("Query: " + row["query_name"])
        # file_content = read_file_content("../data/" +row["code_file_path"])
        # encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        # print("Requires: " + str(len(encoding.encode(file_content))) + " Tokens")
        # print("-----------")

if __name__ == "__main__":
    main()

