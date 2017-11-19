import sys
import time
import re
import os
import random
import datetime
from shutil import copyfile

from __future__ import division


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
    return now.strftime('%Y-%m-%dT%H%M')


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


def only_question_files(all_files):
    question_files = [filename for filename in all_files
            if re.match(r'\d{2,}-(\d)-', filename).groups()[0] == '0']
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
    outpath = os.path.join(os.getenv('FLASHCARDS_ATTEMPTS_DIR'), outfile)
    with open(outpath, 'w') as fd:
        fd.write(myanswer)


def get_question(question_filename):
    path = os.path.join(os.getenv('FLASHCARDS_DIR'))
    with open(path) as fd:
        content = fd.read()

    return content


def store_answer(session_id, question_id, answer):
    attemptsdir = os.getenv('FLASHCARDS_ATTEMPTS_DIR')
    path = os.path.join(attemptsdir, session_id, question_id + '.txt')
    with open(path, 'w') as fd:
        fd.write(answer)


def exam(time_limit, num_questions):
    sourcedir = os.getenv('FLASHCARDS_DIR')
    attemptsdir = os.getenv('FLASHCARDS_ATTEMPTS_DIR')

    time_per_question = time_limit * 60/ num_questions
    print '[{} seconds per question.]'.format(time_per_question)

    print sourcedir, attemptsdir, (time_limit, num_questions)

    sampled_question_filenames = select_random_question_cards(
            sourcedir, num_questions)


    session_id = make_session_id()

    for i, question_filename in enumerate(sampled_question_filenames):
        question_id = question_filename.split('.')[0]
        question = get_question(question_filename)
        print 'question ', i, question
        myanswer = raw_input('> ')

        store_answer(session_id, question_id, myanswer)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'do.py <time limit> <num questions>'
        sys.exit()

    time_limit, num_questions = sys.argv[1:3]
    exam(time_limit, num_questions)

