from data import load_data, move_file_to_directory
import subprocess
import shutil


valid_queries = {
    "Unnecessary pass" : "../queries/unnecessary_path.ql",
    "Unreachable code" : "../queries/unreachable_code.ql",
    "Unused local variable" : "../queries/unused_local_variable.ql",
    "Unused import" : "../queries/unused_import.ql",
    "`__eq__` not overridden when adding attributes" : "../queries/eq_not_overriden.ql",
    "Module is imported more than once" : "../queries/module_import_more_than_once.ql",
    "Testing equality to None" : "../queries/equality_to_none.ql",
    "Variable defined multiple times" : "../queries/variable_defined_multiple.ql",
    "First argument to super() is not enclosing class" : "../queries/first_not_super.ql",
    "Comparison of identical values" : "../queries/cmp_identical_vals.ql",
}


def create_codeql_database(query_path):
    # Make a database from a single file
    query_path = move_file_to_directory(query_path)

    # Define the CodeQL command to create a database
    print("Creating database...")
    codeql_create_command = [
        "../codeql/codeql",
        "database",
        "create",
        "db",
        "--language=python",
        f"--source-root={query_path}"
    ]

    # Run the CodeQL command to create the database
    subprocess.run(codeql_create_command, stdout=subprocess.DEVNULL)


def run_codeql_query(query_filename):
    codeql_query_command = [
        "../codeql/codeql",
        "query",
        "run",
        "--database",
        "db",
        valid_queries[query_filename],
    ]

    print("Running query...")
    result = subprocess.run(codeql_query_command, capture_output=True, text=True)
    print(result.stdout)
    shutil.rmtree("db")
    shutil.rmtree("temp")


def main():
    dataset = load_data()
    # create_codeql_database(
    #    "../data/rcbops/glance-buildpackage/glance/tests/unit/test_db"
    # )
    # run_codeql_query("../queries/unused_import.ql")

    i = 0
    for row in dataset:
        create_codeql_database(row["code_file_path"])
        run_codeql_query(row["query_name"])
        # print("Question Name:", row["query_name"])
        # print("File Path:", row["code_file_path"])


if __name__ == "__main__":
    main()
