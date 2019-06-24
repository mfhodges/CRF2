
from __future__ import print_function
from course.models import *
from datawarehouse.datawarehouse import *

import cx_Oracle
from configparser import ConfigParser

"""

None of these files are good yet, purely copied from last

see: https://github.com/upenn-libraries/accountservices/blob/master/accounts/models.py
about how users are added
"""


def validate_pennkey(pennkey):
    # assumes usernames are valid pennkeys
    print("validating pennkey")
    try:
        user = User.objects.get(username=pennkey)
    except User.DoesNotExist:
        # check if in penn db
        print("checking datawarehouse for: ", pennkey)
        user = datawarehouse_lookup(pennkey)
        if user:
            #clean up first and last names

            first_name = user['firstname'].title()
            last_name = user['lastname'].title()

            User.objects.create_user(username=pennkey,first_name=first_name,last_name=last_name,email=user['email'],Profile)
        print("okokok user: ",user)
    # do a lookup in the data warehouse ?
    return user



def datawarehouse_lookup(penn_key):
    ## connects to the db and makes a query
    config = ConfigParser()
    config.read('config/config.ini') # this works
    info = dict(config.items('datawarehouse'))
    #print(info)
    connection = cx_Oracle.connect(info['user'], info['password'], info['service'])
    cursor = connection.cursor()
    cursor.execute("""
        SELECT FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PENN_ID
        FROM EMPLOYEE_GENERAL
        WHERE PENNKEY= :pennkey""",
        pennkey = penn_key)
    for fname, lname, email, penn_id in cursor:
        print("Values:", [fname, lname, email, penn_id])
        return {'firstname':fname, 'lastname':lname, 'email':email, 'penn_id':penn_id}

    #if no results
    return False

def check_site(sis_id,canvas_course_id):
    """
    with this function it can be verified if the course
    use the function get_course in canvas/api.py and if u get a result then you know it exists?
    """

    return None



def update_request_status():
    request_set = Request.objects.all() # should be filtered to status = approved
    print("r",request_set)
    string = ''
    if request_set:
        print("\t some requests - lets process them ")
        string = "\t some requests - dw I processed them "
        for request_obj in request_set:
            st ="\t"+request_obj.course_requested.course_code+" "+ request_obj.status
            print("ok ",st)
            # process request ( create course)

    else:
        string= "\t no requests"
        print("\t no requests")
    #print("how-do!")
    return "how-dy!"





def get_template_sites(user):
    """
    Function that determines which of a user's known course sites can
    be sourced for a Canvas content migration.
    :param request:
    :return course sites:
    """
    from siterequest.models import CourseSite, CANVAS

    pks = []
    for x in user.coursesite_set.all():
        if x.site_platform == CANVAS:
            pks.append(x.pk)
            continue
        if x.has_export:
            pks.append(x.pk)
    return CourseSite.objects.filter(pk__in=pks)
