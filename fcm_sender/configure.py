CONFIG_FILENAME = 'config'


def prompt_configuration():
    api_key = raw_input('Enter the Firebase server key: ')
    sender_id = raw_input('Set this sender identifier: ')

    return api_key, sender_id


def persist_configuration(api_key, sender_id):
    with open(CONFIG_FILENAME, 'w') as config_file:
        config_file.write(api_key)
        config_file.write('\0')
        config_file.write(sender_id)


def main():
    (api_key, sender_id) = prompt_configuration()
    persist_configuration(api_key, sender_id)


if __name__ == '__main__':
    main()
