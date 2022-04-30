import csv
import requests
import sys
import os
import json
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import PySimpleGUI as sg

FILE_NAME = "currencies22.csv"
WEBSITE   = "https://coinmarketcap.com"

def parse_api():
    parameters = {
        "start": "1",
        "limit": "25",
        "convert": 'USD'
    }

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "41aad901-cad5-4596-854f-a69a6833b3c3"
    }

    data = []

    try:
        response = requests.get(url="https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest", headers=headers, params=parameters)

        file = json.loads(response.text)

        for element in file["data"]:
            item = {
                "name": element["name"],
                "market_cap": element["quote"]["USD"]["market_cap"],
                "price": element["quote"]["USD"]["price"]
            }
            
            data.append(item)

    except(ConnectionError, Timeout, TooManyRedirects) as exp:
        print("Ошибка!", exp)
        sys.exit(1)

    return data

def parse_website():
    data = []

    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.132 YaBrowser/22.3.1.892 Yowser/2.5 Safari/537.36"
    }

    try:
        response = requests.get(url=WEBSITE, headers=headers)

        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.find("tbody")

        names = table.find_all("p", class_="sc-1eb5slv-0 iworPT")
        market_caps = table.find_all("span", class_="sc-1ow4cwt-1 ieFnWP")
        prices = table.find_all("div", class_="sc-131di3y-0 cLgOOr")

        for i in range(len(names)):
            item = {
                "name": names[i].text,
                "market_cap": market_caps[i].text,
                "price": prices[i].text
            }

            data.append(item)
    
    except(ConnectionError, Timeout, TooManyRedirects) as exp:
        print("Ошибка!", exp)
        sys.exit(1)

    return data

def parse_file():
    data = []

    try:
        file = open(FILE_NAME, 'r')
        table = csv.reader(file, delimiter=';')

        for element in table:
            item = {
                "name": element[0],
                "market_cap": element[1],
                "price": element[2]
            }

            data.append(item)

        file.close()

    except FileNotFoundError:
        print("Ошибка! Не удалось открыть файл '{}'.".format(FILE_NAME))
        sys.exit(1)

    return data

def find(data, key):
    find_items = []

    for item in data:
        if item.get("name").lower().startswith(key.lower()):
            find_items.append(item)

    return find_items

def print_data(data):
    table = PrettyTable()

    table.field_names = ["Наименование", "Рыночная капитализация", "Стоимость 1 ед. в долларах"]

    for element in data:
        table.add_row([element["name"], element["market_cap"], element["price"]])

    print(table)

def create_data_for_gui_table(data):
    new_data = []

    for i in data:
        new_data.append([i["name"], i["market_cap"], i["price"]])

    return new_data

def gui():
    data = []

    frame_1 = [
        [sg.Text("Выберите режим считывания данных:")],
        [sg.Button("1. Файл '{}'.".format(FILE_NAME))],
        [sg.Button("2. Веб-сайт '{}'.".format(WEBSITE))],
        [sg.Button("3. С использованием API.")],
        [sg.Text("Поиск:")],
        [sg.Input("Введите название криптовалюты"), sg.Button("Найти", size=(4,1))]
    ]

    headings = ["Наименование", "Рыночная капитализация", "Стоимость 1 ед. в долларах"]

    frame_2 = [
        [sg.Text("Информация о криптовалюте:")],
        [sg.Table(values=data, headings=headings, key="TABLE", size=(400, 420))]
    ]

    layout = [
        [sg.Column(frame_1), sg.Column(frame_2)]
    ]

    window = sg.Window("CoinMarketCap парсер", layout, size=(1280, 520))

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break
        if event == "1. Файл 'currencies22.csv'.":
            data = parse_file()
            gui_data = create_data_for_gui_table(data)
        if event == "2. Веб-сайт 'https://coinmarketcap.com'.":
            data = parse_website()
            gui_data = create_data_for_gui_table(data)
        if event == "3. С использованием API.":
            data = parse_api()
            gui_data = create_data_for_gui_table(data)
        if event == "Найти":
            data = find(data, values[0])
            gui_data = create_data_for_gui_table(data)

        window["TABLE"].update(values=gui_data)

    window.close()
    
def console():
    data = []

    print("Выберите режим считывания данных:")
    print("1. Файл '{}'.".format(FILE_NAME))
    print("2. Веб-сайт '{}'.".format(WEBSITE))
    print("3. С использованием API.")

    while True:
        choice = input("> ")

        if choice not in ['1', '2', '3']:
            print("Ошибка! Введено некоректное значение.")
            print("Пожалуйста, попробуйте снова.")
        else:
            break
    
    os.system("cls")
    
    if choice == '1':
        data = parse_file()
    elif choice == '2':
        data = parse_website()
    else:
        data = parse_api()

    print_data(data)

    print("1. Поиск криптовалюты по названию.")
    print("2. Выход из приложения.")

    while True:
        choice = input("> ")

        if choice not in ['1', '2']:
            print("Ошибка! Введено некоректное значение.")
            print("Пожалуйста, попробуйте снова.")
        else:
            break

    if choice == '1':
        print("Введите ключ поиска")
        key = input("> ")
  
        find_data = find(data, key)

        if len(find_data) == 0:
            print("По Вашему запросу ничего не найдено.")
        else:
            print("По Вашему запросу найдено:")
            print_data(find_data)
    else:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("coinmarketcap парсер - выполненное задание на учебную практику СибГУТИ 2022")
        print("Работу выполнил: студент 2 курса ИП-016 Егошин А.А.")
        print("Запуск: python main.py --mode (-m) console / gui")
        
    else:
        if len(sys.argv) < 3:
            print("Ошибка! Параметров, необходимых для запуска мало.")
            print("Возможно, Вы не указали режим в котором хотите запустить программу.")
            print("Пожалуйста, проверьте и попробуйте снова.")
            sys.exit(1)
        
        if len(sys.argv) > 3:
            print("Ошибка! Параметров, необходимых для запуска много.")
            print("Пожалуйста, удалите лишние и попробуйте снова.")
            sys.exit(1)

        parameter_name = sys.argv[1]
        parameter_value = sys.argv[2]

        if (parameter_name == "--mode" or parameter_name == "-m"):
            if (parameter_value == "console"):
                console()

            elif (parameter_value == "gui"):
                gui()
            else:
                print("Ошибка! Неверное значение параметра mode.")
                print("Пожалуйста, проверьте правильность выбора режима и попробуйте снова.")
                sys.exit(1)
        else:
            print("Ошибка! Неизвестный параметр {}".format(parameter_value))
            print("Пожалуйста, проверьте корректность ввода и попробуйте снова.")
            sys.exit(1)