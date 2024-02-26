import csv
from pickle import GLOBAL
import random
import atexit

# useful alt code
# ç 0231
# ê 136
# é 130
# ó 162
# ô 0244
# á 0225
# â 0226
# ã 0227
# ú 163
YOU ARE SMELLY
FILE_LIST = [['VERBS', 'Verbs.csv'], ['VOCAB', 'Vocab.csv'],['ANSWERS','ANSWERS.csv']]
QUESTIONS_DATA_LIST = {'VOCAB': ['vocab', 'vorbs', 'vorbs_all'],
                       'VERBS': ['verbs', 'vorbs', 'verbs_all', 'past', 'present', 'future', 'vorbs_all']
                       }

PRONOUNS = ['Eu', 'Tu', 'Ele/Ela/Você', 'Nós', 'Vós', 'Eles/Elas/Vocês']

PAST_TENSE = {'er': ['o', 'es', 'e', 'emos', 'eis', 'em'],
              'ar': ['o', 'as', 'a', 'amos', 'ais', 'am'],
              'ir': ['o', 'is', 'i', 'imos', 'is', 'im']}

PRESENT_TENSE = {'er': ['o', 'es', 'e', 'emos', 'eis', 'em'],
                 'ar': ['o', 'as', 'a', 'amos', 'ais', 'am'],
                 'ir': ['o', 'is', 'i', 'imos', 'is', 'im']}

FUTURE_TENSE = {'er': ['o', 'es', 'e', 'emos', 'eis', 'em'],
                'ar': ['o', 'as', 'a', 'amos', 'ais', 'am'],
                'ir': ['o', 'is', 'i', 'imos', 'is', 'im']}


########################################################################
####    Startup Functions to get read and manipulate data into form ####
########################################################################

