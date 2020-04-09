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


def SEAS_config(inputfile='SEAS_2020A.csv',outputfile='RESULT_GRADESCOPE_SEAS_2020A.csv'):
    PANOPTO = "context_external_tool_90311"
    GRADESCOPE = "context_external_tool_132117"
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r") 
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    outFile.write("%s,%s,%s,%s\n"% ('canvas_course_id','course_id','status','Gradescope'))
    for line in dataFile:
        canvas_course_id,course_id,status = line.split(",")
        outFile.write("%s,%s,%s"% (canvas_course_id,course_id,status))
        try:
            canvas_course = canvas.get_course(canvas_course_id)
        except:
            print("didnt find course %s" % course_id)
            canvas_course = None
        if canvas_course:
            print("canvas course: %s" % canvas_course.id)
            tabs = canvas_course.get_tabs()
            for tab in tabs:
                # CONFIGURING PANOPTO
                if tab.id == PANOPTO:
                    print("\tfound panopto")
                    try:
                        tab.update(hidden=False,position=3)
                        print("\t added panopto")
                        outFile.write(",%s" % 'yes')
                    except:
                        print("\tfailed panopto %s" % course_id)
                        outFile.write(",%s" % 'no')
                #CONFIGURING GRADESCOPE
                if tab.id == GRADESCOPE:
                    print("\tfound panopto")
                    try:
                        tab.update(hidden=False,position=4)
                        print("\t added gradescope")
                        outFile.write(",%s" % 'yes')
                    except:
                        print("\tfailed panopto %s" % course_id)
                        outFile.write(",%s" % 'no')
                else:
                    #skip this tab
                    pass
            outFile.write("\n")            
        else:
            # finish the line in the text file
            outFile.write(",%s,%s\n" % ('site NA','site NA'))


def add_reserves(inputfile='reserves.csv',outputfile='RESULT_Reserves.csv'):
    RESERVES = "context_external_tool_139969"
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r") 
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    outFile.write("%s,%s,%s,%s\n"% ('canvas_course_id','course_id','status','Reserves'))
    for line in dataFile:

        canvas_course_id = code_to_sis(line.replace("\n","")) 
        outFile.write("%s,"% (canvas_course_id))
        try:
            canvas_course = canvas.get_course(canvas_course_id,use_sis_id=True)
        except:
            print("didnt find course %s" % canvas_course_id)
            canvas_course = None
        if canvas_course:
            print("canvas course: %s" % canvas_course.id)
            tabs = canvas_course.get_tabs()
            for tab in tabs:
                # CONFIGURING RESERVES
                if tab.id == RESERVES:
                    print("\tfound Reserves")
                    try:
                        if tab.visibility != "public":
                            tab.update(hidden=False,position=3)
                            print("\t added reserves")
                            outFile.write(",%s" % 'yes')
                        else:
                            print("\t already reserves ")
                            outFile.write(",%s" % 'active')
                    except:
                        print("\tfailed reserves %s" % canvas_course_id)
                        outFile.write(",%s" % 'no')
                else:
                    #skip this tab
                    pass
            outFile.write("\n")            
        else:
            # finish the line in the text file
            outFile.write(",%s\n" % ('site NA'))


def raise_quota(inputfile='storage_quota.csv',outputfile='RESULT_storage_quota.csv',incr=1000,use_sis_id=False):
    # quota 
    # storage_quota_mb 
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r") 
    dataFile.readline() # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    outFile.write("%s,%s,%s,%s\n"% ('subaccount_id','course_id','old_quota','new_quota'))
    for line in dataFile:
        
        if use_sis_id and line[:4] != 'SRS_':
            canvas_course_id = code_to_sis(line.replace("\n",""))
        else:
            canvas_course_id = line.replace("\n","")
        
        try:
            canvas_course = canvas.get_course(canvas_course_id,use_sis_id=use_sis_id)
            outFile.write("%s,%s,"% (canvas_course.account_id,canvas_course_id))
        except:
            canvas_course = None
            outFile.write("%s,%s,"% ('ERR',canvas_course_id))
        if canvas_course:
            old_quota = canvas_course.storage_quota_mb
            print("old quota ", old_quota)
            new_quota= old_quota+incr
            print("new quota ", new_quota)
            try:
                canvas_course.update(course={'storage_quota_mb':new_quota})
            except:
                new_quota = 'ERROR'
                print('\t failed to raise quota (%s)' % canvas_course_id)
            
            outFile.write("%s,%s\n" % (old_quota,new_quota))
        else: 
            # no canvas course
            outFile.write("%s,%s\n" % ("NA","NA"))
    
