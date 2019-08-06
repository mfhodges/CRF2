

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


# Import the Canvas class
from canvasapi import Canvas

# Canvas API URL
API_URL = domain
# Canvas API key
API_KEY = key



#--------------- RETREIVEING FROM CANVAS ------------------

def get_user_by_sis(login_id):

    #https://canvas.instructure.com/doc/api/users.html
    # Initialize a new Canvas object
    print("got here")
    canvas = Canvas(API_URL, API_KEY)
    #canvas.get_user(123)
    login_id_user = canvas.get_user(login_id, 'sis_login_id')
    print(login_id_user, login_id_user.attributes)
    print(login_id_user.get_courses()[0].attributes)
    return login_id_user

def get_user_courses(login_id):
    user = get_user_by_sis(login_id)
    return user.get_courses(enrollment_type='teacher')






def search_course(terms):
    #https://github.com/instructure/canvas-lms/blob/master/app/controllers/search_controller.rb
    return None


#--------------- PUTTING IN  CANVAS ------------------

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
