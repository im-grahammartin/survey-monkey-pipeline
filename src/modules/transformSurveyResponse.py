import logging

from modules.dataLake import readFromDatalake
from modules.postgres import postgresConnection, postgresSession
from modules.postgresSchema import Responses, ResponseMetaData, Answers, AnswerRow, AnswerChoice

def transformResponse(session, responseData):
    response = Responses(
        responseId=responseData['id'],
        surveyId=responseData['survey_id'],
        totalTime=responseData['total_time'],
        editUrl=responseData['edit_url'],
        analyzeUrl=responseData['analyze_url'],
        ipAddress=responseData['ip_address'],
        responseStatus=responseData['response_status'],
        collectionMode=responseData['collection_mode'],
        dateCreated=responseData['date_created'],
        dateModified=responseData['date_modified'],
        downloadUrl=responseData['href']
    )

    session.add(response)
    session.commit()

    logging.info(f'Response {responseData['id']} inserted to database')

def transformResponseMetadata(session, responseData):
    if('metadata' in responseData and 'respondent' in responseData['metadata']):
        metadataKeys = responseData['metadata']['respondent'].keys()

        for key in metadataKeys:
            metadata = ResponseMetaData(
                responseId=responseData['id'], 
                metadataKey=key,
                metadataValue=str(responseData['metadata']['respondent'][key]['value'])
            )
            session.add(metadata)
            logging.info(f'Response metadata {key} for {responseData['id']} inserted to database')

        # session.commit()

def transformAnswer(session, responseId, questionId, answerData):
    if(len(answerData) == 1 and 'text' in answerData[0]):
        textValue = answerData[0]['text']
    else:
        textValue = ''

    answer = Answers(
        responseId=responseId, 
        questionId=questionId,
        text=textValue
    )
    session.add(answer)
    session.commit()
    answerId = answer.answerId
    logging.info(f'Answer for question {questionId} in response {responseId} inserted to database')

    for answer in answerData:
        if 'choice_id' in answer:
            transformAnswerChoice(session, answerId, answer)
        elif 'row_id' in answer:
            transformAnswerRow(session, answerId, answer)

def transformAnswerChoice(session, answerId, answerData):
    answerChoice = AnswerChoice(
        answerId=answerId, 
        choiceId=answerData['choice_id'],
    )
    session.add(answerChoice)
    # session.commit()

    logging.info(f'Answer choice {answerData['choice_id']} for answer {answerId} inserted to database')

def transformAnswerRow(session, answerId, answerData):
    answerRow = AnswerRow(
        answerId=answerId, 
        rowId=answerData['row_id'],
        text=answerData['text']
    )
    session.add(answerRow)
    # session.commit()

    logging.info(f'Answer row {answerData['row_id']} for answer {answerId} inserted to database')

def transformSurveyResponse(responseFile):
    responseDetails = readFromDatalake(responseFile)

    engine = postgresConnection()
    session = postgresSession(engine)

    transformResponse(session, responseDetails)
    transformResponseMetadata(session, responseDetails)

    for page in responseDetails['pages']:
        if 'questions' in page:
            for question in page['questions']:
                 transformAnswer(session, responseDetails['id'], question['id'], question['answers'])

    session.commit()
    session.close()