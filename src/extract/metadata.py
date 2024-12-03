import logging

from extract.data_lake import saveToDataLake, readFromDatalake

def saveExtractMetadata(surveyId, metadata):
    saveToDataLake(f'survey_{surveyId}/', f'metadata', metadata)
    saveToDataLake(f'survey_{surveyId}/metadata_archive/', f'metadata_{metadata['start']}', metadata)

    logging.info('-----------------------------------------')
    logging.info('Survey Monkey Data Extracton success')
    logging.info(f'Title: {metadata['survey_title']}')
    logging.info(f'{metadata['response_count']} records are now saved (previously {metadata['response_count_previous']})')
    logging.info(f'{metadata['responses_added_count']} records were added')
    logging.info(f'{metadata['responses_updated_count']} records were updated')
    logging.info(f'{metadata['responses_deleted_count']} records were deleted')
    logging.info('-----------------------------------------')

def getExtractMetadata(surveyId):
    filePath = f'datalake/survey_{surveyId}/metadata.json'
    return readFromDatalake(filePath)