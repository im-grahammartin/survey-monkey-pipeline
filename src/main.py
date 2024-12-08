import sys
import logging

from datetime import datetime, timezone
from modules.logging import logging_init
from modules.survey_monkey import surveyMonkey
from modules.pandas import pandasLoad
from modules.normalize import transformToNormalizedDb
from modules.survey_transforms.mfm_transforms import transformMfmTesters, mfmColumns
from modules.validate import validatePipelineRun

# surveyId = '416262167' # Graham test
surveyId = '314840976' # MFM data

def main():
    startTime = datetime.now(timezone.utc)

    # Setup loading
    logging_init()
    logging.info(f'Pipeline started at {startTime}')

    # Extract from API source to data lake
    surveyMonkey(surveyId)

    # Transform into a generic, normalized database loaded into Postgres
    transformToNormalizedDb(surveyId)

    # Transform into a denormalized data object with domain specific transformations for MFM
    transformedData = transformMfmTesters(surveyId)

    # Get column names for denormalized data
    dataColumns = mfmColumns(surveyId)

    # Load into a Pandas data frame, saved to CSV, JSON and Excel file formats
    pandaLoad = pandasLoad(transformedData, dataColumns)

    # End and validate the pipeline
    endTime = datetime.now(timezone.utc)
    validatePipelineRun(surveyId, pandaLoad, startTime, endTime)
    logging.info(f'Pipeline finished at {endTime}')

if __name__ == '__main__':
    sys.exit(main())