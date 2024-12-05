import sys

from modules.logging import logging_init
from extract.survey_monkey import surveyMonkey
from transform.normalize import transformToNormalizedDb
from transform.join import join


# surveyId = '416262167' # Graham test
surveyId = '314840976' # MFM data
# surveyId = '123'

def main():
    logging_init()
    # surveyMonkey(surveyId)
    # transformToNormalizedDb(surveyId)
    join(surveyId)

if __name__ == '__main__':
    sys.exit(main())