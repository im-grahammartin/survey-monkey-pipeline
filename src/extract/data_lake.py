import json
import os
import logging
import shutil

def saveToDataLake(dir_name, file_name, data):
    dir_name = 'datalake/' + dir_name
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    json_object = json.dumps(data, indent=4)
 
    with open(f'{dir_name}/{file_name}.json', 'w') as outfile:
        success = outfile.write(json_object)
    
    if(success > 0):
        logging.info(f'Data saved to {dir_name}/{file_name}.json')
    else:
        logging.error(f'Error saving {dir_name}/{file_name}.json')

def readFromDatalake(filePath):
    if os.path.exists(filePath):
        metadataFile = open(filePath, 'r')
        metadata = metadataFile.read()
        metadataFile.close()
        return json.loads(metadata)
    else:
        logging.warning('No prior metadata found')
        return { 'start': None }

def clearExistingResponses(surveyId):
    folder_path = f'datalake/survey_{surveyId}/responses'
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            logging.info('Previous response summaries successfully cleared')
        except:
            logging.error('Unable to clear historic response summary data')
    else:
        logging.warn(f'No exisiting responses saved to {folder_path}. Skipping the cleaning step')

def deleteResponseFromDataLake(surveyId, responseId):
    filePath = f'datalake/survey_{surveyId}/responses_details/response_{responseId}.json'
    if os.path.exists(filePath): 
        os.remove(filePath)
        logging.info(f'File {filePath} deleted successfully')
    else: 
        logging.error(f'File {filePath} not found')

def getResponseDetails(surveyId):
    existingResponseIds = []
    existingResponsesPath = f'datalake/survey_{surveyId}/responses_details'
    if os.path.exists(existingResponsesPath):
        existingResponseDetails = os.listdir(existingResponsesPath)
    
        for responseDetailsFile in existingResponseDetails:
            existingResponseIds.append(responseDetailsFile.replace('response_','').replace('.json','')) # Extract ID from file name
    else:
        logging.warning(f'No existing records found at ${existingResponsesPath}')

    return existingResponseIds

def checkForDataLakeFile(surveyId, filePath):
    filePath = f'datalake/survey_{surveyId}/{filePath}'
    return os.path.exists(filePath)