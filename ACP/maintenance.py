

"""
This code is to help do some maintence in the CRF and  in Canvas

"""

from course.models import *
from datawarehouse import datawarehouse
from datawarehouse.helpers import *
import datetime
import os 
from .logger import canvas_logger
from .logger import crf_logger
import sys
from configparser import ConfigParser


################ HELPERS ################

def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


################ MAIN CODE ################

def check_canceled(yearterm,outputfile='checkingCanceled.txt'):
    term = yearterm[-1]
    year = yearterm[:-1]
    requests = Request.objects.filter(course_requested__course_term=term,course_requested__year=year)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data/", outputfile)
    f= open(file_path,"w+")
    for r in requests: 
        course = r.course_requested
        if is_canceled(course.course_code)
            f.write("CANCELED:%s\n" % course.course_code)

def delete_canceled(inputfile='checkingCanceled.txt'):
    pass



def check_requests(yearterm):
    """
    for a given term make sure that if a crosslisted course is requested that it has its secondary pointing to the request.
    """
    term = yearterm[-1]
    year = yearterm[:-1]
    courses = Course.objects.filter(
        year=year,
        course_term=term,
        primary_crosslist__isnull=False,
        requested=False
        )
    for course in courses:
        primary_cx = get_or_none(Course,course_id=course.primary_crosslist)
        if primary_cx:
            try:
                primary_req = primary_cx.request
            except:
                #no request??? 
                print("no request found for primary course %s" % primary_cx.course_code)
                primary_req = None
            if primary_req:
                course.crosslisted_request = primary_req
                course.save()



            
