import base64
import json
import re

import requests
from bs4 import BeautifulSoup
from requests import request

URL_API = '/v2/api'
URL_LOGIN = f'{URL_API}/auth/login'
URL_DASHBOARD = f'{URL_API}/student/dashboard/dashboard'
URL_CALENDAR = f'{URL_API}/calendar/student'
URL_GRADES = f'{URL_API}/student/all_subjects'
URL_PROFILE = f'{URL_API}/profile/get'
URL_MESSAGES = f'{URL_API}/message/getMyMessages'
URL_ABSENCES = f'{URL_API}/student/dashboard/absences'
URL_NOTIFICATIONS = f'{URL_API}/notification/unread'
URL_COURSECONTENT = f'{URL_API}/courseContent/getCourse'
URL_LOG = f'{URL_API}/lesson/student'
URL_RECIPIENTS = f'{URL_API}/message/getRecipients'
URL_UPDATE_ENTRY = f'{URL_API}/submission/updateEntry'
URL_UPLOAD = f'{URL_API}/file/upload'
URL_DELETE_ENTRY = f'{URL_API}/submission/deleteEntry'
URL_CHECK = f'{URL_API}/student/dashboard/toggle_reminder'
URL_LESSON_DETAIL = f'{URL_API}/lesson/get'
URL_GRADE_DETAIL = f'{URL_API}/student/subject_detail'
URL_GET_COURSE = f'{URL_API}/courseContent/getCourse'
URL_CHANGE_LANG = f'{URL_API}/profile/updateLanguage'
URL_NOTIFICATIONS_SETTINGS = f'{URL_API}/profile/updateNotificationSettings'
URL_CHANGE_PASSWORD = f'{URL_API}/auth/setNewPassword'
URL_CHANGE_EMIL = f'{URL_API}/profile/updateProfile'
URL_RECIPIENT_DETAILS = f'{URL_API}/message/getRecipientsDetails'
URL_SEND_MESSAGE = f'{URL_API}/message/sendMessage'
URL_SAVE_REMINDER = f'{URL_API}/student/dashboard/save_reminder'
URL_DELETE_REMIDER = f'{URL_API}/student/dashboard/delete_reminder'
URL_EXTEND_SESSION = f'{URL_API}/auth/extendSession'
URL_GET_GRADE = f'{URL_API}/student/entry/getGrade'
URL_GET_TYPES = f'{URL_API}/grade/getTypes'
URL_CHANGE_SEMESTER = '/v2/?semesterWechsel='
URL_CERTIFICATE = '/v2/student/certificate'
URL_HOMEWORK_OVERVIEW = '/v2/vorstand/homework&klasse'

