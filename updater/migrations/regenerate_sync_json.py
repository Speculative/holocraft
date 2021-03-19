from updater.update_holocraft import load_data, write_data


def main():
    # Load existing data
    data = load_data()
    write_data(data)


if __name__ == "__main__":
    main()
