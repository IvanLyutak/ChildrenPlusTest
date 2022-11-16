import pyodbc
import json
from data import config

# Database Connection
connection_to_db = pyodbc.connect(fr'DRIVER={config.DRIVER};'
                                  fr'Server={config.DB_SERVER};'
                                  fr'Database={config.DB_DATABASE};'
                                  fr'UID={config.DB_UID};'
                                  fr'PWD={config.DB_PWD};'
                                  fr'TrustServerCertificate=yes;')


def get_my_courses(idTelegram):
    cursor = connection_to_db.cursor()
    cursor.execute(f"SELECT UserId FROM AspNetUserClaims WHERE ClaimType Like '%/sid%' and ClaimValue = "
                   f"'{idTelegram}'")
    idUser = cursor.fetchall()[0][0]

    cursor.execute(f"SELECT e.EducationItem, ei.Title, g.Beginning, g.Ending FROM UserGroupsRelation g INNER JOIN "
                   f"UserEducationRelation e ON g.Id = e.UserInGroup INNER JOIN EducationItems ei ON e.EducationItem "
                   f"= ei.Id where g.UserInGroup = '{idUser}' and ei.ItemType = 'Курс'")
    results = cursor.fetchall()

    result = []
    for row in results:
        result.append({
            "EducationItem": row[0],
            "title": row[1],
            "beginning": row[2],
            "ending": row[3]
        })
    cursor.commit()
    return result


def get_sequence_lessons(idParent):
    cursor = connection_to_db.cursor()
    cursor.execute(f"SELECT Id, Title FROM EducationItems where ItemType = 'Урок' and Parent = {idParent} ORDER BY seqNo")
    result = []
    for item in cursor.fetchall():
        result.append({
            "id": item[0],
            "title": item[1]
        })
    cursor.commit()
    return result


def get_content_courses(itemType: str, _id: int = None, serialNumber: int = None, testSerialNumber: int = None):
    if itemType == 'Целевая группа':
        cursor = connection_to_db.cursor()
        cursor.execute(f"SELECT Id, ItemType, Title FROM EducationItems where ItemType='{itemType}'")
        results = cursor.fetchall()

        result = []
        for row in results:
            result.append({
                "id": row[0],
                "title": row[2]
            })
        cursor.commit()
        return result

    elif itemType == 'Курс':
        cursor = connection_to_db.cursor()
        cursor.execute(
            f"SELECT Id, Parent, ItemType, Title FROM EducationItems where ItemType='{itemType}' and Parent={_id}")
        results = cursor.fetchall()

        result = []
        for row in results:
            result.append({
                "id": row[0],
                "title": row[3]
            })
        cursor.commit()
        return result

    elif itemType == 'Урок':
        cursor = connection_to_db.cursor()
        cursor.execute(
            f"SELECT Parent, ItemType, Title, ContentId FROM EducationItems where ItemType='{itemType}' and Parent={_id}")
        results = cursor.fetchall()
        result = []
        for row in results:
            result.append({
                "contentId": row[3],
                "title": row[2]
            })
        cursor.commit()
        return result

    elif itemType == 'Контент':
        cursor = connection_to_db.cursor()
        cursor.execute(f"SELECT ContentId, ContentJSON FROM EducationContents where ContentId={int(_id)}")
        content = cursor.fetchall()[0][1]
        if content is not None:
            content = json.loads(content)
            if len(content["Sections"]) == serialNumber:
                cursor.commit()
                return {"finalStage": True}
            cursor.commit()
            return content["Sections"][serialNumber]
        cursor.commit()
        return None

    elif itemType == 'Тест':
        cursor = connection_to_db.cursor()
        cursor.execute(f"SELECT ContentId, ContentJSON FROM EducationContents where ContentId={int(_id)}")
        content = json.loads(cursor.fetchall()[0][1])
        cursor.commit()
        return content["Sections"][serialNumber]["Slides"][testSerialNumber]
    return None


def get_result_course(course_number, idTelegram):
    cursor = connection_to_db.cursor()
    cursor.execute("SELECT ei.Title, ue.EducationItem, ue.Result FROM UserEducationRelation as ue "
                   "INNER JOIN EducationItems AS ei ON ei.Id = ue.EducationItem WHERE ue.UserInGroup = "
                   "(SELECT uer.UserInGroup FROM UserEducationRelation AS uer INNER JOIN UserGroupsRelation AS ugr "
                   "ON ugr.Id = uer.UserInGroup WHERE ugr.UserInGroup = (SELECT UserId FROM AspNetUserClaims "
                   f"WHERE ClaimType Like '%/sid%' and ClaimValue ='{idTelegram}') and uer.EducationItem = {course_number}) and "
                   f"ue.EducationItem != {course_number}")
    results = []
    for row in cursor.fetchall():
        results.append({
            "Title": row[0],
            "EducationItem": row[1],
            "Result": row[2]
        })
    cursor.commit()
    return results


