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
