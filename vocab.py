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
FILE_LIST = [['VERBS', 'Verbs.csv'], ['VOCAB', 'Vocab.csv'],['ANSWERS','ANSWERS.csv']]
QUESTIONS_DATA_LIST = {'VOCAB': ['vocab', 'vorbs', 'vorbs_all'],
                       'VERBS': ['verbs', 'vorbs', 'verbs_all', 'past', 'present', 'future', 'vorbs_all']
                       }

PRONOUNS = ['Eu', 'Tu', 'Ele/Ela/Você', 'Nós', 'Vós', 'Eles/Elas/Vocês']

### Past and future tense TBD correctly ###
PAST_TENSE = {'er': ['o', 'es', 'e', 'emos', 'eis', 'em'],
              'ar': ['o', 'as', 'a', 'amos', 'ais', 'am'],
              'ir': ['o', 'es', 'e', 'imos', 'is', 'im']}

PRESENT_TENSE = {'er': ['o', 'es', 'e', 'emos', 'eis', 'em'],
                 'ar': ['o', 'as', 'a', 'amos', 'ais', 'am'],
                 'ir': ['o', 'es', 'e', 'imos', 'is', 'em']}

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
    """
    Loads in the files in the Global var FILE_LIST while doing minor modfications to the date depending on source
    keeps the reason as a set data type once loaded in from csv
    """
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
                row['Reason']= eval(row['Reason']) # 
            data.append(row)
        globals()[tuple[0]] = data


def add_conjugation(verb) -> str:
    if verb['Kind'] == 'Regular':
        v = verb['Portuguese']
        ending = v[-2:] # Verb type eg er,ar,ir
        root = v[:-2]
        verb['past'] = " ".join(
            [root + ending for ending in PAST_TENSE[ending]])
        verb['present'] = " ".join(
            [root + ending for ending in PRESENT_TENSE[ending]])
        verb['future'] = " ".join(
            [root + ending for ending in FUTURE_TENSE[ending]])
    return verb


def conjugate_verbs() -> None:
    """
    conjugates all the verbs on load in so that it does not need to be done everytime a question is generated
    """ 
    tmp = []
    global VERBS
    for verb in VERBS:
        res = add_conjugation(verb)
        tmp.append(res)
    VERBS = tmp


def set_default_batch() -> None:
    """
    Batch here is just a number added to the csv indicating that the words were added at the same time
    This facilitates easier testing as we can generate the question space based off of newer or older batch numbers
    """ 
    global VERB_MAX_BATCH
    global VOCAB_MAX_BATCH
    global DEFAULT_BATCH
    VERB_MAX_BATCH = 1 + int(max([(x['Batch']) for x in VERBS]))
    VOCAB_MAX_BATCH = 1 + int(max([(x['Batch']) for x in VOCAB]))
    DEFAULT_BATCH = {'VERBS': range(
        VERB_MAX_BATCH), 'VOCAB': range(VOCAB_MAX_BATCH)}


def exit_handler():
    """
    Exit handler to keep track of what we got right/wrong this session
    """ 
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
            qs = globals()[k].copy() # ie VERBS or VOCAB
            qs = prune_data_set(qs, batch, k)
            questions += qs
    random.shuffle(questions)
    return questions


def prune_correct_answers(base_questions):
    """
    This function removes questions we get correct very often as we likely don't need to be tested on them as often
    Also takes into account incorrect answers as if we get something right only 70% of the time we should be tested on it more
    """ 
    array = []
    for entry in base_questions:
        if any(entry['Root'] in k for k in ANSWERS):
            spread = max(0,entry['Correct'] - entry['Incorrect'])
            spread = min(5,spread)
            if not random.randint(0, spread):
                array.append(entry)
        else:
            array.append(entry)
    if len(base_questions):
        return array
    
    else:
        return prune_correct_answers(base_questions)
     
