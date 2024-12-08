import logging
from modules.postgres import postgresConnection
from sqlalchemy import text

engine = postgresConnection()

def runSQL(query):    
    with engine.connect() as conn:

        try:
            result = conn.execute(text(query))    
            result = [r for r in result]

            return result
        
        except Exception as e:
            logging.error(f'SQL Error retrieving data from database. {e}')

def getSurveyQuestions(surveyId):
    logging.debug(f'Getting survey questions for survey {surveyId}')

    return runSQL(f"""
        SELECT
            questions."Question ID",
            questions."Heading",
            questions."Family" as "Question Type",
            questions."Subtype" as "Question Subtype"
        FROM pages
        JOIN questions
        ON questions."Page ID" = pages."Page ID"
        WHERE pages."Survey ID" = '{surveyId}'
            AND questions."Visible" = TRUE 
        ORDER BY pages."Position" ASC, questions."Position" ASC
    """)

def getSurveyResponses(surveyId):
    logging.debug(f'Getting survey responses for survey {surveyId}')

    return runSQL(f"""
        SELECT
            responses."Response ID"
        FROM responses
        WHERE responses."Survey ID" = '{surveyId}'
    """)

def getSurveyResponseAnswers(surveyId, responseId):
    logging.debug(f'Getting survey response answers for survey {surveyId}, response {responseId}')

    return runSQL(f"""
        SELECT 
            responses."Survey ID",
            responses."Response ID",
            answers."Answer ID",
            answers."Question ID",
            questions."Heading",
            questions."Family" as "Question Type",
            questions."Subtype" as "Question Subtype",
            NULLIF(answers."Text",'') as "Answer Text",
            NULLIF(choices."Text",'') as "Answer Choice",
            NULLIF(answer_rows."Text",'') as "Answer Row Text",
            responses."Response Status"
        FROM answers
        JOIN responses
        ON answers."Response ID" = responses."Response ID"
        LEFT JOIN questions
        ON questions."Question ID" = answers."Question ID"
        LEFT JOIN pages
        ON pages."Page ID" = questions."Page ID"
        LEFT JOIN answer_choices
        ON answers."Answer ID" = answer_choices."Answer ID"
        LEFT JOIN choices
        ON answer_choices."Choice ID" = choices."Choice ID"
        LEFT JOIN answer_rows
        ON answers."Answer ID" = answer_rows."Answer ID"
        LEFT JOIN rows
        ON answer_rows."Row ID" = rows."Row ID"
        WHERE responses."Response ID" = '{responseId}'
        AND responses."Survey ID" = '{surveyId}'
        ORDER BY questions."Position" ASC, rows."Position" ASC, choices."Position" ASC
    """)

# ,
#             metadata."Metadata Key",
#             metadata."Metadata Value"

# LEFT JOIN metadata
#         ON responses."Response ID" = metadata."Response ID"