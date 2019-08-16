from __future__ import absolute_import, unicode_literals
from celery import task
from datetime import datetime
from course import utils

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



@task()
def task_check_course_in_canvas():
    """
    check to see if any of the courses that do not have a request object associated with them exist yet in Canvas
    if they do then write to the file and set the course to request_override
    """
    courses = Course.objects.filter(requested=False).filter(requested_override=False)

    for course in courses:
        # if the section doesnt exist then it will return None
        found = find_in_canvas("SRS_"+ course.srs_format())
        if found:
            pass # this course doesnt exist in canvas yet
        else:
            # set the course to requested
            course.requested_override= True
            # check that the canvas site exists
            try:
                CanvasSite.objects.get(canvas_id=found.course_id)

@task()
def process_canvas():
    users = User.objects.all()
    for user in users:
        print("adding for ", user.username)
        updateCanvasSites(user.username)








#----------- CREATE COURSE IN CANVAS ---------------

## CREATE LOGIN -- USERNAME: PENNKEY, SIS ID: PENN_ID


@task():
def create_canvas_site():
    # get all approved sites
    # check that instructors and additional enrollments have canvas accounts
