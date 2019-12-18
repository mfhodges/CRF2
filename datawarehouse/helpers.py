# myscript.py
from __future__ import print_function
import cx_Oracle
from configparser import ConfigParser
import string
import logging
from course import utils
import re
from OpenData.library import *
from course.models import *



######
# If you want to omitt a parameter pass '*' instead.
#
#####
def search_course(subject_area,course_number='*',sect_number='*',term='*'):

        config = ConfigParser()
        config.read('config/config.ini')
        # check that term is available!
        info = dict(config.items('datawarehouse'))
        connection = cx_Oracle.connect(info['user'], info['password'], info['service'])
        cursor = connection.cursor()
        cursor.execute("""
        SELECT
          cs.section_id
          || cs.term section,
          cs.section_id,
          cs.term,
          cs.subject_area subject_id,
          cs.tuition_school school_id,
          cs.xlist,
          cs.xlist_primary,
          cs.activity,
          cs.section_dept department,
          cs.section_division division,
          trim(cs.title) srs_title,
          cs.status srs_status,
          cs.schedule_revision
        FROM
          dwadmin.course_section cs
        WHERE
          cs.section_number= :section_number
        AND cs.subject_area= :subject_area
        AND cs.course_number= :course_number
        AND cs.term= :term""",
        term = term,section_number = sect_number,course_number=course_number,subject_area=subject_area)


        for data in cursor:
            print(data)