class user():
    def __init__(self, username_: str, password_: str, domain_: str):
        self.cache_dump = {}
        self.protocol = 'https://'
        self.domain = domain_
        self.username = username_
        self.password = password_
        self.cookies = None

    def reqst(self, url, method='POST', data=None, json=None, cache=None, get_cache=None, **kwargs):
        if get_cache is not None and (temp := self.cache_dump.get(get_cache, False)):
            result = temp
            print(self.cache_dump)
        else:
            result = request(method, self.protocol + self.domain + url, json=json, data=data, cookies=self.cookies,
                             allow_redirects=True, **kwargs)

        if result.text.count('window.location = "https://rgtfo-me.digitalesregister.it/v2/login";'):
            self.request_cookies()
            return self.reqst(url, method=method, data=data, json=json, cache=cache, get_cache=get_cache, **kwargs)

        try:
            result.json()
        except ValueError:
            pass
        else:
            if isinstance(result.json(), dict):
                if error := result.json().get('error', False):
                    raise Exception(f"{error}: {result.json().get('error', False)}")

        if cache is not None:
            self.cache_dump[cache] = result
        return result

    def request_cookies(self):
        class LoginError(Exception):
            pass

        login_payload = dict(username=self.username, password=self.password)
        login = requests.get(self.protocol + self.domain + URL_LOGIN, json=login_payload, allow_redirects=True)
        if 'error' in (data := login.json()).keys() and data['error'] is not None:
            raise LoginError(f"{data['error']}: {data['message']}")
        self.cookies = login.cookies

    def request_dashboard(self, viewFuture=True, **kwargs):
        return self.reqst(URL_DASHBOARD, json={"viewFuture": viewFuture}, **kwargs)

    def request_notifications(self, **kwargs):
        return self.reqst(URL_NOTIFICATIONS, **kwargs)

    def request_profile(self, **kwargs):
        return self.reqst(URL_PROFILE, **kwargs)

    def request_grades(self, **kwargs):
        return self.reqst(URL_GRADES, **kwargs)

    def request_absences(self, **kwargs):
        return self.reqst(URL_ABSENCES, **kwargs)

    def request_log(self, **kwargs):
        return self.reqst(URL_LOG, **kwargs)

    def request_week_calendar(self, date, **kwargs):
        return self.reqst(URL_CALENDAR, json={"startDate": date}, **kwargs)

    def request_messages(self, **kwargs):
        return self.reqst(URL_MESSAGES, **kwargs)

    def request_recipients(self, filter, **kwargs):
        return self.reqst(URL_RECIPIENTS, json={"filter": filter}, **kwargs)

    def request_recipients_details(self, recipients, **kwargs):
        return self.reqst(URL_RECIPIENT_DETAILS, json={"recipientGroups": recipients}, **kwargs)

    def request_entry_deletion(self, submission_item_id, category_id, **kwargs):
        return self.reqst(URL_DELETE_ENTRY, json={"submissionItemId": submission_item_id, "categoryId": category_id}, **kwargs)

    def request_entry_check(self, id, value, **kwargs):
        return self.reqst(URL_CHECK, json={"id": id, "type": "gradeGroup", "value": value}, **kwargs)

    def request_hour_details(self, date, hour, to_hour, class_id, **kwargs):
        return self.reqst(URL_LESSON_DETAIL, json={"date": date, "hour": str(hour), "toHour": to_hour, "classId": class_id},
                     **kwargs)

    def request_subject_detail(self, subject_id, student_id, **kwargs):
        return self.reqst(URL_GRADE_DETAIL, json={"subjectId": subject_id, "studentId": student_id}, **kwargs)

    def request_course(self, class_id, subject_id, **kwargs):
        return self.reqst(URL_GET_COURSE, json={"classId": class_id, "subjectId": subject_id}, **kwargs)

    def request_language_switch(self, lang, **kwargs):
        return self.reqst(URL_CHANGE_LANG, json={"language": lang}, **kwargs)

    def request_email_notifications_change(self, bool, **kwargs):
        return self.reqst(URL_NOTIFICATIONS_SETTINGS, json={"notificationsEnabled": bool}, **kwargs)

    def request_grade(self, gradeId, **kwargs):
        return self.reqst(URL_GET_GRADE, json={"gradeId": gradeId}, **kwargs)

    def request_types(self, classId, subjectId, **kwargs):
        return self.reqst(URL_GET_TYPES, payload={"classId": classId, "subjectId": subjectId}, **kwargs)

    def request_password_change(self, username, old_password, new_password, **kwargs):
        return self.reqst(URL_CHANGE_PASSWORD,
                     json={"username": username, "oldPassword": old_password, "newPassword": new_password}, **kwargs)

    def request_email_change(self, new_email, password, **kwargs):
        return self.reqst(URL_CHANGE_EMIL, json={"email": new_email, "password": password}, **kwargs)

    def request_reminder_save(self, date, text, **kwargs):
        return self.reqst(URL_SAVE_REMINDER, json={"date": date, "text": text}, **kwargs)

    def request_reminder_deletion(self, id, **kwargs):
        return self.reqst(URL_DELETE_REMIDER, json={"id": id}, **kwargs)

    def request_semester_change(self, sem, **kwargs):
        return self.reqst("https://rgtfo-me.digitalesregister.it/v2/", params=('semesterWechsel', str(sem)), **kwargs)

    def request_base_html(self, **kwargs):
        return self.reqst("/v2/", **kwargs)

    def parse_certificate(self, ):
        arr = BeautifulSoup(self.request_base_html(cache='html', get_cache='html'), 'html.parser').find_all("td", {
            "class": "padding-cell"})
        dic = {}
        for i in range(0, len(arr), 2):
            dic[arr[i].text] = arr[i + 1].text
        return dic

    def parse_teachers(self, ):
        return json.loads(
            re.search("(?<=teachers = )(.*)(?=;)", self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_teachers_object(self, ):
        return json.loads(
            re.search("(?<=teachersObject = )(.*)(?=;)", self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_lesson_types(self, ):
        return json.loads(
            re.search("(?<=lessontypes = )(.*)(?=;)", self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_rooms(self, ):
        return json.loads(
            re.search("(?<=rooms = )(.*)(?=;)", self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_subjects(self, ):
        return json.loads(
            re.search("(?<=subjects = )(.*)(?=;)", self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_classes(self, ):
        return json.loads(
            re.search("(?<=classes = )(.*)(?=;)", self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_grade_types(self, ):
        return json.loads(
            re.search("(?<=gradeTypes = )(.*)(?=;)", self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_observation_types(self, ):
        return json.loads(
            re.search("(?<=observationTypes = )(.*)(?=;)", self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_calendar_time_grid_objects_without_gaps(self, ):
        return json.loads(re.search("(?<=calendarTimeGridObjectsWithoutGaps = )(.*)(?=;)",
                                    self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_student_absence_time_grid_objects(self, ):
        return json.loads(re.search("(?<=studentAbsenceTimeGridObjects = )(.*)(?=;)",
                                    self.request_base_html(cache='html', get_cache='html').text).group())

    def parse_new_lesson_time_grid_array(self, ):
        return json.loads(re.search("(?<=newLessonTimeGridArray = )(.*)(?=;)",
                                    self.request_base_html(cache='html', get_cache='html').text).group())

    # message sending has been removed
    # def send_message(sendable):
    #     return self.reqst(URL_SEND_MESSAGE, payload=sendable))

    # TODO: homework overview
    # TODO: file uploader
    # TODO: entry updater
