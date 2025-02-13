from dataStructs import *
from textnow.sms import SMS
from database.databaseHandler import *
from database.logger import Logger
from schoology.absence import Absence
from datetime import date
import time
import random

class NotificationDriver:
    
    # Configures a dict of DB objects and a dict of blocks keyed by day as returned by datetime.
    def __init__(self, textnowCreds: TextNowCreds, scCreds: SchoologyCreds):
        self.sms = SMS(textnowCreds)
        # Dict of both DB objects.
        self.db = {
            SchoolName.NEWTON_NORTH: DatabaseHandler(SchoolName.NEWTON_NORTH), 
            SchoolName.NEWTON_SOUTH: DatabaseHandler(SchoolName.NEWTON_SOUTH)
        }
        # Dict of blocks occuring on a given day.
        self.blockDict = {
            0: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.C, SchoolBlock.D, SchoolBlock.E),
            1: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.F, SchoolBlock.G),
            2: (SchoolBlock.C, SchoolBlock.D, SchoolBlock.E, SchoolBlock.F),
            3: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.G, SchoolBlock.E),
            4: (SchoolBlock.C, SchoolBlock.D, SchoolBlock.F, SchoolBlock.G),
            5: None,
            6: None
        }
        # Schoology API hookup.
        self.sc = Absence(scCreds)
        
        # Logging:
        self.logger = Logger()

    # Runtime code, calls the various functions within the class and sends the appropriate messages to people with absent teachers.
    def run(self, date, school: SchoolName):
        self.date = date
        absences = self.getAbsenceList(school)
        print(school)
        if absences == None:
            print("NO DATA AVAILABLE.")
            self.logger.noDataAvailable()
            return False
        notificationList = self.getStudentsToNotify(absences, school) 
        messages = self.genMessages(notificationList)
        attemptSend = self.sendMessages(messages) # returns sucess of message send.
        return attemptSend

    # Fetches absent teachers.
    def getAbsenceList(self, school: SchoolName):
        if school == SchoolName.NEWTON_NORTH:
            absenceList = self.sc.filterAbsencesNorth(self.date)
            self.logger.schoolgyGrabAbsences(SchoolName.NEWTON_NORTH)
        elif school == SchoolName.NEWTON_SOUTH:
            absenceList = self.sc.filterAbsencesSouth(self.date)
            self.logger.schoolgyGrabAbsences(SchoolName.NEWTON_SOUTH)
        else:
            return None
        return absenceList

    # Returns students in each class that a teacher is absent in.
    def getStudentsToNotify(self, absences: list, school: SchoolName):
        notificationList = []
        for teacher in absences:
            for block in self.blockDict[self.date.weekday()]:
                # To-Do: Implement casting between AbsentTeacher and Teacher classes
                queryStudents = self.db[school].queryStudentsByAbsentTeacher(Teacher(teacher.first, teacher.last, school), block)
                if queryStudents != []:
                    # Send notification to each student if there are students to sent to.
                    notificationList.append(NotificationInformation(teacher, queryStudents, block)) 
        return notificationList

    # Generates a dict of messages to send to each student.
    ## Each absent class for a student is smushed into one message to save TextNow API calls.
    def genMessages(self, notificationList: list):
        messageDict = {}
        messageStart = "Hey there! You have absent teachers:\\n"
        for notification in notificationList:
            for student in notification.students:
                messageContent = f"{notification.teacher.first} {notification.teacher.last}\\n    Note: {notification.teacher.note}.\\n"     
                # Map a student its update message. 
                ## Meant to prevent duplicate messages (Dict entries are unique)
                if messageDict.get(student) == None:
                    # Create number entry if it doesn't exist.
                    messageDict[student] = messageStart + messageContent
                else:
                    # Append to existing message.
                    messageDict.update({student: messageDict[student] + messageContent})
        return messageDict

    # Send messages to each student.
    def sendMessages(self, messageDict: dict):
        if len(messageDict) == 0:
            print("NO USERS TO NOTIFY.")
            self.logger.noUsersToNotify()
            return True
        for student in messageDict:
            self.sms.send(str(student.number), messageDict[student])
            self.logger.sentAbsencesNotification(student)
            delay = random.uniform(0.25, 1.0) # Random delay so no get banned from API.
            time.sleep(delay)
            print(f"NOTIFICATION SENT: {str(student.number)}.")
        return True