#!/usr/local/miniconda3/envs/flashcard/bin/python
from __future__ import division

import sys
import time
import re
import os
import random
import datetime
from shutil import copyfile
import csv
import yaml

from contextlib import contextmanager

FLASHCARDS_ATTEMPTS_DIR = None
FLASHCARDS_DIR = None
TIME_LIMIT = None
NUM_QUESTIONS = None

def set_variables(time_limit, num_questions):
    global FLASHCARDS_ATTEMPTS_DIR
    global FLASHCARDS_DIR
    global TIME_LIMIT
    global NUM_QUESTIONS

    user_profile_file = os.path.join(os.getenv('HOME', ''),
            '.flashcardexam.conf')
    profile = read_user_profile(user_profile_file)

    for var in ['FLASHCARDS_ATTEMPTS_DIR',
            'FLASHCARDS_DIR', 'TIME_LIMIT', 'NUM_QUESTIONS']:
        globals()[var] = (locals().get(var.lower())
                or os.getenv(var)
                or profile.get(var)
                or sys.exit(['Undefined variable {}'.format(var)]))

    NUM_QUESTIONS = int(NUM_QUESTIONS)
    TIME_LIMIT = int(TIME_LIMIT)
    assert isinstance(TIME_LIMIT, int)

    pass

def read_user_profile(user_profile_file):
    with open(user_profile_file) as fd:
        profile = yaml.load(fd)
        return profile


@contextmanager
def clock_this():
    d = {'start': datetime.datetime.now()}
    yield d
    d['end'] = datetime.datetime.now()
    d['seconds'] = (d['end'] - d['start']).seconds


def make_out_filename(out_dir, source_filename, card_type, card_id,
        out_file_format):
    ''' card_type is 'question' or 'answer' ... 0 or 1.
    '''
    source_filename_base = source_filename.split('.')[0]

    card_type_num = {'question': 0, 'answer': 1}.get(card_type)
    return os.path.join(out_dir,
            '{}-{}-{}.{}'.format(
                card_id,
                card_type_num,
                source_filename_base,
                out_file_format))


def make_card_id(number, char_num):
    return str(number).zfill(char_num)


def make_session_id():
    now = datetime.datetime.now()
    session_id = now.strftime('%Y-%m-%dT%H%M')

    # Make new session dir.
    attemptsdir = FLASHCARDS_ATTEMPTS_DIR
    path = os.path.join(attemptsdir, session_id)
    os.mkdir(path)

    return session_id


def format_flash_card_files(source_dir, out_dir, next_card_id, dry_run=True):
    ''' Take a source of flashcards, letting them be the "answers",
    and use the format

    <card id>-0-<description>.<txt/png>  => question card
    <card id>-1-<description>.<txt/png>  => answer card


    next_card_id: the next valid <card id> which can be used to output into <out_dir>.
    '''

    for root, dirs, files in os.walk(source_dir):
        for i, source_filename in enumerate(files):

            card_id = make_card_id(int(next_card_id) + i, char_num=3)

            #
            (source_filename_base,
            source_filename_file_type) = source_filename.split('.')

            # write new question file
            outfilename_question = make_out_filename(
                out_dir,
                source_filename_base,
                card_type='question',
                card_id=card_id,
                out_file_format='txt')

            content = source_filename_base

            if dry_run:
                print 'writing outfile question: ', outfilename_question
            else:
                with open(outfilename_question, 'w') as fd:
                    fd.write(content)


            # write new answer file
            outfilename_answer = make_out_filename(
                out_dir,
                source_filename_base,
                card_type='answer',
                card_id=card_id,
                out_file_format=source_filename_file_type)

            source_file_path = os.path.join(
                    root,
                    source_filename)

            if dry_run:
                print 'writing outfile answer', outfilename_answer
            else:
                copyfile(
                        source_file_path,
                        outfilename_answer) 


def get_all_files(sourcedir):
    badfile = '.DS_Store'
    all_files = os.listdir(sourcedir)

    if badfile in all_files:
        all_files.pop(all_files.index(badfile))
    return all_files


