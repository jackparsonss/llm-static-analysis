from data import load_data, move_file_to_directory
import subprocess


def create_codeql_database(query_path):
    # Make a database from a single file
    query_path = move_file_to_directory(query_path)

    # Define the CodeQL command to create a database
    codeql_create_command = [
        "../codeql/codeql",
        "database",
        "create",
        "db",
        "--language=python",
        f"--source-root={query_path}",
    ]

    # Run the CodeQL command to create the database
    subprocess.run(codeql_create_command)


def run_codeql_query(query_filename):
    codeql_query_command = [
        "../codeql/codeql",
        "query",
        "run",
        "--database",
        "../src/db",
        query_filename,
    ]

    result = subprocess.run(codeql_query_command, capture_output=True, text=True)
    print(result.stdout)


def main():
    dataset = load_data()
    create_codeql_database(
        "../data/rcbops/glance-buildpackage/glance/tests/unit/test_db"
    )
    run_codeql_query("../queries/unused_import.ql")


if __name__ == "__main__":
    main()
