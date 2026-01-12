import logging
import pandas as pd
from datetime import datetime

def fileName():
    return f'output/survey-{datetime.now().isoformat()}'

def loadToDataframe(rows, columns):
    pd.options.display.max_columns = None

    df = pd.DataFrame(rows).set_index('Response ID')
    df = df.rename(columns=columns)

    return df

def pandasToJSON(df):
    df.to_json(f'{fileName()}.json', orient='table')
    logging.info('Data frame saved to JSON output')

def pandasToCSV(df):
    df.to_csv(f'{fileName()}.csv')
    logging.info('Data frame saved to CSV output')

def pandasToExcel(df):
    df.to_excel(f'{fileName()}.xlsx')
    logging.info('Data frame saved to Excel output')

def pandasLoad(rows, columns):
    df = loadToDataframe(rows, columns)
    pandasToCSV(df)
    pandasToJSON(df)
    pandasToExcel(df) 

    return df