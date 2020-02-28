# script that creates Requests in the CRF based on the final SIS ID file.
# the requests are then all approved and proceed from this script
# also any additional site configurations are then implemented 

from canvasapi import Canvas
#from .course.models import *
#from .datawarehouse import datawarehouse

import os 
from logger import canvas_logger
from logger import crf_logger



def test_log():
	canvas_logger.info("canvas test")
	crf_logger.info("crf test?!")


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def create_requests(file):

	for id in courseList:
		# find in CRF
		course = get_or_none(Course,course_code=id.replace(" ","").replace("-",""))
		if course:
			# create request
			# mark request as approved
			pass
		else:
			#LOG
			pass

def process_requests():
	# Processes in batch 

	pass


def config_sites(file,capacity):

	inc_storage(file,capacity)
	enable_lti(file)
	publish_sites(file)
	

def copy_content(file):
	pass

def publish_sites(file):

	pass

def enable_lti(file,):
	
	pass

def inc_storage(file,capacity):
	pass

"""
Pre-populate with Resources: copy content from a site that has resources for first time Canvas users and for async/sync online instruction. Also set on the homepage that this site has been created for ‘Academic Continuity During Disruption’. Info about the closure could also be shared.
Storage Quota: increase the storage quota from the standard 1GB to 2GB.
Enable LTIs: automatically configure Panopto.
Automatically publish the site once created.


"""