def create_quota_file(inputfile='mystorage_quota.csv',outputfile='storage_quota.csv',incr=1000,use_sis_id=False):
    # quota 
    # storage_quota_mb 
    # make sure you remove the unnecessary columns and then filter by storage used >80

    SUB_ACCOUNTS = ['99243','99237','132280','107448','132413','128877','99241','99244','99238','99239','131752','131428','99240','132153','82192']
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r") 
    dataFile.readline() # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    outFile.write("sis_id\n")
    for line in dataFile:
        canvas_id, sis_id, account_id, storage_used, all_used = line.replace("\n","").split(",")
        if account_id in SUB_ACCOUNTS:
            try:
                canvas_course = canvas.get_course(canvas_id)
                #print(canvas_id,storage_used,canvas_course.storage_quota_mb)
                percentage_used = float(storage_used)/round(int(canvas_course.storage_quota_mb))
                #print("\t percentage used ",percentage_used)
                if percentage_used >= 0.79:
                    print("\t %s needs to be increased" % sis_id)
                    outFile.write("%s\n" % sis_id)
            except:
                print("couldnt find course %s" % sis_id)
    print("raise_quota(use_sis_id=True)")


def start_quota_report():
    # DOESNT WORK YET
    canvas = Canvas(API_URL, API_KEY)
    account = canvas.get_account(96678)
    report = account.create_report('course_storage_csv',parameters={"enrollment_term_id": "6055"})
    print(report)
    print(report.to_json())



def find_unconfirmed_emails(inputfile='2020A_Enrollments.csv',outputfile='RESULT_2020A_Enrollments.csv'):
    total = 27291 # hard coded 
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r") 
    dataFile.readline() # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"a")
    outFile.write("%s,%s\n"% ('canvas_user_id','email_status'))
    counter = 1
    for line in dataFile:
        if counter % 25 == 0:
            print("%s/%s done" % (counter,total))
        canvas_user_id,pennkey = line.replace("\n","").split(",")
        user = canvas.get_user(canvas_user_id)
        email_status = 'NONE'
        communication_channels = user.get_communication_channels()
        for c in communication_channels:
            # we only want the first one! 
            try:
                email_status = c.workflow_state
            except:
                pass 
            break
    
        if email_status == 'NONE' or email_status == 'unconfirmed':
            outFile.write("%s,%s\n" % (canvas_user_id,email_status))
    
        counter +=1

        

def unconfirmed_email_check_school(inputfile='RESULT_2020A_Enrollments.csv',outputfile='REMEDIATE_2020A_Enrollments.csv'):
    # given the unconfirmed emails list, checks in the original file if they have multiple enrollments
    # if they have multiple enrollments, check if any all of the enrollments are in schools we do not support
    # if this is the case, write this user down in a separate file
    # otherwise, write them in a file that will then be remediated.  
    total = 5893 # HARDCODED
    SUB_ACCOUNTS = ['99243','99237','128877','99241','99244','99238','99239','131428','99240','132153','82192']
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r") 
    dataFile.readline() # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    outFile.write("%s,%s,%s\n"% ('canvas_user_id','email_status','can_remediate'))
    counter =1
    for line in dataFile:
        if counter % 25 == 0:
            print("%s/%s done" % (counter,total))
        
        canvas_user_id,email_status = line.replace("\n","").split(",")
        user = canvas.get_user(canvas_user_id)
        user_enrollments = user.get_courses() # should we limit by term?
        not_supported_school = True
        for course in user_enrollments:
            try:
                if str(course.account_id) in SUB_ACCOUNTS:
                    not_supported_school = False
                    break # will this stop from iterating through the rest of the list? 
            except:
                print("\t (%s) error with user %s" % (counter, canvas_user_id))
            # check if the account id is in the list of sub accounts
            # if it is not_supported_school = False
        
        # we can remediate this user's account if the final column is False!
        outFile.write("%s,%s,%s\n" % (canvas_user_id,email_status,not_supported_school))
        counter+=1
    

