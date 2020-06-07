import json


def update_db(current_state):
    completed_list = form_inverted_index(current_state)

    with open("reversed_index.txt", "r+") as file:
        file.write(json.dumps(completed_list))
        file.close()


def get_db():
    with open("reversed_index.txt", "r+") as file:
        current_state = file.read()
        json_out = json.loads(current_state)

        try:
            return json_out['words'], json_out['urls'], json_out['raw']
        except json.decoder.JSONDecodeError:
            file.close()
            return ""


def form_inverted_index(completed_list):
    final_form = {'urls': [], 'words': {}, 'raw': completed_list}

    for num, i in enumerate(completed_list.items()):
        final_form['urls'].append(i[0])

        for terms in i[1][0]:
            if terms[0] not in final_form['words']:
                final_form['words'][terms[0]] = []
                final_form['words'][terms[0]].append((num, terms[1]))
            else:
                final_form['words'][terms[0]].append((num, terms[1]))

    return final_form
