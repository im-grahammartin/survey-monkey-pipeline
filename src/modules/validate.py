import logging

from modules.metadata import getExtractMetadata, savePipelineMetadata
from modules.sqlSelects import getSurveyResponses

def validatePipelineRun(surveyId, loadData, start, end):
    extract = getExtractMetadata(surveyId)
    extractCount = extract['response_count']
    normalizedLoadCount = len(getSurveyResponses(surveyId))
    denormalizedLoadCount = loadData.shape[0]

    if extractCount == normalizedLoadCount == denormalizedLoadCount:
        validation = True
        validationText = 'Pass'
    else:
        validation = False
        validationText = 'Fail'
    
    pipelineDuration = round((end - start).total_seconds() / 60, 2)

    metadata = {
        'start': start.isoformat(),
        'end': end.isoformat(),
        'duration_minutes': pipelineDuration,
        'survey_title': extract['survey_title'],
        'extract_count': extractCount,
        'db_count': normalizedLoadCount, 
        'load_count': denormalizedLoadCount,
        'validation': validationText 
    }

    savePipelineMetadata(surveyId, metadata)

    if validation is True:
        logging.info('Pipeline completed ✅')
    else:
        logging.error('Pipeline validation failed ⛔️')