def verify_email_list(inputfile,outputfile='Errors_Emails.txt'):
    total = 5893 # HARDCODED
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r") 
    dataFile.readline() # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    outFile.write("%s,%s\n"% ('canvas_user_id','email_status'))
    counter =1
    for line in dataFile:
        if counter % 25 == 0:
            print("%s/%s done" % (counter,total))
        user_id = line.replace("\n","")
        try:
            is_verified = verify_first_email(user_id)
            if is_verified:
                outFile.write("%s,%s\n"% (user_id,'confirmed'))
            else:
                outFile.write("%s,%s\n"% (user_id,'needs check'))
        except:
            outFile.write("%s,%s\n"% (user_id,'error'))

def check_dummy_email_deleted(user_id):
    DUMMY = 'test@gmail.com'
    canvas = Canvas(API_URL, API_KEY)
    user = canvas.get_user(user_id)
    communication_channels = user.get_communication_channels()
    found = False
    for comm_channel in communication_channels:
        if comm_channel.address == DUMMY:
            found= True
            if comm_channel.workflow_state == 'deleted':
                return True
            else:
                return False # ahh it is stll active!
    
    if found:
        print("\t Dummy email wasnt deleted for user %s" % (user_id))
        return False
    else:
        return True 

def check_verified_email(user_id,address):
    canvas = Canvas(API_URL, API_KEY)
    user = canvas.get_user(user_id)
    communication_channels = user.get_communication_channels()
    for comm_channel in communication_channels:
        if comm_channel.address == address:
            # return True if workflow
            if comm_channel.workflow_state == 'active':
                return True
            else:
                return False
    print("\t Couldn't find former email %s for user %s" % (address,user_id))
    return False


def verify_first_email(user_id):
    canvas = Canvas(API_URL, API_KEY)
    user = canvas.get_user(user_id)
    communication_channels = user.get_communication_channels()
    for comm_channel in communication_channels:
        # verify the first one by re-creating it but auto-verify the new one
        if comm_channel.type =='email': 
            dummy_channel = user.create_communication_channel(communication_channel={'address':'test@gmail.com','type':'email'},skip_confirmation=True)
            #print(dummy_channel.to_json())
            email = comm_channel.address
            #print(comm_channel.to_json())
            comm_channel.delete()
            new_channel = user.create_communication_channel(communication_channel={'address':email,'type':'email'},skip_confirmation=True)
            dummy_channel.delete()
            
            # check that email is verified
            email_is_verified = check_verified_email(user_id,email)
            if email_is_verified == False:
                print("\t email not verified for user %s" % user_id)

            # check that dummy is deleted
            dummy_is_deleted = check_dummy_email_deleted(user_id)
            if dummy_is_deleted==False:
                print("\t dummy not deleted for user %s" % user_id)

            if dummy_is_deleted and email_is_verified:
                return True
            else:
                return False
        break            

    return False




