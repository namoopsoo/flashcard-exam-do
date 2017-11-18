




import os

from shutil import copyfile



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


