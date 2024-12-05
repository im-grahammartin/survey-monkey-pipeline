import math
import logging

from datetime import datetime, timezone
from extract.data_lake import saveToDataLake, clearExistingResponses, deleteResponseFromDataLake, checkForDataLakeFile, getResponseDetailIDs
from extract.metadata import getExtractMetadata, saveExtractMetadata
from extract.survey_monkey_api import apiSurveyDetails, apiSurveyResponsesBulk, apiSurveyResponseDetails, apiPageSize

def surveyDetails(surveyId): 
    survey = apiSurveyDetails(surveyId)

    saveToDataLake(f'survey_{surveyId}', 'details', survey)

    return {
        'title': survey['title'],
        'response_count': survey['response_count'],
    }

def getFetchableResponses(responseData): 
    ids = []
    for response in responseData:
        ids.append(response['id'])
    return ids

def getResponseSummaries(responseData):
    ids = []
    for response in responseData:
        ids.append({'id': response['id'], 'date_modified': response['date_modified']})
    return ids

def surveyResponses(surveyId, responseCount):
    responseSummaries = []
    pagesRequired = math.ceil(responseCount / apiPageSize())

    for page in range(pagesRequired):
        response = apiSurveyResponsesBulk(surveyId, page + 1)
        saveToDataLake(f'survey_{surveyId}/responses', f'responses_page_{str(response['page'])}', response)
        responseSummaries += getResponseSummaries(response['data'])

    return responseSummaries

def surveyResponseDetails(surveyId, responseId):
    try:
        response = apiSurveyResponseDetails(surveyId, responseId)
        saveToDataLake(f'survey_{surveyId}/responses_details', f'response_{responseId}', response)
        return True
    except:
        logging.error('Unknown error whilst retreiving survey response details')
        return False

def deletedRemovedSurveyResponses(surveyId, existingResponses, newResponses):
    deleteCount = 0
    deletedIds = []

    for existing in existingResponses:
        if len(list(filter(lambda r: r['id'] == existing , newResponses))) != 1:
            deleteResponseFromDataLake(surveyId, existing)
            deletedIds.append(existing)
            deleteCount =+ 1

    return { 'count': deleteCount, 'ids': deletedIds }

def determineNewResponsesToPull(surveyId, responseSummaries):
    filteredResponses = []

    for response in responseSummaries:
        filePath = f'/responses_details/response_{response['id']}.json'
        if not checkForDataLakeFile(surveyId, filePath):
            filteredResponses.append(response['id'])

    return filteredResponses

def determineUpdatedResponsesToPull(responseSummaries, lastExtractDateString=None):
    filteredResponses = []
    
    if(lastExtractDateString is not None):
        lastExtractDate = datetime.fromisoformat(lastExtractDateString)

        for response in responseSummaries:
            if datetime.fromisoformat(response['date_modified']) >= lastExtractDate:
                filteredResponses.append(response['id'])

    else:
        logging.warning('No last extract date provided. Assuming all responses need updating')
        for response in responseSummaries:
                filteredResponses.append(response['id'])
    
    return filteredResponses

def getSurveyResponseDetailsBatch(surveyId, responses):
    processedCount = 0

    for responseId in responses:
        if surveyResponseDetails(surveyId, responseId):
            processedCount+= 1
    return processedCount
        
    
def removeDuplicatedRecordsToUpdate(added, updated):
    duplicatedToRemove = []

    for response in updated:
        if response in added:
            duplicatedToRemove.append(response)

    for duplicate in duplicatedToRemove:
        updated.remove(duplicate)

    return updated
    
def validateFinalResults(newCount, oldCount):
    if oldCount == newCount:
        logging.info('Total number of saved responses validated successfully')
    else:
        logging.error(f'Unexpected number of responses saved. {newCount} found, {oldCount} expected')
        raise Exception('Extract step validation failed')
    
def surveyMonkey(surveyId):
    # Prep before running extract
    logging.info(f'Starting extract for survey {surveyId}')
    previousExtractMetadata = getExtractMetadata(surveyId)
    startTime = datetime.now(timezone.utc)
    clearExistingResponses(surveyId)
    existingResponses = getResponseDetailIDs(surveyId)

    # Get survey questions
    details = surveyDetails(surveyId)

    # Get survey responses in bulk, return IDs that need updating
    responseSummaries = surveyResponses(surveyId, details['response_count'])

    # Delete removed records
    deletedResponses = deletedRemovedSurveyResponses(surveyId, existingResponses, responseSummaries)

    # Determine which responses need to be pulled in full
    responsesToAdd = determineNewResponsesToPull(surveyId, responseSummaries)
    responsesToUpdate = determineUpdatedResponsesToPull(responseSummaries, previousExtractMetadata['start'])
    responsesToUpdate = removeDuplicatedRecordsToUpdate(responsesToAdd, responsesToUpdate)

    # Get survey response details
    responsesAddedCount = getSurveyResponseDetailsBatch(surveyId, responsesToAdd)
    responsesUpdatedCount = getSurveyResponseDetailsBatch(surveyId, responsesToUpdate)

    # Validate total number of records is as expected
    newResultCount = len(getResponseDetailIDs(surveyId))
    validateFinalResults(newResultCount, details['response_count'])

    # Save metadata about this pipeline execution    
    metadata = {
        'start': startTime.isoformat(),
        'end': datetime.now(timezone.utc).isoformat(),
        'survey_title': details['title'],
        'response_count': newResultCount,
        'response_count_previous': previousExtractMetadata['response_count'],
        'responses_added_count': responsesAddedCount,
        'responses_updated_count': responsesUpdatedCount,
        'responses_deleted_count': deletedResponses['count'],
        'responses_added': responsesToAdd,
        'responses_updated': responsesToUpdate,
        'responses_deleted': deletedResponses['ids'],
        'response_ids': getResponseDetailIDs(surveyId)
    }
    saveExtractMetadata(surveyId, metadata)