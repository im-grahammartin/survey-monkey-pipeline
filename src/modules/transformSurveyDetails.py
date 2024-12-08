import logging
from modules.data_lake import readFromDatalake
from modules.postgres import postgresConnection, postgresSession
from modules.postgresSchema import Surveys, Pages, Choices, Row, Questions

def transformSurvey(session, surveyData):
    survey = Surveys(
        surveyId=surveyData['id'],
        title=surveyData['title'],
        language=surveyData['language'],
        category=surveyData['category'],
        questionCount=surveyData['question_count'],
        pageCount=surveyData['page_count'],
        responseCount=surveyData['response_count'],
        dateCreated=surveyData['date_created'],
        dateModified=surveyData['date_modified'],
        href=surveyData['href'],
        analyzeUrl=surveyData['analyze_url'],
        editUrl=surveyData['edit_url'],
        collectUrl=surveyData['collect_url'],
        summaryUrl=surveyData['summary_url'],
        previewUrl=surveyData['preview']
    )
    session.add(survey)
    session.commit()

    logging.info(f'Survey {surveyData['id']} inserted to database')

def transformPage(session, surveyData, pageData):
    survey = Pages(
        pageId=pageData['id'],
        surveyId=surveyData['id'],
        title=pageData['title'],
        description=pageData['description'], 
        position=pageData['position'],
        questionCount=pageData['question_count'],
        href=pageData['href']
    )
    
    session.add(survey)
    session.commit()

    logging.info(f'Page {pageData['id']} inserted to database')

def transformQuestion(session, pageData, questionData):
    questions = Questions(
        questionId=questionData['id'],
        pageId=pageData['id'],
        heading=questionData['headings'][0]['heading'],
        position=questionData['position'], 
        visible=questionData['visible'],
        family=questionData['family'],
        subtype=questionData['subtype']
    )
    session.add(questions)
    session.commit()

    logging.info(f'Question {questionData['id']} inserted to database')

def transformChoice(session, questionData, choiceData):
    choices = Choices(
        choiceId=choiceData['id'],
        questionId=questionData['id'],
        position=choiceData['position'],
        visible=choiceData['visible'], 
        text=choiceData['text']
    )
    session.add(choices)
    # session.commit()

    logging.info(f'Choice {choiceData['id']} inserted to database')

def transformRow(session, questionData, rowData):
    rows = Row(
        rowId=rowData['id'],
        questionId=questionData['id'],
        position=rowData['position'],
        visible=rowData['visible'], 
        text=rowData['text'],
        rowType=rowData['type'] if 'type' in rowData else '',
        required=rowData['required'] if 'required' in rowData else False
    )
    session.add(rows)
    # session.commit()

    logging.info(f'Row {rowData['id']} inserted to database')

def transformSurveyDetails(surveyId):
    surveyDetails = readFromDatalake(f'datalake/survey_{surveyId}/details.json')

    engine = postgresConnection()
    session = postgresSession(engine)
    
    transformSurvey(session, surveyDetails)

    for page in surveyDetails['pages']:
        transformPage(session, surveyDetails, page)
        
        for question in page['questions']:
            transformQuestion(session, page, question)

            if 'answers' in question:
                if 'choices' in question['answers']:
                    for choice in question['answers']['choices']:
                        transformChoice(session, question, choice)

                if 'rows' in question['answers']:
                    for answerRow in question['answers']['rows']:
                        transformRow(session, question, answerRow)

    session.commit()
    session.close()