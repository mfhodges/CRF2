# script that creates Requests in the CRF based on the final SIS ID file.
# the requests are then all approved and proceed from this script
# also any additional site configurations are then implemented 


## ONLY RUN THIS FROM home/crf2/ in $ python3 manage.py shell 
## file = the 2nd file created in create_course_list that contains sis ids of courses that haven't been created yet.

from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from course.models import *
from datawarehouse import datawarehouse
import datetime
import os 
from .logger import canvas_logger
from .logger import crf_logger
import sys
from course.tasks import create_canvas_site
from .create_course_list import sis_id_status
from configparser import ConfigParser

config = ConfigParser()
config.read('config/config.ini')
API_URL = config.get('canvas','prod_env') #'prod_env')
API_KEY = config.get('canvas', 'prod_key')#'prod_key')


"""
BEFORE YOU DO ANYTHING PLEASE SYNC INSTRUCTORS AND COURSES WITH SRS!!!


Configurations to run with:

	- publish
	- enable panopto - external_tools/90311
	- copy from: 1502387
	- storage: 2GB

"""




######## TESTS / HELPERS ########

def test_CRF_App():
	x = Course.objects.all()
	print(x[1])

def test_reading(file):
	my_path = os.path.dirname(os.path.abspath(__file__))
	print("path",my_path)
	file_path = os.path.join(my_path, "data/", file)
	print("file path", file_path)
	dataFile = open(file_path, "r") 
	for line in dataFile:
		course = line.replace('\n',"")
		print("'"+course+"'")
		
def test_log():
	canvas_logger.info("canvas test")
	crf_logger.info("crf test?!")

def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None




######## CODE TO USE ########


def create_requests(inputfile='notUsedSIS.txt',copy_site=''):
	# copy_site is the canvas id of a Canvas site inwhich we'd like to copy content from. 
	owner = User.objects.get(username='mfhodges')
	my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
	print("path",my_path)
	file_path = os.path.join(my_path, "ACP/data", inputfile)
	print("file path", file_path)
	dataFile = open(file_path, "r") 
	for line in dataFile:
		#FIND IN CRF	
		id = line.replace('\n',"").replace(" ","").replace("-","")
		course = get_or_none(Course,course_code=id)
		if course: 
			# create request
			try:
				r = Request.objects.create(
					course_requested = course,
					copy_from_course = copy_site,
					additional_instructions = 'Created automatically, contact courseware support for info',
					owner = owner,
					created= datetime.datetime.now()
				)
				r.status = 'APPROVED' # mark request as approved
				r.save()
				course.save() ## you have to save the course to update its request status !
				print("Created request for: %s", line)
			except:
				print("\t Failed to create request for: %s", line)
				# report that this was failed to be created
				crf_logger.info("Failed to create request for: %s", line)

		else:
			#LOG
			print("course not in CRF")
			crf_logger.info("Not in CRF : %s", line)
	print("-> Finished Creating Requests in CRF")
	print("-> Please check `ACP/logs/crf.log` for a list of failed Request creations")
	print("-> NEXT: Please now run `process_requests('%s')`" % inputfile)

def gather_request_process_notes(inputfile='notUsedSIS.txt'):
	# Gathers the `process_notes` for all processed requests
	# Creates a file of all of the process notes for each request (this can be used to find who has a new account)
	# Creates a file of canvas sites that have been created. 
	my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
	file_path = os.path.join(my_path, "ACP/data", inputfile)
	print("file path", file_path)
	dataFile = open(file_path, "r") 
	requestResultsFile = open(os.path.join(my_path,"ACP/data","requestProcessNotes.txt"),"w+")
	canvasSitesFile = open(os.path.join(my_path,"ACP/data","canvasSitesFile.txt"),"w+")
	for line in dataFile:
		#FIND IN CRF	
		id = line.replace('\n',"").replace(" ","").replace("-","")
		course = get_or_none(Course,course_code=id)
		request = get_or_none(Request,course_requested=course)
		if request: # the request exists
			# check if stuck in process -> log error
			if request.status == 'COMPLETED':
				#find canvas site id and write that to a file with the SIS ID
				canvasSitesFile.write("%s,%s\n" % (id, request.canvas_instance.canvas_id))
				requestResultsFile.write("%s | %s\n" %(id,request.process_notes))
			else:
				canvas_logger.info("request incomplete for %s", id)
		else:
			# no request exists? thats concerning.. lets log that
			crf_logger.info("couldnt find request for %s", id)



