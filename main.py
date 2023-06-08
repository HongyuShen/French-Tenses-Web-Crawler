import csv

import requests as requests
from bs4 import BeautifulSoup

import pandas as pd
import xlsxwriter

reader = csv.DictReader(open('Verb List.csv', newline='', encoding='utf-8'))

print_verb = True
print_all_tenses = False

word_count = 0

verb_list = None
data_frame = None

headers = requests.utils.default_headers()
headers.update({"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0', })


def search_all_verbs():
    global word_count

    global verb_list
    global data_frame

    verb_list = []

    for row in reader:
        find_all_tenses_for_one_verb(row['Français'])
        word_count += 1

    print("Total verbs: " + str(word_count))

    data_frame = pd.DataFrame(verb_list, columns=['0'] * 116)

    writer = pd.ExcelWriter('Temps En Français.xlsx', engine='xlsxwriter')
    data_frame.to_excel(writer, sheet_name='Temps En Français', index=False)

    writer._save()


def find_all_tenses_for_one_verb(verb):
    if print_verb:
        print(verb)

    url = "https://conjugator.reverso.net/conjugation-french-verb-" + verb + ".html"

    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')

    termination_index = 0

    participe_present_content = ""

    global word_count

    global verb_list

    current_verb_list = []

    for div_element in soup.find_all("div", {"class": "blue-box-wrap"}):
        termination_index += 1

        item_count = 0

        long_version = False
        separate_masculine_feminine = False
        masculine = ""

        no_imperatif_present = True
        imperatif_present_list = []

        if termination_index == 4 or termination_index == 7 or (
                9 < termination_index < 13) or termination_index == 15 or (
                16 < termination_index < 19):
            continue

        for tense_item in div_element.find_all("li"):
            if termination_index == 16:
                participe_present_content = tense_item.text
                break

            if (not long_version and item_count > 5) or (long_version and item_count > 8):
                break

            content = ""

            for tense_subElement in tense_item.find_all():
                tense_item_string = str(tense_subElement.text)

                if tense_item_string == "":
                    item_count = 99
                    break
                else:
                    content += str(tense_subElement.text)

            item_count += 1

            if termination_index == 9:
                current_verb_list.append(content)
                current_verb_list.append(",")

                if print_all_tenses:
                    print(content)
            elif termination_index == 19:
                no_imperatif_present = False

                imperatif_present_list.append(content)

                if print_all_tenses:
                    print(content)

                if item_count == 3:
                    for imperatif_present_list_index in range(3):
                        current_verb_list.insert(0, ",")
                        current_verb_list.insert(0, imperatif_present_list[2 - imperatif_present_list_index])

                    current_verb_list.insert(0, ",")
                    current_verb_list.insert(0, participe_present_content)

                    break
            else:
                if not separate_masculine_feminine:
                    if item_count == 3 and content[0:3] != "il/":
                        masculine = content
                        long_version = True
                        separate_masculine_feminine = True
                    elif item_count == 7 and content[0:4] != "ils/":
                        masculine = content
                        separate_masculine_feminine = True
                    else:
                        current_verb_list.append(content)
                        current_verb_list.append(",")

                        if print_all_tenses:
                            print(content)
                else:
                    separate_masculine_feminine = False

                    content = masculine + "/" + content

                    current_verb_list.append(content)
                    current_verb_list.append(",")

                    if print_all_tenses:
                        print(content)

        if termination_index == 19:
            if no_imperatif_present:
                for imperatif_present_list_index in range(3):
                    current_verb_list.insert(0, ",")
                    current_verb_list.insert(0, "N/A")

                current_verb_list.insert(0, ",")
                current_verb_list.insert(0, participe_present_content)

            break

    verb_list.append(current_verb_list)


search_all_verbs()
