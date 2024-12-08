import requests
import time
import logging

from os import getenv
from dotenv import load_dotenv

load_dotenv(override=True)

apiBase = getenv('SURVEY_MONKEY_API_BASE')
pageSize = 50

def handleRateLimit(type, limit, remaining, reset):
    if remaining == 0:
        # Allow a sleep of up to 1 minute, otherwise error
        if reset <= 60:
            time.sleep(reset)
            logging.warning(f'{remaining} requests of {limit} requests per {type} remaining. Sleeping for {reset} seconds before continuing')
        else:
            logging.error(f'{remaining} requests of {limit} requests per {type} remaining. Wait {reset} seconds before attempting again')
            raise Exception('Rate limit exceeded')

    else:
        logging.info(f'{remaining} requests of {limit} requests per {type} remaining')

def getSurveyMonkeyRateLimitHeaders(type, responseHeaders):
    return [
        responseHeaders[f'X-Ratelimit-App-Global-{type}-Limit'],
        responseHeaders[f'X-Ratelimit-App-Global-{type}-Remaining'], 
        responseHeaders[f'X-Ratelimit-App-Global-{type}-Reset']
    ]

def checkSurveyMonkeyRateLimits(responseHeaders):
    handleRateLimit(
        'minute',
        *getSurveyMonkeyRateLimitHeaders('Minute', responseHeaders)
    )
    handleRateLimit(
        'day',
        *getSurveyMonkeyRateLimitHeaders('Day', responseHeaders)
    )

def apiGetRequest(endpoint, payload=None):
    bearer_token = getenv('SURVEY_MONKEY_API_KEY')
    headers = {"Authorization": f"Bearer {bearer_token}"}

    try:
        response = requests.get(endpoint, headers=headers, params=payload, timeout=5)

        responseBody = response.json()

        if(response.status_code != 200):
            logging.error(f'Survey Monkey API Error ({response.status_code} HTTP response)')
            logging.error(f'Survey Monkey API - Error ID: {responseBody['error']['id']}')
            logging.error(f'Survey Monkey API - Name: {responseBody['error']['name']}')
            logging.error(f'Survey Monkey API - Message: {responseBody['error']['message']}')
            logging.error(f'Survey Monkey API - Docs: {responseBody['error']['docs']}')
            raise Exception(f'Survey Monkey API {response.status_code} response')

        # Check against rate limits and pause or exit process if rate limit is exceeded
        checkSurveyMonkeyRateLimits(response.headers)

        return responseBody
    except:
        raise Exception('Uncaught error in Survey Monkey API request')

def apiPageSize():
    return pageSize

def apiSurveyDetails(surveyId):
    endpoint = apiBase + 'surveys/' + surveyId + '/details'
    return apiGetRequest(endpoint)

def apiSurveyResponsesBulk(surveyId, page):
    endpoint = apiBase + 'surveys/' + surveyId + '/responses/bulk'
    params = { "page": page, "per_page": pageSize, "sort_by": "date_modified", "sort_order": "DESC" } 
    return apiGetRequest(endpoint, params)

def apiSurveyResponseDetails(surveyId, responseId):
    endpoint = f'{apiBase}surveys/{surveyId}/responses/{responseId}/details'
    return apiGetRequest(endpoint)