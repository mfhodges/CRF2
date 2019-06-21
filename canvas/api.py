

import json
import re
import requests
from configparser import ConfigParser
# here are most of the basic API requests that should support the CRF

config = ConfigParser()
config.read('config/config.ini')
domain = config.get('canvas', 'prod_env')
key = config.get('canvas', 'prod_key')
headers = {
    'Authorization': 'Bearer %s' % (key)
}



def get_course(course_id):
    #GET /api/v1/courses/:id

    url = domain + '/api/v1/courses/' + str(course_id)
    response = requests.get(url,headers=headers)
    r_json = response.json()
    #print(r_json)
    return(r_json)




def get_course_users(course_id):
    #GET /api/v1/courses/:course_id/users
    # enrollment_type[] Allowed values: teacher, student, student_view, ta, observer, designer
    # returns teachers, ta, and designers of a course
    data = {
        'enrollment_type[]':['teacher','ta']
    }
    url = domain + '/api/v1/courses/%s/search_users' % (str(course_id))
    response = requests.get(url,headers=headers,data=data)
    print(response.status_code, url)
    if response.status_code != 200:
        return {"error" : response.status_code} # maybe return something better/more easily identifiable ?
    r_json = response.json()
    return [x['login_id'] for x in r_json]


def search_course(terms):
    #https://github.com/instructure/canvas-lms/blob/master/app/controllers/search_controller.rb
    return None




"""
#######################################
########### EXAMPLE COURSE ############
#######################################
{
   'id':1448756,
   'name':'Bad Link Testing',
   'account_id':96678,
   'uuid':'TDaK94IomVMXoYKPudVwcP4YoERhhleVkTgd4PWw',
   'start_at':'2019-04-01T14:59:31Z',
   'grading_standard_id':None,
   'is_public':False,
   'created_at':'2019-04-01T14:56:39Z',
   'course_code':'zNS-BADLINK-A2019',
   'default_view':'wiki',
   'root_account_id':96678,
   'enrollment_term_id':4373,
   'license':'private',
   'end_at':None,
   'public_syllabus':False,
   'public_syllabus_to_auth':False,
   'storage_quota_mb':1000,
   'is_public_to_auth_users':False,
   'hide_final_grades':False,
   'apply_assignment_group_weights':False,
   'calendar':{
      'ics':'https://canvas.upenn.edu/feeds/calendars/course_TDaK94IomVMXoYKPudVwcP4YoERhhleVkTgd4PWw.ics'
   },
   'time_zone':'America/New_York',
   'blueprint':False,
   'sis_course_id':'zNS-BADLINK-A2019',
   'sis_import_id':None,
   'integration_id':None,
   'enrollments':[
      {
         'type':'student',
         'role':'StudentEnrollment',
         'role_id':2022,
         'user_id':5443278,
         'enrollment_state':'active'
      }
   ],
   'workflow_state':'available',
   'restrict_enrollments_to_course_dates':False
}
"""