def get_csv_file(name) -> list:
    with open(name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data


def load_files() -> None:
    for tuple in FILE_LIST:
        file = get_csv_file(tuple[1])
        data = []
        for row in file:
            if tuple[0] in ['VERBS','VOCAB']:
                row['q_type'] = tuple[0]
                row['Root'] = f"{row['English'].lower()} | {row['Portuguese'].lower()}"
            else:
                row['Correct']= int(row['Correct'])
                row['Incorrect']= int(row['Incorrect'])
                row['Reason']= eval(row['Reason'])
            data.append(row)
        globals()[tuple[0]] = data


def add_conjugation(verb) -> str:
    if verb['Kind'] == 'Regular':
        v = verb['Portuguese']
        ending = v[-2:]
        root = v[:-2]
        verb['past'] = " ".join(
            [root + ending for ending in PAST_TENSE[ending]])
        verb['present'] = " ".join(
            [root + ending for ending in PRESENT_TENSE[ending]])
        verb['future'] = " ".join(
            [root + ending for ending in FUTURE_TENSE[ending]])
        return verb
    else:
        return verb


def conjugate_verbs() -> None:
    tmp = []
    global VERBS
    for verb in VERBS:
        res = add_conjugation(verb)
        tmp.append(res)
    VERBS = tmp


def set_default_batch() -> None:
    global VERB_MAX_BATCH
    global VOCAB_MAX_BATCH
    global DEFAULT_BATCH
    VERB_MAX_BATCH = 1 + int(max([(x['Batch']) for x in VERBS]))
    VOCAB_MAX_BATCH = 1 + int(max([(x['Batch']) for x in VOCAB]))
    DEFAULT_BATCH = {'VERBS': range(
        VERB_MAX_BATCH), 'VOCAB': range(VOCAB_MAX_BATCH)}

def exit_handler():
    with open('ANSWERS.csv', 'w') as f:
        # create the csv writer
        writer = csv.DictWriter(f,fieldnames=ANSWERS[0].keys())
        # write a row to the csv file
        writer.writeheader()
        writer.writerows(ANSWERS)

atexit.register(exit_handler)
#######################################################################
####    Functions to get the data set the questions are asked from ####
#######################################################################


def prune_data_set(qs: list, batch: dict, kind: str) -> list:
    if batch == DEFAULT_BATCH:
        return qs
    return [q for q in qs if int(q['Batch']) in batch[kind]]


def get_data_set(entry_name: str, batch: dict = {}) -> list:
    if {} == batch:
        batch = DEFAULT_BATCH
    questions = []
    for k in QUESTIONS_DATA_LIST.keys():
        if entry_name in QUESTIONS_DATA_LIST[k]:
            qs = globals()[k].copy()
            qs = prune_data_set(qs, batch, k)
            questions += qs
    random.shuffle(questions)
    return questions

def prune_correct_answers(base_questions):
    array = []
    for entry in base_questions:
        if any(entry['Root'] in k for k in ANSWERS):
            spread = 0 | entry['Correct'] - entry['Incorrect']
            spread = min(5,spread)
            if not random.randint(0, spread):
                array.append(entry)
        else:
            array.append(entry)
    if len(base_questions):
        return array
    
    else:
        return prune_correct_answers(base_questions)
     
debug_x = []
##########################################################################
####    Functions used to derive the question from the given data row ####
##########################################################################
def update_answer(kind: str,root:str,correct:bool):
    global debug_x
    debug_x = [kind,root,correct] 
    reason = kind if not correct else 'Correct'
    not_present = True
    for entry in ANSWERS:    
        if root == entry['Word']:
            entry['Correct']+= correct
            entry['Incorrect']+= not correct
            entry['Reason'].add(reason)
            not_present = False
            continue
    if not_present:
        ANSWERS.append({'Word':root,'Correct':0 | correct,'Incorrect':0 | (not correct),'Reason':set([reason])})

def get_answer(question: str) -> str:
    print(question)
    return input().lower()


def check_answer(question: str, answer: str, kind: str,root:str) -> None:
    user_answer = get_answer(question)
    answer=answer.lower()
    correct = user_answer == answer
    if correct:
        print(f"{kind}: Correct")
    else:
        print(f"{kind}: '{user_answer}' is wrong. \nCorrect {kind}: {answer}")
    
    if not kind == 'Definitive Article':
        update_answer(kind, root,correct)


def get_translation(q: dict, language_options: list) -> None:
    has_context = 'context' in q and bool(q['context'])
    if language_options[0] == 'Portuguese' and has_context:
        question_context = f"({q['context']})"
    else:
        question_context = ''
        
    check_answer(
        f"What is the {language_options[0]} of {q[language_options[1]]}{question_context}?", q[language_options[0]].split(' (')[0], 'Translation',q['Root'])

    if language_options[0] == 'English' and has_context:
        check_answer(
            "In what context?", q['context'], 'Context',q['Root'])


def do_some_conjugating(verb: dict, tense: str) -> list:
    print(f"Conjugate {verb['Portuguese']} in the {tense} tense")
    user_answer = []
    for pronoun in PRONOUNS:
        print(pronoun)
        user_answer.append(input().lower())
    correct_answer = list(map(str.lower, verb[tense].split()))
    correct = user_answer == correct_answer
    tense_correct = tense + " tense: " + \
        ["Incorrect", "Correct"][correct]
    if correct:
        return [tense_correct, []]
    else:
        zipped_answer = list(zip(['user'] + user_answer,
                             ['correct'] + correct_answer))
        return [tense_correct, zipped_answer]


def get_conjugation(verb: dict, question_area: list) -> list:
    if 'regular' == verb['Kind'] and not random.randint(0, 5):
        return []
    if question_area[0] in ['verbs_all', 'vorbs_all']:
        #question_area = ['past', 'present', 'future']
        question_area = [ 'present']
    return [do_some_conjugating(verb, area) for area in question_area]


def get_question_verb(q: dict, question_area: str) -> None:
    conjugation = get_conjugation(q, [question_area])
    for entry in conjugation:
        print(entry[0])
        for pair in entry[1]:
            if pair[0] != pair[1]:
                print(pair)

def get_word_ending(q:dict)->str:
    m,f=q['Masculine'],q['Feminine']
    if m and f:
        return random.choice(['Masculine','Feminine'])
    if m:
        return 'Masculine'
    if f:
        return 'Feminine'
    else:
        ''

def compose_word(q:dict)->dict:
    ending = get_word_ending(q)
    if ending: 
        q['English'] = f"{q['English']} ({ending})"
        q['Portuguese']=f"{q['Portuguese']}{q[ending]}"
        q['Article'] = q[ending]
    return q
    


def get_question(array: list, index: int, question_area: str) -> None:
    q = array[index].copy()
    language_options = ['English', 'Portuguese']
    random.shuffle(language_options)
    if q['q_type'] == 'VOCAB':
        q = compose_word(q)
    get_translation(q, language_options)
    if q['q_type'] == 'VERBS' and question_area not in ['verbs', 'vorbs']:
        get_question_verb(q, question_area)
    elif q['q_type'] == 'VOCAB':
        if q['Article'] and  random.randint(0,4):
            check_answer('What is the definitive article of the word?',
                     q['Article'], 'Definitive Article',q['Root'])


def quiz(questions: int = 1, question_area: str = 'present', batch: dict = {}) -> None:
    base_questions = get_data_set(question_area, batch)
    array = prune_correct_answers(base_questions)
    questions = min(questions+1, len(array))
    for index in range(0, questions):
        get_question(array, index, question_area)

def get_batch(verbs:list,vocab:list):
    return {'VERBS': verbs, 'VOCAB': vocab}

def vocab(questions: int = 10,batch: dict = {}):
    quiz(questions,'vocab',batch)

def verbs(questions: int = 10,kind:str = '',batch: dict = {}):
    if not kind:
        quiz(questions,'verbs',batch)
    else:
        quiz(questions,kind,batch)

def vorbs(questions: int = 10,kind:str = '',batch: dict = {}):
    quiz(questions,'vorbs_all',batch)



if __name__ == "__main__":
    load_files()
    conjugate_verbs()
    set_default_batch()