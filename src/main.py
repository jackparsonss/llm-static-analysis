from data import load_data


def main():
    dataset = load_data()

    dataset = next(dataset)
    print("Question Name:", dataset["query_name"])
    print("File Path:", dataset["code_file_path"])

    with open("data/" + dataset["code_file_path"]) as file:
        print(file.readlines())


if __name__ == "__main__":
    main()
