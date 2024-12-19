import logging

from modules.sqlSelects import getSurveyQuestions, getSurveyResponses, getSurveyResponseAnswers
from modules.postgres import postgresConnection

def columnNames(surveyId):
    engine = postgresConnection()
    questions = getSurveyQuestions(surveyId, engine)

    columnDict = { 'Response ID': 'Response ID' }

    for question in questions:
        columnDict[question[0]] = question[1]

    return columnDict

def getAnswerFromAnswer(answer):
    formattedAnswer = ''

    if answer[7] is not None:
        formattedAnswer = answer[7]

    if answer[8] is not None:
        formattedAnswer = answer[8]

    if answer[9] is not None:
        formattedAnswer = answer[9]

    return formattedAnswer
    
def transformToDenormalizedDb(surveyId):
    engine = postgresConnection()
    logging.info(f'Start denormalising survey data for {surveyId}')

    responses = getSurveyResponses(surveyId, engine)

    denormalizedData = []
    
    for response in responses:
        responseDict = {}
        answers = getSurveyResponseAnswers(surveyId, response[0], engine)
        responseDict['Response ID'] = response[0]

        for answer in answers:
            if(answer[3] in responseDict):
                responseDict[answer[3]] = f'{responseDict[answer[3]]}, {getAnswerFromAnswer(answer)}' 
            else:
                responseDict[answer[3]] = getAnswerFromAnswer(answer)

        denormalizedData.append(responseDict)

    logging.info(f'Finish denormalising survey data for {surveyId}')

    return denormalizedData

    