def question_match(filename):
    try:
        return re.match(r'\d{2,}-(\d)-.*txt', filename).groups()[0] == '0'
    except AttributeError:
        return False


def only_question_files(all_files):
    question_files = [filename for filename in all_files
            if question_match(filename)]
    return question_files


def sample(thelist, n):
    return [thelist[i] for i in sorted(random.sample(xrange(len(thelist)), n))]


def select_random_question_cards(source_dir, how_many):
    all_files = get_all_files(source_dir)
    question_files = only_question_files(all_files)

    # Random sample.
    sampled_question_files = sample(question_files, how_many)
    return sampled_question_files


def write_attempt(outfile, myanswer):
    outpath = os.path.join(FLASHCARDS_ATTEMPTS_DIR, outfile)
    with open(outpath, 'w') as fd:
        fd.write(myanswer)


def get_question(question_filename):
    path = os.path.join(FLASHCARDS_DIR, question_filename)
    with open(path) as fd:
        content = fd.read()

    return content


def filename_in_attempts_dir(session_id, filename):
    attemptsdir = FLASHCARDS_ATTEMPTS_DIR
    path = os.path.join(attemptsdir, session_id, filename)
    return path


def store_answer(session_id, question_id, answer):
    path = filename_in_attempts_dir(
            session_id,
            question_id + '.txt')
    with open(path, 'w') as fd:
        fd.write(answer)


def collect_answer():
    answer = raw_input('> ')
    fullanswer = ''
    while answer != '--':
        fullanswer += answer + '\n'
        answer = raw_input()
    return fullanswer


def write_csv(path, table):
    with open(path, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile,
                                quotechar=',',
                                quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(table)


def test_write_csv():
    rows = [
            [
                'session_id', 'question_id', 'time_taken', 'points', 'explanation'],
            ['2017-11-26T1124','043-0-Chi-Squared_For_Feature_Selection','0:00','0',''],
            ['2017-11-26T1124','044-0-Chi-Squared','0:00','0',''],
            ['2017-11-26T1124','072-0-Dropout','0:00','0',''],
            ['2017-11-26T1124','085-0-Extrema','0:00','0',''],
            ['2017-11-26T1124','238-0-ReLU_Activation_Function','0:00','0',''],
            ]
    write_csv('blah.csv', rows)


def make_scores_file(session_id, sampled_question_filenames, times):
    path = filename_in_attempts_dir(
            session_id,
            'scores.csv')

    columns = [
            'session_id', 'question_id', 'time_taken', 'points', 'explanation']
    rows = [
            [session_id, q.split('.')[0], times[i], '', '']
            for i, q in enumerate(sampled_question_filenames)]
    write_csv(path, [columns] + rows)


def exam(time_limit, num_questions):
    sourcedir = FLASHCARDS_DIR
    attemptsdir = FLASHCARDS_ATTEMPTS_DIR

    time_per_question = time_limit * 60/ num_questions
    print '[{} seconds per question.]'.format(time_per_question)

    print sourcedir, attemptsdir, (time_limit, num_questions)

    sampled_question_filenames = select_random_question_cards(
            sourcedir, num_questions)

    session_id = make_session_id()
    times = []

    for i, question_filename in enumerate(sampled_question_filenames):
        question_id = question_filename.split('.')[0]
        question = get_question(question_filename)
        print 'question ', i, question

        with clock_this() as time_dict:
            myanswer = collect_answer()
        times.append(time_dict['seconds'])

        store_answer(session_id, question_id, myanswer)

    make_scores_file(session_id, sampled_question_filenames, times)
    print 'wrote responses in ', filename_in_attempts_dir(
            session_id,
            '')


if __name__ == '__main__':
    time_limit, num_questions = None, None
    if len(sys.argv) == 3:
        time_limit, num_questions = int(sys.argv[1]), int(sys.argv[2])

    set_variables(time_limit, num_questions)

    exam(TIME_LIMIT, NUM_QUESTIONS)

