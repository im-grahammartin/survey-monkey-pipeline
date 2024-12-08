import logging

from datetime import datetime
from dateutil import relativedelta

from modules.denormalize import columnNames, transformToDenormalizedDb
from modules.sqlSelects import getSurveyQuestions

dobQuestions = [ 
    '732951251', 
    '732951274', 
    '732951280', 
    '732951285', 
    '732951290', 
    '732951295', 
    '732951300', 
    '732951305', 
    '732951310', 
    '732951315', 
    '732951320', 
    '732951325', 
    '732951330', 
    '732951335', 
    '732951340', 
    '732951345', 
    '732951350', 
    '732951355', 
    '732951360', 
    '732951365'
]

followerQuestions = [ 
    '732951407', 
    '732951421', 
    '732951410', 
    '733518723', 
    '732951413'
]

def numbersFromString(string):
    # Return only numbers from a string
    f = filter(str.isdecimal,string) 
    s = ''.join(f) 
    return s

def containsNumber(splitString): 
    # Check a string to see if it contains any numbers
    if any(map(str.isdigit, splitString)):
        return splitString 
    else:
        return ''


def followerCountFromString(followerCount):
    followerCountInt = 0
 
    # Try/catch as may not always be possible to extract followe count from a string
    try:
        
        # Convert string into a list of words, and remove any words that do not contain any numbers
        followerCountTextList = str(followerCount).split(' ') 
        segmentsWithNumbers = map(containsNumber, followerCountTextList) 
        rejoinedFollowerCountString = ' '.join(segmentsWithNumbers)

        # Attempt to clean common common formatting characters/words from the follower count text input
        cleanedString = ' '.join(rejoinedFollowerCountString.splitlines()).strip().upper().replace('+','').replace('?','').replace(',','').replace(')','').replace(')','').replace('-',' ').replace('/',' ').replace('OVER ', '')
 
        # K and M are used to denote thousands and millions – if present in the string then convert to int
        if 'K' in cleanedString:
            if len(followerCount) > 1: 
                followerCountInt = int(float(cleanedString.replace('K','')) * 1000) 
        elif 'M' in cleanedString: 
            if len(followerCount) > 1:
                followerCountInt = int(float(cleanedString.replace('M','')) * 1000000) 
        elif(len(numbersFromString(cleanedString)) > 0):
            followerCountInt = int(numbersFromString(cleanedString.split(' ')[0]))
 
    except:
        logging.warning(f'Unable to parse follower count string {followerCount}')
 
    return followerCountInt

def convertDobToAge(dob):
    # Try/except due to text input format on Survey Monkey
    try:
        start_date = datetime.strptime(dob.split(',')[0], "%m/%d/%Y")
        end_date = datetime.now()

        delta = relativedelta.relativedelta(end_date, start_date)
    
        return int(delta.years) # Only return the whole year value – no requirement for more precise ages
    except:
        logging.warning(f'Unable to convert {dob} into an age')
        return None

def mfmColumns(surveyId):
    standardColumns = columnNames(surveyId)
    additionalColumns = mfmAdditionalColumns(surveyId)
    return standardColumns | additionalColumns

def mfmAdditionalColumns(surveyId):
    questions = getSurveyQuestions(surveyId)
    questionHeadings = {}

    for question in questions:
        if question[0] in dobQuestions:
            questionHeadings.update({f'{question[0]}-dob': question[1].replace('date of birth', 'age')})

    return questionHeadings

def transformMfmTesters(surveyId): 
    mfmAdditionalColumns(surveyId)
    denormed = transformToDenormalizedDb(surveyId) 
     
    transformed = []
 
    logging.info(f'Start MFM transformations to survey data for {surveyId}')

    for response in denormed:
        aggregatedFollowers = 0 
        transformedResponse = {}

        for key, value in response.items():
            # Check if this answer is for a date of birth question – if so, add an additional property with the current age
            if key in dobQuestions:
                transformedResponse.update({f'{key}-dob': convertDobToAge(value)}) 
             
             # If this answer is for a social network follower count then included it in the aggregated total
            if key in followerQuestions: 
                aggregatedFollowers+= followerCountFromString(value)
 
        transformedResponse.update({'Aggregated Follower Count': aggregatedFollowers}) 
        transformedResponse.update(response)
 
        transformed.append(transformedResponse)
 
    logging.info(f'Finish MFM transformations to survey data for {surveyId}')

    return transformed 