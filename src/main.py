from data import load_data


def main():
    dataset = load_data()

    for value in dataset:
        print("Question Name:", value["query_name"])
        print("File Path:", value["code_file_path"])


if __name__ == "__main__":
    main()
