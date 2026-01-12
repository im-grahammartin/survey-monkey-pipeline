from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Text, String, Boolean, ForeignKey

Base = declarative_base()

class Surveys(Base):
    __tablename__ = 'surveys'

    surveyId = Column("Survey ID", String(20), primary_key=True)
    title = Column("Title", String(500))
    language = Column("Language", String(5))
    category = Column("Category", String(200))
    questionCount = Column("Question Count", Integer)
    pageCount = Column("Page Count", Integer)
    responseCount = Column("Response Count", Integer)
    dateCreated = Column("Date Created", DateTime)
    dateModified = Column("Date Modified", DateTime)
    href = Column("Href", String(250))
    analyzeUrl = Column("Analyze URL", String(250))
    editUrl = Column("Edit URL", String(250))
    collectUrl = Column("Collect URL", String(250))
    summaryUrl = Column("Summary URL", String(250))
    previewUrl = Column("Preview URL", String(250))
    
    def __repr__(self):
        return f'Survey ID {self.surveyId}'

class Pages(Base):
    __tablename__ = 'pages'

    pageId = Column("Page ID", String(20), primary_key=True)
    surveyId = Column("Survey ID", String(20), ForeignKey('surveys.Survey ID'))
    title = Column("Title", String(300))
    description = Column("Description", Text)
    position = Column("Position", Integer)
    questionCount = Column("Question Count", Integer)
    href = Column("Href", String(250))

    def __repr__(self):
        return f'Page ID {self.pageId}'

class Choices(Base):
    __tablename__ = 'choices'

    choiceId = Column("Choice ID", String(20), primary_key=True)
    questionId = Column("Question ID", String(20), ForeignKey('questions.Question ID'))
    position = Column("Position", Integer)
    visible = Column("Visible", Boolean)
    text = Column("Text", String(250))

    def __repr__(self):
        return f'Choice ID {self.choiceId}'

class Row(Base):
    __tablename__ = 'rows'

    rowId = Column("Row ID", String(20), primary_key=True)
    questionId = Column("Question ID", String(20), ForeignKey('questions.Question ID'))
    position = Column("Position", Integer)
    visible = Column("Visible", Boolean)
    text = Column("Text", Text)
    rowType = Column("Type", String(250))
    required = Column("Required", Boolean)

    def __repr__(self):
        return f'Row ID {self.rowId}'

class Questions(Base):
    __tablename__ = 'questions'

    questionId = Column("Question ID", String(20), primary_key=True)
    pageId = Column("Page ID", String(20), ForeignKey('pages.Page ID'))
    heading = Column("Heading", Text)
    position = Column("Position", Integer)
    visible = Column("Visible", Boolean)
    family = Column("Family", String(250))
    subtype = Column("Subtype", String(250))


    def __repr__(self):
        return f'Question ID {self.questionId}'

class Responses(Base):
    __tablename__ = 'responses'

    responseId = Column("Response ID", String(20), primary_key=True)
    surveyId = Column("Survey ID", String(20), ForeignKey('surveys.Survey ID'))
    totalTime = Column("Total Time", Integer)
    editUrl = Column("Edit URL", String(250))
    analyzeUrl = Column("Analyze URL", String(250))
    ipAddress = Column("IP Address", String(32))
    responseStatus = Column("Response Status", String(50))
    collectionMode = Column("Collection Mode", String(50))
    dateCreated = Column("Date Created", DateTime)
    dateModified = Column("Date Modified", DateTime)
    downloadUrl = Column("Download URL", String(250))

    def __repr__(self):
        return f'Response ID {self.responseId}'

class ResponseMetaData(Base):
    __tablename__ = 'metadata'

    metadataId = Column("Metadata ID", Integer, primary_key=True)
    responseId = Column("Response ID", String(20), ForeignKey('responses.Response ID'))
    metadataKey = Column("Metadata Key", String(100))
    metadataValue = Column("Metadata Value", String(500))

    def __repr__(self):
        return f'Metadata ID {self.metadataId}'

class Answers(Base):
    __tablename__ = 'answers'

    answerId = Column("Answer ID", Integer, primary_key=True)
    responseId = Column("Response ID", String(20), ForeignKey('responses.Response ID'))
    questionId = Column("Question ID", String(20), ForeignKey('questions.Question ID'))
    text = Column("Text", Text)
    
    def __repr__(self):
        return f'Answer ID {self.answerId}'

class AnswerRow(Base):
    __tablename__ = 'answer_rows'

    answerRowId = Column("Answer Row ID", Integer, primary_key=True)
    answerId = Column("Answer ID", Integer, ForeignKey('answers.Answer ID'))
    rowId = Column("Row ID", String(20))
    text = Column("Text", Text)

    def __repr__(self):
        return f'Answer Row ID {self.answerRowId}'

class AnswerChoice(Base):
    __tablename__ = 'answer_choices'

    answerChoiceId = Column("Answer Choice ID", Integer, primary_key=True)
    answerId = Column("Answer ID", Integer, ForeignKey('answers.Answer ID'))
    choiceId = Column("Choice ID", String(20))

    def __repr__(self):
        return f'Answer Choice ID {self.answerChoiceId}'