##########################################################################
####    Functions used to derive the question from the given data row ####
##########################################################################
def update_answer(kind: str,root:str,correct:bool):
    """
    Updates the Answer dictionary to include the answer to the question just asked to help keep track of progress    
    """ 
    reason = kind if not correct else 'Correct'
    not_present = True
    for entry in ANSWERS:    
        if root == entry['Word']:
            entry['Correct']+= correct
            entry['Incorrect']+= not correct
            entry['Reason'].add(reason)
            not_present = False
    if not_present:
        ANSWERS.append({'Word':root,'Correct':int(correct),'Incorrect':int(not correct),'Reason':set([reason])})

def get_answer(question: str) -> str:
    """
    Asks given question and gets user answer
    """ 
    print(question)
    return input().lower()


def check_answer(question: str, answer: str, kind: str,root:str) -> None:
    """
    Checks answer user answer vs given answer and updates our answer dict
    It ignores the definitve article case because it isn't as relevant as getting the translation or conjugation wrong
    """ 
    user_answer = get_answer(question)
    answer=answer.lower()
    correct = user_answer == answer
    if correct:
        print(f"{kind}: Correct")
    else:
        print(f"{kind}: '{user_answer}' is wrong. \nCorrect {kind}: {answer}")
    
    if kind != 'Definitive Article':
        update_answer(kind, root,correct)


def get_translation(q: dict, language_options: list) -> None:
    """
    Generates question based on whether word being tested is in English or Portuguese 
    """ 
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
    """
    Generates questions + cprrect answers to ask the user in terms of verbs
    """ 
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
    """
    Triggers get_conjugation and prints to console what items were incorrect
    """ 
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
    return ''

def compose_word(q:dict)->dict:
    """
    Chooses what gender type of the word we will ask for this word
    """
    ending = get_word_ending(q)
    if ending: 
        q['English'] = f"{q['English']} ({ending})"
        q['Portuguese']=f"{q['Portuguese']}{q[ending]}"
        q['Article'] = q[ending]
    return q
    
def get_batch_dict(verbs:list,vocab:list):
    return {'VERBS': verbs, 'VOCAB': vocab}

def quiz_batch(question_area:str,number:int =0):
    """
    Creates the batch dictionary for the given batch numbers
    """
    if question_area == 'vorbs':
        return get_batch_dict([number],[number])
    elif question_area == 'verbs':
        return get_batch_dict([number],[])
    elif question_area == 'vocab':
        return get_batch_dict([],[number])
    else:
        print("Not a valid type")
        return {}

def get_question(array: list, index: int, question_area: str) -> None:
    """
    Asks for the translation of the given word
    If it is a verb and the question area is past/present/future it will ask for the conjugation of the verb in that tense
    Only asks the definitive article occassionally
    """
    q = array[index].copy()
    language_options = ['English', 'Portuguese']
    random.shuffle(language_options)
    if q['q_type'] == 'VOCAB':
        q = compose_word(q)
    get_translation(q, language_options)
    if q['q_type'] == 'VERBS' and question_area not in ['verbs', 'vorbs']:
        get_question_verb(q, question_area)
    elif q['q_type'] == 'VOCAB':
        if q['Article'] and  not random.randint(0,4):
            check_answer('What is the definitive article of the word?',
                     q['Article'], 'Definitive Article',q['Root'])


def quiz(questions: int = 1, question_area: str = 'vorbs', batch_number:int = None) -> None:
    """
    generates the question set and asks the questions that are generated
    """
    if batch_number:
        batch=quiz_batch(question_area,batch_number)
    else: 
        batch = {}
    base_questions = get_data_set(question_area, batch)
    array = prune_correct_answers(base_questions)
    questions = min(questions+1, len(array))
    for index in range(0, questions):
        get_question(array, index, question_area)


def vocab(questions: int = 10, batch_number:int = None):
    quiz(questions,'vocab',batch_number)

def verbs(questions: int = 10,tense:str = '', batch_number:int = None):
    if not tense:
        quiz(questions,'verbs',batch_number)
    else:
        quiz(questions,tense,batch_number)

def vorbs(questions: int = 10, batch_number:int = None):
    quiz(questions,'vorbs_all',batch_number)



if __name__ == "__main__":
    load_files()
    conjugate_verbs()
    set_default_batch()