def process_requests(file='notUsedSIS.txt'):

	# THERE IS A BUG IN THE FOLLOWING FUNCTION THAT DOES NOT ALLOW A CREATION TO FAIL SILENTLY
	create_canvas_site() # runs the task 
	# should wait till the above task is done... 
	print("\t-> Finished Processing Requests in CRF")
	print("\t-> NOW: gathering Request Processing Report in `ACP/data/requestProcessNotes.txt`")
	gather_request_process_notes(file)
	print("-> Finished Generating: `ACP/data/requestProcessNotes.txt`")
	print("-> Please Check `ACP/logs/canvas.log` for a list of incomplete Requests")
	print("-> Please Check `ACP/logs/crf.log` for a list of errors in the CRF")
	print("-> Please Check `ACP/data/requestProcessNotes.txt` for a details on each Request")
	print("-> NEXT: (OPTIONAL) Please now run `config_sites` to configure these sites")
	


"""
		Pre-populate with Resources: copy content from a site that has resources for first time Canvas users and for async/sync online instruction. Also set on the homepage that this site has been created for ‘Academic Continuity During Disruption’. Info about the closure could also be shared.
		Storage Quota: increase the storage quota from the standard 1GB to 2GB.
		Enable LTIs: automatically configure Panopto.
		Automatically publish the site once created.
"""


def config_sites(inputfile="canvasSitesFile.txt",capacity=2,publish=False,tool=None,source_site=None):
	if source_site:
		copy_content(inputfile,source_site)
	if tool:
		enable_lti(inputfile,tool)

	config = {}
	if capacity:
		config['storage_quota_mb'] = capacity
	if publish:
		config['event']='offer'
	if publish or capacity:
		canvas = Canvas(API_URL, API_KEY)
		my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
		print("path",my_path)
		file_path = os.path.join(my_path, "ACP/data", file)
		print("file path", file_path)
		dataFile = open(file_path, "r") # # test6660002020A,1500426
		for line in dataFile:
			canvas_id = line.replace("\n","").split(",")[-1]
			#check that the site exists
			try:
				course_site = canvas.get_course(canvas_id)
			except:
				canvas_logger.info('(inc. quota/publish) failed to find site %s' % canvas_id)
				course_site =None
			if course_site:
				print(course_site)
				course_site.update(course=config)


def copy_content(file,source_site):
	# NOT TESTING THAT THE SOURCE SITE IS VALID
	# √ TESTED 
	canvas = Canvas(API_URL, API_KEY)
	my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
	print("path",my_path)
	file_path = os.path.join(my_path, "ACP/data", file)
	print("file path", file_path)
	dataFile = open(file_path, "r") # # test6660002020A,1500426
	for line in dataFile:
		canvas_id = line.replace("\n","").split(",")[-1]
		#check that the site exists
		try:
			course_site = canvas.get_course(canvas_id)
		except:
			canvas_logger.info('(copy content) failed to find site %s' % canvas_id)
			course_site =None
		if course_site:
			print(course_site)
			contentmigration = course_site.create_content_migration(migration_type='course_copy_importer',settings={'[source_course_id':source_site})


		

def publish_sites(file,capacity):
	# ? TESTED 
	# CAPACITY IS IN MB NOT GB
	canvas = Canvas(API_URL, API_KEY)
	my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
	print("path",my_path)
	file_path = os.path.join(my_path, "ACP/data", file)
	print("file path", file_path)
	dataFile = open(file_path, "r") # # test6660002020A,1500426
	for line in dataFile:
		canvas_id = line.replace("\n","").split(",")[-1]
		#check that the site exists
		try:
			course_site = canvas.get_course(canvas_id)
		except:
			canvas_logger.info('(publish) failed to find site %s' % canvas_id)
			course_site =None
		if course_site:
			print(course_site)
			course_site.update(course={'storage_quota_mb':capacity,'event':'offer'})
	pass

def enable_lti(file,tool):
	#tool = "context_external_tool_90311"
	canvas = Canvas(API_URL, API_KEY)
	my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
	print("path",my_path)
	file_path = os.path.join(my_path, "ACP/data", file)
	print("file path", file_path)
	dataFile = open(file_path, "r") # # test6660002020A,1500426
	for line in dataFile:
		canvas_id = line.replace("\n","").split(",")[-1]
		#check that the site exists
		try:
			course_site = canvas.get_course(canvas_id)
		except:
			canvas_logger.info('(enable tool) failed to find site %s' % canvas_id)
			course_site =None
		if course_site:
			print(course_site)

			course_site.update_tab( tool, {'hidden':'false','position':3})
	pass



