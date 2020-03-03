
# testing Provisioning process and other tests
import os 
from logger import canvas_logger
from logger import crf_logger


"""
>>> from ACP.create_course_list import *
>>> create_unused_sis_list(inputfile="test.txt",outputfile="test_out.txt")
"""




################# OTHER  #################


def test_reading(file):
	dataFile = open(file, "r") 
	for line in dataFile:
		course = line.replace('\n',"")
		print("'"+course+"'")
		
def test_log():
	canvas_logger.info("canvas test")
	crf_logger.info("crf test?!")