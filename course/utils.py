
from course.models import *
"""

None of these files are good yet, purely copied from last

see: https://github.com/upenn-libraries/accountservices/blob/master/accounts/models.py
about how users are added
"""


def validate_pennkey(pennkey):
    # assumes usernames are valid pennkeys
    try:
        user = User.objects.get(username=pennkey)
    except User.DoesNotExist:
        user = None

    # do a lookup in the data warehouse ?
    return user



def datawarehouse_lookup(pennkey):
    ## connects to the db and makes a query


    #if no results
    return False

def check_site(sis_id,canvas_course_id):
    """
    with this function it can be verified if the course
    use the function get_course in canvas/api.py and if u get a result then you know it exists?
    """

    return None



def update_request_status():
    request_set = Request.objects.all() # should be filtered to status = approved
    print("r",request_set)
    string = ''
    if request_set:
        print("\t some requests - lets process them ")
        string = "\t some requests - dw I processed them "
        for request_obj in request_set:
            st ="\t"+request_obj.course_requested.course_code+" "+ request_obj.status
            print("ok ",st)
            # process request ( create course)

    else:
        string= "\t no requests"
        print("\t no requests")
    #print("how-do!")
    return "how-dy!"





def get_template_sites(user):
    """
    Function that determines which of a user's known course sites can
    be sourced for a Canvas content migration.
    :param request:
    :return course sites:
    """
    from siterequest.models import CourseSite, CANVAS

    pks = []
    for x in user.coursesite_set.all():
        if x.site_platform == CANVAS:
            pks.append(x.pk)
            continue
        if x.has_export:
            pks.append(x.pk)
    return CourseSite.objects.filter(pk__in=pks)
