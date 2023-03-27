import csv

import requests as requests
from bs4 import BeautifulSoup

import pandas as pd
import xlsxwriter

reader = csv.DictReader(open('Verb List.csv', newline='', encoding='utf-8'))

word_count = 0

verb_list = None
data_frame = None

headers = requests.utils.default_headers()
headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0', })


def search_all_verbs():
    global word_count

    global verb_list
    global data_frame

    verb_list = []

    for row in reader:
        find_all_tenses_for_one_verb(row['Français'])
        word_count += 1

    print("Total verbs: " + str(word_count))

    data_frame = pd.DataFrame(verb_list, columns=['0'] * 108)

    writer = pd.ExcelWriter('Temps En Français.xlsx', engine='xlsxwriter')
    data_frame.to_excel(writer, sheet_name='Temps En Français', index=False)

    writer.save()


def find_all_tenses_for_one_verb(verb):
    url = "https://conjugator.reverso.net/conjugation-french-verb-" + verb + ".html"

    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')

    termination_index = 0

    global word_count

    global verb_list

    print_all_verbs = False

    current_verb_list = []

    for div_element in soup.find_all("div", {"class": "blue-box-wrap"}):
        termination_index += 1

        item_count = 0

        long_version = False
        masculine = ""

        if termination_index > 13:
            break

        if termination_index == 4 or termination_index == 10 or termination_index == 11 or termination_index == 12:
            continue

        for tense_item in div_element.find_all("li"):
            content = ""

            for tense_subElement in tense_item.find_all():
                tense_item_string = str(tense_subElement.text)

                if tense_item_string == "":
                    item_count = 99
                    break
                else:
                    content += str(tense_subElement.text)

            item_count += 1

            if (not long_version and item_count > 6) or item_count > 8:
                break

            if termination_index != 9 and item_count == 3 or item_count == 7:
                if content[0:3] == "il/" or content[0:4] == "ils/":
                    current_verb_list.append(content)
                    current_verb_list.append(",")

                    if print_all_verbs:
                        print(content)
                else:
                    masculine = content

                    long_version = True
            elif termination_index != 9 and content[0:4] == "elle":
                content = masculine + "/" + content

                current_verb_list.append(content)
                current_verb_list.append(",")

                if print_all_verbs:
                    print(content)
            else:
                current_verb_list.append(content)
                current_verb_list.append(",")

                if print_all_verbs:
                    print(content)

    verb_list.append(current_verb_list)


search_all_verbs()
