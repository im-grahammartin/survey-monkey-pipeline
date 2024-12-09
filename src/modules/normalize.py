import logging

from modules.dataLake import getResponseDetails
from modules.metadata import getExtractMetadata
from modules.postgres import postgresConnection, postgresSession
from modules.transformSurveyDetails import transformSurveyDetails
from modules.transformSurveyResponse import transformSurveyResponse
from modules.postgresSchema import Base, Responses

def transformSurveyResponses(surveyId):
    responsesList = getResponseDetails(surveyId)

    for responseFile in responsesList:
        transformSurveyResponse(responseFile)

def transformToNormalizedDb(surveyId):
    extract = getExtractMetadata(surveyId)

    engine = postgresConnection()
    session = postgresSession(engine)

    # Uncomment to start a full refresh
    Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)

    transformSurveyDetails(surveyId)
    transformSurveyResponses(surveyId)

    if extract['response_count'] == session.query(Responses).filter_by(surveyId = surveyId).count():
        logging.info(f'{session.query(Responses).filter_by(surveyId = surveyId).count()} of {extract['response_count']} are in database')
    else:
        logging.error(f'{session.query(Responses).filter_by(surveyId = surveyId).count()} of {extract['response_count']} are in database')
        raise Exception('Transformation validation failed')