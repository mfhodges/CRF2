

"""

None of these files are good yet, purely copied from last

see: https://github.com/upenn-libraries/accountservices/blob/master/accounts/models.py
about how users are added
"""



def check_site(sis_id,canvas_course_id):
    """
    with this function it can be verified if the course



    """
    return None



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
