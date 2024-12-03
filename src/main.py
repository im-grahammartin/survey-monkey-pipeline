import sys

from utils.logging import logging_init
from extract.survey_monkey import surveyMonkey

# surveyId = '416262167' # Graham test
surveyId = '314840976' # MFM data

def main():
    logging_init()
    surveyMonkey(surveyId)

if __name__ == '__main__':
    sys.exit(main())