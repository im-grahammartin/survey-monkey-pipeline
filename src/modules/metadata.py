import logging

from modules.data_lake import saveToDataLake, readFromDatalake

def saveExtractMetadata(surveyId, metadata):
    saveToDataLake(f'survey_{surveyId}/', f'extract_metadata', metadata)
    saveToDataLake(f'survey_{surveyId}/metadata_archive/extracts/', f'metadata_{metadata['start']}', metadata)

    logging.info('-----------------------------------------')
    logging.info('Survey Monkey Data Extracton success')
    logging.info(f'Title: {metadata['survey_title']}')
    logging.info(f'{metadata['response_count']} records are now saved (previously {metadata['response_count_previous']})')
    logging.info(f'{metadata['responses_added_count']} records were added')
    logging.info(f'{metadata['responses_updated_count']} records were updated')
    logging.info(f'{metadata['responses_deleted_count']} records were deleted')
    logging.info('-----------------------------------------')

def getExtractMetadata(surveyId):
    filePath = f'datalake/survey_{surveyId}/extract_metadata.json'
    metadata = readFromDatalake(filePath)

    if metadata:
        return metadata
    else:
        return { 'start': None, 'survey_title': '', 'response_count': 0 }
    

def savePipelineMetadata(surveyId, metadata):
    saveToDataLake(f'survey_{surveyId}/', f'pipeline_metadata', metadata)
    saveToDataLake(f'survey_{surveyId}/metadata_archive/pipeline_executions/', f'pipeline_metadata_{metadata['start']}', metadata)

    logging.info('-----------------------------------------')
    logging.info('Survey Monkey Data Pipeline completed')
    logging.info(f'Title: {metadata['survey_title']}')
    logging.info(f'{metadata['extract_count']} records extracted from Survey Monkey')
    logging.info(f'{metadata['db_count']} records stored in normalized database')
    logging.info(f'{metadata['load_count']} records transformed into final dataset')
    logging.info(f'Validation: {metadata['validation']}')
    logging.info(f'Start time: {metadata['start']}')
    logging.info(f'Finish time: {metadata['end']}')
    logging.info(f'Duration: {metadata['duration_minutes']} minutes')
    logging.info('-----------------------------------------')