def SEAS_raise_quota(outputfile='RESULT_SEAS_storage_quota.csv'):
    # quota 
    # storage_quota_mb 
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    #file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = ['1487140','1493453','1488890','1490144','1493525','1493544','1494663','1495105','1495910','1494658','1488896','1494771','1491170','1495345','1489898','1493206','1493738','1495881','1494074','1490137','1495656','1495954','1489852','1495911','1496305','1495306','1495114','1495256','1493543','1491099','1493409','1490118','1494387','1493641','1494351','1490145','1490149','1493555','1495344','1493334','1495631','1495765','1504523','1494056','1495257','1490155','1493255','1493553','1494273','1494700','1495940','1490138','1489864','1495434','1495176','1493460','1488864','1484692','1490156','1493638','1494050','1495534','1494981','1494699','1490151','1486075','1494220','1495513','1494775','1496705','1496258','1489222','1490141','1494198','1491266','1494345','1495104','1495447','1494382','1478531','1493228','1494164','1493455','1495529','1504521','1494105','1488889','1493611','1491832','1495212','1495970','1490154','1493633','1491320','1484812','1490136','1493554','1496106','1490116','1493600','1493526','1493551','1493601','1494669','1495652','1491865','1495022','1495107','1493725','1494766','1494576','1495185','1486807','1494585','1491806','1493975','1495432','1487239','1490135','1490140','1494344','1503867','1493454','1491072','1493726','1494461','1494989','1495106','1495159','1493634','1494618','1495630','1495976','1488894','1491566','1491864','1493218','1494769','1495431','1487238','1489366','1490065','1490143','1495034','1495305','1497172','1488895','1488897','1490142','1490150','1491268','1493796','1494333','1494605','1488863','1490148']
    
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    outFile.write("%s,%s,%s,%s\n"% ('subaccount_id','course_id','old_quota','new_quota'))
    for canvas_course_id in dataFile:
        
        try:
            canvas_course = canvas.get_course(canvas_course_id)
            outFile.write("%s,%s,"% (canvas_course.account_id,canvas_course_id))
        except:
            canvas_course = None
            outFile.write("%s,%s,"% ('ERR',canvas_course_id))
        if canvas_course:
            old_quota = canvas_course.storage_quota_mb
            print("old quota ", old_quota)
            new_quota= 4000
            print("new quota ", new_quota)
            if old_quota > new_quota:
                new_quota = old_quota # DONT LOWER THE QUOTA!! 
            try:
                canvas_course.update(course={'storage_quota_mb':new_quota})
            except:
                new_quota = 'ERROR'
                print('\t failed to raise quota (%s)' % canvas_course_id)
            
            outFile.write("%s,%s\n" % (old_quota,new_quota))
        else: 
            # no canvas course
            outFile.write("%s,%s\n" % ("NA","NA"))




def libGuideUsage(inputfile,outputfile='LibGuides_Canvas_2020A.csv'):
    total = 6124 # HARDCODED
    canvas = Canvas(API_URL, API_KEY)
    my_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(my_path, "ACP/data", inputfile)
    dataFile = open(file_path, "r") 
    dataFile.readline() # THIS SKIPS THE FIRST LINE
    outFile = open(os.path.join(my_path, "ACP/data", outputfile),"w+")
    outFile.write("%s,%s,%s\n"% ('canvas_course_id','course_id','libguide'))
    counter =0
    for line in dataFile:
        counter+=1
        if counter % 25 == 0:
            print("%s/%s done" % (counter,total))
        
        canvas_course_id, course_sis_id, canvas_account_id, status = line.replace("\n","").split(',')
        try:
            canvas_course = canvas.get_course(canvas_course_id)
            tabs = canvas_course.get_tabs()
            libguide = False
            for tab in tabs:
                if tab.id =='context_external_tool_89961':
                    #print(course_sis_id, tab.id,tab.label,tab.visibility)
                    if tab.visibility == 'admins': # the tab is not active
                        pass 
                    else:
                        libguide = True
                    break # dont continue with the loop! 
                
            outFile.write("%s,%s,%s\n"% (canvas_course_id,course_sis_id,libguide))
        except:
            outFile.write("%s,%s,%s\n"% (canvas_course_id,course_sis_id,'ERROR'))
            


def test():
    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(1494867)
    tabs = course.get_tabs()
    counter = 1
    libguide=False
    for tab in tabs:
        print(counter)
        if tab.id =='context_external_tool_89961':
            print(tab.id,tab.label,tab.visibility)
            if tab.visibility == 'admins':
                pass # the tab is not active
            else:
                libguide = True
            break
        counter+=1
    print(counter,libguide)