
from course.models import *
from datawarehouse import datawarehouse
from datawarehouse.helpers import *
import datetime
import os 
from .logger import canvas_logger
from .logger import crf_logger
import sys
from configparser import ConfigParser
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException


config = ConfigParser()
config.read('config/config.ini')
API_URL = config.get('canvas','prod_env') #'prod_env')
API_KEY = config.get('canvas', 'prod_key')#'prod_key')



########### HELPERS ################

def code_to_sis(course_code):
    middle=course_code[:-5][-6:]
    sis_id="SRS_%s-%s-%s %s" % (course_code[:-11], middle[:3],middle[3:], course_code[-5:] )
    return(sis_id)


####################################


def get_requests(outputfile='RequestSummary.csv'):
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    requests = Request.objects.all()
    outFile.write('course_code, subaccount, status, provisioned, date_created')
    total  = r.count()
    counter = 1
    for r in requests:
        if counter % 25 == 0:
            print("%s/%s done" % (counter,total))
        course_code = r.course_requested.course_code
        try:
            subaccount = r.course_requested.course_schools.abbreviation
        except:
            subaccount = 'NA'
        try:
            status = r.canvas_instance.workflow_state
        except:
            status = 'NA'

        try:
            canvas_course = canvas.get_course(r.canvas_instance.canvas_id)
            datecreated = canvas_course.created_at
        except:
            datecreated = 'NA'
        
        provisioned = ''
        outFile.write('%s,%s,%s,%s,%s,', % (course_code, subaccount, status, provisioned, date_created))
        counter +=1






