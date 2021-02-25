from updater.update_holocraft import load_data, emit_client_data


def main():
    # Load existing data
    data = load_data()
    emit_client_data(data)


if __name__ == "__main__":
    main()
