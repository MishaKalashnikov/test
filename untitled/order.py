def process_twitch_links(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        processed_lines = [line.strip().replace("https://www.twitch.tv/", "") for line in lines]

        with open(filename, 'w', encoding='utf-8') as file:
            file.write("\n".join(processed_lines))

        print("Файл успешно обработан!")
    except FileNotFoundError:
        print("Ошибка: Файл не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Укажите имя вашего файла
filename = "filtered_streams.txt"
process_twitch_links(filename)