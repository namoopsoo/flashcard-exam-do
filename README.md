# flashcard-exam-do
Run tiny self assessment on flashcards

### Setup

```
git clone git@github.com:namoopsoo/flashcard-exam-do.git

cd flashcard-exam-do
chmod u+x do.py

mkdir -p ~/bin
ln -s $(pwd)/do.py ~/bin/flashcardexamdo

cat

# make a dir for attempts
mkdir /myblah/attempts

# put flashcards into your flashcards directory
# /blah/my/cards

```
* Make a profile , 
```yaml
FLASHCARDS_ATTEMPTS_DIR: '/myblah/attempts'
FLASHCARDS_DIR: '/blah/my/cards'
TIME_LIMIT: '5'
NUM_QUESTIONS: '5'
```
* Do assessments whenever you feel like it
```
flashcardexamdo
```

