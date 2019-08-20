from __future__ import absolute_import, unicode_literals
from celery import task
from datetime import datetime
from course import utils
from canvas import api as canvas_api
from course.models import *

@task()
def task_process_approved():
    # this task takes all of the Approved requests and attempts to make a course
    # if it doesnt work then it is locked
    #print("howdy!")
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f = open("course/static/logs/test.log", "a")

    ans = utils.update_request_status()
    print(ans)
    f.write(time+" Now the file has more content! \n\t"+ans+"\n")
    f.close()

# there should be a task that check all courses if they have been created in Canvas
# if they have then course.requested is set to true !

# there should be a task that checks all requests with status == Submitted if they have already been created in Canvas
# if they have been then lock the request ! and create the associated CanvasSite Instance

#def task_check_courses()


#----------- CHECK COURSE IN CANVAS ---------------
# FREQUENCY = NIGHTLY
@task()
def task_check_course_in_canvas():
    """
    check to see if any of the courses that do not have a request object associated with them exist yet in Canvas
    if they do then write to the file and set the course to request_override
    """
    courses = Course.objects.filter(requested=False).filter(requested_override=False)

    for course in courses:
        # if the section doesnt exist then it will return None
        found = canvas_api.find_in_canvas("SRS_"+ course.srs_format())
        if found:
            pass # this course doesnt exist in canvas yet
        else:
            # set the course to requested
            course.requested_override= True
            # check that the canvas site exists
            try:
                CanvasSite.objects.get(canvas_id=found.course_id)
            except:
                pass



#----------- PULL IN CANVAS COURSES ---------------
# FREQUENCY = NIGHTLY
@task()
def process_canvas():
    users = User.objects.all()
    for user in users:
        print("adding for ", user.username)
        updateCanvasSites(user.username)



#----------- CREATE COURSE IN CANVAS ---------------
# FREQUENCY = NIGHTLY
# https://github.com/upenn-libraries/accountservices/blob/master/siterequest/management/commands/process_approved_items.py


## CREATE LOGIN -- USERNAME: PENNKEY, SIS ID: PENN_ID, fullname
@task()
def check_for_account(pennkey):
    user = canvas_api.get_user_by_sis(pennkey)
    if user == None: # no account lets create
        try:
            crf_account = User.objects.get(username=pennkey)
            pennid = crf_account.profile.pennid
            full_name = crf_account.get_full_name()
            canvas_account = canvas_api.create_user(pennkey,pennid,fullname)
            if canvas_account:
                return canvas_account
            else: return None
        except:
            # log error
            pass

@task()
def create_canvas_site():
    ################### STEPS #########################
    # 1. set request to in process
    # 2. Create course in canvas ( check that is doesnt exist first )
    # 2a. Crosslist
    # 2b. add sections
    # 3. enroll faculty and additional enrollments ( check that they have accounts first)
    # 4. Configure reserves
    # 5. Content Migration
    # 6. Create CanvasSite Object and link to Request ( set canvas_instance_id )
    # 7. Set request to Complete
    # 8. Notify with email
    ####################################################
    _to_process = Request.objects.filter(status='APPROVED')
    for request_obj in _to_process:
        serialized = RequestSerializer(request_obj)
        ######## Step 1. Set request to IN_PROCESS ########
        request_obj.status = 'IN_PROCESS'
        request_obj.save()
        course_requested = request_obj.course_requested
        ######## Step 2. Create course in canvas ########
        account = canvas_api.find_account(course_requested.course_schools.canvas_subaccount)
        if account: # account exists
            name_code = "%s %s %s" % (course_requested.course_primary_subject.abbreviation, course_requested.course_number, course_requested.year+course_requested.course_term)
            # check if there is a title override
            if request_obj.title_override: name = name_code + request_obj.title_override
            else: name = name_code + course_requested.course_name
            sis_course_id = 'SRS_'+ course_requested.srs_format()
            print("sis_course_id",sis_course_id)
            term_id = canvas_api.find_term_id(96678, course_requested.year+course_requested.course_term)
            print("going to create",name,',',sis_course_id)
            course = {'name':name,'sis_course_id':sis_course_id,'course_code':sis_course_id,'term_id':term_id}
            canvas_course = account.create_course(course=course)
            print("created",canvas_course)
            # add sections
            # add main one
            canvas_course.create_course_section(course_section={'name':course_requested,'sis_section_id':sis_course_id},enable_sis_reactivation=True)
        else:
            #error log and stop for loop
            pass

        ######## Step 3. enroll faculty and additional enrollments  ########
        enrollment_types = {'INST':'TeacherEnrollment', 'TA':'TaEnrollment', 'ObserverEnrollment', 'DES':'DesignerEnrollment', 'LIB':'DesignerEnrollment'}
        librarian_role_id = '1383'
        for instructor in course_requested.instructors.all():
            # check that they have an account
            user = canvas_api.get_user_by_sis(instructor.username)
            if user == None: # user doesnt exist
                user = canvas_api.create_user(instructor.username, instructor.profile.penn_id, instructor.full_name())
            else:
                canvas_course.enroll_user(enrollment={'user_id':user.id, 'enrollment_type':'TeacherEnrollment' ,'enrollment_state':'active'} )
        additional_enrollments = serializer.data['additional_enrollments']
        for enrollment in additional_enrollments:
            user = enrollment['user']
            role = enrollment['role']
            # check if user exists
            user_canvas = canvas_api.get_user_by_sis(user)
            if user_canvas == None: # user doesnt exist
                user_crf = User.objects.get(username=user)
                user_canvas = canvas_api.create_user(user, user_crf.profile.penn_id, user_crf.full_name())
            if role ='LIB':
                canvas_course.enroll_user(enrollment={ 'user_id':user_canvas.id ,'role_id':librarian_role_id, 'enrollment_type':enrollment_types[role] ,'enrollment_state':'active'} )
            else:
                canvas_course.enroll_user(enrollment={ 'user_id':user_canvas.id ,'enrollment_type':enrollment_types[role] ,'enrollment_state':'active'} )
        ######## Step 4. Configure reserves ########
        if serialized.data['reserves']:
            tabs = canvas_course.get_tabs()
            for tab in tabs:
                if tab.id = 'context_external_tool_139969': # its the reserves !
                    tab.update(hidden=False)
                else:
                    pass

        ######## Step 5. Content Migration ########
        if serialized.data['copy_from_course']:
            canvas_course.create_content_migration(migration_type='course_copy_importer', **kwargs)


        ######## Step 6. Create CanvasSite Object and link to Request ########



        ######## Step 7. Set request to Complete ########


        ######## Step 8. Notify with email ########



# get all approved sites, if a creation fails the site is then locked !
# check that instructors and additional enrollments have canvas accounts
"""
    {'_state': <django.db.models.base.ModelState object at 0x102bc3ba8>,
    'course_requested_id': 'ACCT1019102019B', 'copy_from_course': '',
    'title_override': None, 'additional_instructions': None,
    'reserves': False, 'canvas_instance_id': None,
    'status': 'SUBMITTED',
    'created': datetime.datetime(2019, 8, 11, 23, 34, 52, 868865, tzinfo=<UTC>),
     'updated': datetime.datetime(2019, 8, 11, 23, 34, 52, 868916, tzinfo=<UTC>),
     'owner_id': 1, 'masquerade': ''}
 """