def set_end_lesson(educationItem: int, idTelegram: str, result=None, finalCourse: bool = False):

    cursor = connection_to_db.cursor()
    cursor.execute(f"SELECT UserId FROM AspNetUserClaims WHERE ClaimType Like '%/sid%' and ClaimValue = "
                   f"'{idTelegram}'")
    idUser = cursor.fetchall()[0][0]

    # print(idUser)
    # print(educationItem)
    # print("Result test", result)
    
    if result is not None:

        cursor.execute(f"UPDATE UserEducationRelation SET Ending = CURRENT_TIMESTAMP, Result = {result} "
                       f"FROM UserEducationRelation AS uer INNER JOIN UserGroupsRelation AS ugr ON "
                       f"ugr.Id = uer.UserInGroup WHERE ugr.UserInGroup = '{idUser}' and "
                       f"uer.EducationItem = {educationItem}")
        cursor.commit()

        if finalCourse:
            cursor.execute(f"SELECT uer.UserInGroup, (SUM(uer.Result)/COUNT(*)) FROM UserEducationRelation AS uer "
                           f"INNER JOIN UserGroupsRelation AS ugr ON ugr.Id = uer.UserInGroup and uer.Result is not "
                           f"NULL and uer.UserInGroup = (SELECT uer.UserInGroup FROM UserEducationRelation AS uer "
                           f"INNER JOIN UserGroupsRelation AS ugr ON ugr.Id = uer.UserInGroup WHERE ugr.UserInGroup = "
                           f"'{idUser}' and uer.EducationItem = {educationItem}) GROUP BY uer.UserInGroup")

            results = cursor.fetchall()[0]
            cursor.commit()

            cursor.execute(f"UPDATE UserGroupsRelation SET Ending = CURRENT_TIMESTAMP, Result = {results[1]} "
                           f"WHERE Id = '{results[0]}'")
            cursor.commit()


def set_progress(idTelegram, lessonId, lessonStage, finalStage: bool = False):

    cursor = connection_to_db.cursor()
    cursor.execute(f"SELECT ContentId, ContentJSON FROM EducationContents where ContentId={lessonId}")
    numberOfStages = len(json.loads(cursor.fetchall()[0][1])["Sections"])
    cursor.commit()

    cursor.execute(f"SELECT UserId FROM AspNetUserClaims WHERE ClaimType Like '%/sid%' and ClaimValue = "
                   f"'{idTelegram}'")

    idUser = cursor.fetchall()[0][0]
    # print(idUser)

    if numberOfStages > lessonStage:
        progress = int(((lessonStage+1)/numberOfStages)*100)
        # print("Progress", lessonId, progress)

        cursor.execute(f"UPDATE UserEducationRelation SET Progress = {progress} "
                       f"FROM UserEducationRelation AS uer INNER JOIN UserGroupsRelation AS ugr ON "
                       f"ugr.Id = uer.UserInGroup WHERE ugr.UserInGroup = '{idUser}' and "
                       f"uer.EducationItem = {lessonId}")
        cursor.commit()
    else:
        cursor.execute(f"UPDATE UserEducationRelation SET Progress = 100 "
                       f"FROM UserEducationRelation AS uer INNER JOIN UserGroupsRelation AS ugr ON "
                       f"ugr.Id = uer.UserInGroup WHERE ugr.UserInGroup = '{idUser}' and "
                       f"uer.EducationItem = {lessonId}")
        cursor.commit()

    if finalStage:
        cursor.execute(f"UPDATE UserGroupsRelation SET Progress=(SELECT SUM(uer.Progress)/(SELECT COUNT(*) "
                       f"FROM EducationItems where Parent=(SELECT Parent FROM EducationItems where Id={lessonId})) "
                       f"FROM UserEducationRelation AS uer INNER JOIN UserGroupsRelation AS ugr ON ugr.Id = "
                       f"uer.UserInGroup WHERE ugr.UserInGroup = '{idUser}' and uer.Progress is not NULL) FROM "
                       f"UserEducationRelation AS uer INNER JOIN UserGroupsRelation AS ugr ON ugr.Id = uer.UserInGroup "
                       f"WHERE ugr.UserInGroup = '{idUser}' and uer.EducationItem = {lessonId}")
        cursor.commit()