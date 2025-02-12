import time
from threading import Thread
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from .sms import SMS
import yaml
from database.logger import Logger

# Control Panel for admin
class ControlConsole(Thread):

    def __init__(self, sms: SMS, msg: Message, secretPath: str = 'secrets.yml'):
        Thread.__init__(self)
        self.db = None
        self.sms = sms
        self.msg = msg
        self.number = Number(msg.number)
        
        # Logging:
        self.logger = Logger()

        with open(secretPath) as f:
            cfg = yaml.safe_load(f)
        self.adminNumbers = map(Number, cfg['admin']['numbers'])
        self.password = cfg['admin']['password']

        if self.checkIsAdmin():
            self.run()

     
    def checkIsAdmin(self):
        # Wait for password:
        rawInput = self.sms.awaitResponse(str(self.number))

        if self.number in self.adminNumbers:
            if rawInput.content == self.password:
                return True
        return False
    
    def run(self):
        adminConsoleExit = "Exited admin mode."
        successMessage = "Admin access granted. Text 'QUIT' to exit. Text 'HELP' for help."

        self.sms.send(str(self.number), successMessage)
        self.logger.adminLogin(str(self.number))

        # Creates temporary DBs.
        dbNorth = DatabaseHandler(SchoolNameMapper()['NNHS'])
        dbSouth = DatabaseHandler(SchoolNameMapper()['NSHS'])

        # Dict of MSG: Response
        responsesDict = {
            'HELP': self.help,
            'ANNOUNCE': self.announce,
            'ANALYTICS': self.analytics
        }
        
        contentRaw = self.sms.awaitResponse(str(self.number))
        if contentRaw == None:
            return False
        content = contentRaw.content.upper()

        while content != 'QUIT': # Admin console toggled until quit.
            if content in responsesDict:
                responsesDict[content]()
            response = self.sms.awaitResponse(str(self.number))
            if response == None: # Meant to avoid timeout none issue
                self.sms.send(str(self.number), f"Timeout: {adminConsoleExit}") # Timeout
                self.logger.adminTimeout(str(self.number))
            else:
                content = response.content.upper() # Update content
        
        # Quitting admin mode.
        self.sms.send(str(self.number), adminConsoleExit)

    def getContent(self):
        # Set messages.
        initialMessage = "Enter the message you would like to send."
        confirmationMessage = "Type 'YES' to confirm, or 'NO' to cancel."
        failedMessage = "Please enter the corrected message."
        self.sms.send(str(self.number), initialMessage)
        # Get content.
        announcement = None
        while announcement == None:
            contentRaw = self.sms.awaitResponse(str(self.number))
            if contentRaw == None:
                return None
            content = contentRaw.content
            if content.upper() == 'EXIT':
                return None
            contentConfirm = f"To confirm, you would like to send the following announcement: {content}"
            self.sms.send(str(self.number), contentConfirm)
            self.sms.send(str(self.number), confirmationMessage)
            confirmationRaw = self.sms.awaitResponse(str(self.number))
            if confirmationRaw == None:
                return None
            confirmation = confirmationRaw.content.upper()
            if confirmation == 'YES':
                announcement = content
                return announcement
            else:
                self.sms.send(str(self.number), failedMessage)
            
    def announce(self):
        announceInit = "You've entered announcement mode. To exit at any time, text 'EXIT'."
        onSuccess = "Announcement queued!"
        self.sms.send(str(self.number), announceInit)
        
        announcement = self.getContent()
        if announcement == None:
            return False
        school = self.getSchool()
        if school == None:
            return False
        grade = self.getGrade()
        if school == None:
            return False

        numbers = self.getNumbers(school, grade)
        self.sms.send(str(self.number), onSuccess)
        self.massSend(announcement, numbers)
        self.logger.adminAnnounce(self.number, announcement, school, grade)
    
    def getSchool(self):
        initialMessage = "Enter the target school (NNHS, NSHS), or * for all."
        invalidMessage = "That's not a valid school. Try again."
        self.sms.send(str(self.number), initialMessage)
        school = None
        while school == None:
            rawContent = self.sms.awaitResponse(str(self.number))
            if rawContent == None:
                return False
            content = rawContent.content.upper()
            if content == 'NNHS':
                school = (SchoolName.NEWTON_NORTH)
                return school
            elif content == 'NSHS':
                school = (SchoolName.NEWTON_SOUTH)
                return school
            elif content == '*':
                school = (SchoolName.NEWTON_NORTH, SchoolName.NEWTON_SOUTH)
                return school
            else:
                self.sms.send(str(self.number), invalidMessage)

    def getGrade(self):
        initialMessage = "Enter the target grade or grades, or * for all. If entering multiple integers seperate them by spaces."
        failedMessage = "You didn't enter any grades! Try again."
        self.sms.send(str(self.number), initialMessage)
        grades = ['9', '10', '11', '12']
        grade = None
        while grade == None:
            rawContent = self.sms.awaitResponse(str(self.number))
            if rawContent == None:
                return None
            content = rawContent.content.upper()
            if content == "*":
                grade = grades
                return grade
            else:
                rawArray = content.split(' ')
                array = []
                for grade in rawArray:
                    if grade in grades:
                        array.append(int(grade))
                if len(array) > 0: 
                    grade = array
                    return grade
                else:
                    self.sms.send(str(number), failedMessage)

    def help(self):
        helpMessage = "Enter 'ANNOUNCE' to send an announcement. Enter 'ANALYTICS' to view analytics."
        self.sms.send(str(self.number), helpMessage)
        return True
    
    def getNumbers(self, schools: tuple, grades: list):
        studentNumbers = []
        for school in schools:
            db = DatabaseHandler(school)
            for grade in grades:
                students = db.getStudentsByGrade(grade)
                for student in students:
                    studentNumbers.append(student.number)
        return studentNumbers

    def massSend(self, message: str, numbers: list):
        for number in numbers:
            self.sms.send(number, message)
            time.sleep(1)

    def analytics(self):
        db = {
            SchoolName.NEWTON_NORTH: DatabaseHandler(SchoolName.NEWTON_NORTH),
            SchoolName.NEWTON_SOUTH: DatabaseHandler(SchoolName.NEWTON_SOUTH)
        }
        northUsers = len(db[SchoolName.NEWTON_NORTH].getStudents())
        southUsers = len(db[SchoolName.NEWTON_SOUTH].getStudents())

        southGrades = [] 
        northGrades = []

        for grade in range(9, 13):
            southGrades.append(len(db[SchoolName.NEWTON_SOUTH].getStudentsByGrade(grade)))
            northGrades.append(len(db[SchoolName.NEWTON_NORTH].getStudentsByGrade(grade)))

        message = f"North: {northUsers} users. Grade 9: {northGrades[0]}, 10: {northGrades[1]}, 11: {northGrades[2]}, 12: {northGrades[3]} | South: {southUsers} users. Grade 9: {southGrades[0]}, 10: {southGrades[1]}, 11: {southGrades[2]}, 12: {southGrades[3]} | Total abSENT Users: {northUsers + southUsers}"

        self.sms.send(str(self.number), message)
        return True