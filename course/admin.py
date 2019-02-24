from django.contrib import admin
from . models import Course, Notice, Request, School, Subject


admin.site.register(Course)
admin.site.register(Request)
admin.site.register(Notice)
admin.site.register(School)
admin.site.register(Subject)


# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Admin_site

# https://medium.com/@hakibenita/how-to-turn-django-admin-into-a-lightweight-dashboard-a0e0bbf609ad

#https://medium.com/crowdbotics/how-to-add-a-navigation-menu-in-django-admin-770b872a9531
