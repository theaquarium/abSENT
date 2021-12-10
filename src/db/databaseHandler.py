from dataStructs import *

import sqlite3

from typing import Tuple

class DatabaseHandler():

    def __init__(self, school: SchoolName, db_path = "abSENT.db"):
        self.classes_id = 0
        self.user_id = 0
        self.teacher_id = 0

        self.db_path = f"data/{school.name}_{db_path}"
        
        self.reset()

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        create_student_directory = """
        CREATE TABLE IF NOT EXISTS student_directory (
                student_id INTEGER PRIMARY KEY,
                number TEXT,
                first_name TEXT,
                last_name TEXT,
                school TEXT,
                grade TEXT
            )
            """
        create_teacher_directory = """
        CREATE TABLE IF NOT EXISTS teacher_directory (
                teacher_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                school TEXT
            )
            """
        create_classes = """
        CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY,
                teacher_id INTEGER,
                block TEXT,
                student_id INTEGER,
                FOREIGN KEY(teacher_id) REFERENCES student_directory(teacher_id),
                FOREIGN KEY(student_id) REFERENCES teacher_directory(student_id)
            )
            """
        self.cursor.execute(create_student_directory)
        self.cursor.execute(create_teacher_directory)
        self.cursor.execute(create_classes)

    def reset(self):
        import os
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # Generate new ids for user, teacher, and class
    def newUserID(self):
        self.user_id += 1
        return self.user_id
    
    def newTeacherID(self):
        self.teacher_id += 1
        return self.teacher_id

    def newClassID(self):
        self.classes_id += 1
        return self.classes_id

    def getTeacher(self, teacher: Teacher):
        if teacher.id == None:
            query = f"SELECT * FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
        else:
            query = f"SELECT * FROM teacher_directory WHERE teacher_id = '{teacher.id}' LIMIT 1"
        return self.cursor.execute(query).fetchone()
    
    def getStudent(self, student: Student):
        if student.id == None:
            query = f"SELECT * FROM student_directory WHERE number = '{student.number}' LIMIT 1"
        else:
            query = f"SELECT * FROM student_directory WHERE student_id = '{student.id}' LIMIT 1"
        return self.cursor.execute(query).fetchone()
    
    def getTeacherID(self, teacher: Teacher):
        if teacher.id == None:
            query = f"SELECT teacher_id FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
            res = self.cursor.execute(query).fetchone()
            if res == (1,):
                return res[0]
            else:
                return None
        else:
            return teacher.id
    
    def getStudentID(self, student: Student):
        if student.id == None:
            query = f"SELECT student_id FROM student_directory WHERE number = '{student.number}' LIMIT 1"
            res = self.cursor.execute(query).fetchone()
            if res == (1,):
                return res[0]
            else:
                return None
        else:
            return student.id
        
    def addStudentToUserDirectory(self, student: Student):
        new_id = self.newUserID()
        query = f"""
        INSERT INTO student_directory VALUES (
            '{new_id}',
            '{student.number}',
            '{student.first}',
            '{student.last}',
            '{student.school}',
            '{student.grade}'
            )
        """
        self.cursor.execute(query)
        self.connection.commit()
        return new_id
    
    def addTeacherToTeacherDirectory(self, teacher: Teacher):
        new_id = self.newTeacherID()
        query = f"""
        INSERT INTO teacher_directory VALUES (
            '{new_id}',
            '{teacher.first}',
            '{teacher.last}',
            '{teacher.school}'
            )
        """
        self.cursor.execute(query)
        self.connection.commit()
        return new_id
    
    def addClassToClasses(self, teacher_id: int, block: SchoolBlock, student_id: int) -> Tuple[bool, int]:
        str_block = BlockMapper()[block] 
        if teacher_id == None or str_block == None or student_id == None:
            return False, None
        new_id = self.newClassID()
        query = f"""
        INSERT INTO classes VALUES (
            '{new_id}',
            '{teacher_id}',
            '{str_block}',
            '{student_id}'
            )
        """
        self.cursor.execute(query)
        self.connection.commit()
        return True, new_id
    
    # def addStudent(self, student: Student):
    #     res = self.
    #     new_id = self.addStudentToUserDirectory(student)

    # def addStudent(self, student: Student, schedule: Schedule):
    #     res = self.checkIfInUserDirectory(student)
    #     if not res:
    #         for block in schedule:
    #             teacher = schedule[block]
    #             if teacher is not None:
    #                 teacher = self.getTeacher(teacher)
    #                 if 
    #                 if self.checkIfInTeacherDirectory(teacher):
    #                     self.addStudentToClasses(student, teacher, block)
    #                 else:
    #                     print("Teacher not in directory")
    #             else:
    #                 print(f"No class during {block} block")
    #         return True
    #     return False

    # def checkIfInUserDirectory(self, student: Student):
    #     query = f"SELECT * FROM student_directory WHERE student_id = {student.id} LIMIT 1"
    #     if self.cursor.execute(query).fetchone() == (1,):
    #         return True
    #     else:
    #         return False
        
    # def checkIfInTeacherDirectory(self, teacher: Teacher):
    #     query = f"SELECT * FROM teacher_directory WHERE teacher_id = {teacher.id} LIMIT 1"
    #     if self.cursor.execute(query).fetchone() == (1,):
    #         return True
    #     else:
    #         return False

    # def addStudentToClasses(self, student: Student, teacher: Teacher, block: str):
    #     classes_id = self.newClassID()
    #     teacher_id = self.getTeacherID(teacher)
    #     student_id = self.getStudentID(student)
    #     self.cursor.execute("INSERT INTO classes VALUES (?, ?, ?, ?)", (classes_id, teacher_id, block, student_id))
    #     self.connection.commit() 

if __name__ == "__main__":
    kevin = Student("6176868207", "Kevin", "Yang", SchoolName.NEWTON_SOUTH, 10)

    NORM = Teacher("RYAN", "NORMANDIN", SchoolName.NEWTON_SOUTH)
    PAL = Teacher("ALEX", "PALILUNAS", SchoolName.NEWTON_SOUTH)
    BECKER = Teacher("RACHEL", "BECKER", SchoolName.NEWTON_SOUTH)
    KOZUCH = Teacher("MICAEL", "KOZUCH", SchoolName.NEWTON_SOUTH)
    CROSBY = Teacher("ALAN", "CROSBY", SchoolName.NEWTON_SOUTH)
    RUGG = Teacher("ILANA", "RUGG", SchoolName.NEWTON_SOUTH)

    schedule = Schedule(NORM)

    db = DatabaseHandler(SchoolName.NEWTON_SOUTH)
    db.addStudentToUserDirectory(kevin)
    db.addTeacherToTeacherDirectory(NORM)
    db.addTeacherToTeacherDirectory(BECKER)
    print(db.addClassToClasses(db.getTeacherID(CROSBY), SchoolBlock.A, db.getStudentID(kevin)))
    print(db.getStudent(kevin))
    print(db.getTeacher(NORM))