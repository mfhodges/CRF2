from django.contrib import admin
from . models import Course, Notice, Request, School, Subject, AutoAdd
from admin_auto_filters.filters import AutocompleteFilter



"""
can implement EXACT search by instructor username, course code, or course title

"""
class CourseAdmin(admin.ModelAdmin):
    list_display =['course_code','course_name','get_instructors','get_subjects','get_schools','course_term','course_activity','requested']

    list_filter = (
        ('requested','course_activity','course_term','course_schools')
    )
    search_fields = ('instructors__username','course_code','course_name')
    readonly_fields = ['created','updated','owner'] # maybe add requested to here.
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "course":
            kwargs["queryset"] = Course.objects.filter(course_schools__abbreviation=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


"""
can implement EXACT search by user that made the request or masquerade, course code

"""
class RequestAdmin(admin.ModelAdmin):
    list_display =['course_requested','status','requestors','created','updated',]
    list_filter = (
        ('status',)
    )
    search_fields = ('owner__username','masquerade','course_requested__course_code')
    readonly_fields = ['created','updated','owner','masquerade']
    #def formfield_for_manytomany(self, db_field, request, **kwargs):
    #    if db_field.name == "request":
    #        kwargs["queryset"] = Course.objects.filter(course_schools__abbreviation=request.user)
    #    return super().formfield_for_manytomany(db_field, request, **kwargs)

    def requestors(self,object):
        if object.masquerade != '': return object.owner.username + " (" + object.masquerade +") "
        return object.owner.username

admin.site.register(Course, CourseAdmin)
admin.site.register(Request,RequestAdmin)
admin.site.register(Notice)
admin.site.register(School)
admin.site.register(Subject)
admin.site.register(AutoAdd)


# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Admin_site

# https://medium.com/@hakibenita/how-to-turn-django-admin-into-a-lightweight-dashboard-a0e0bbf609ad

#https://medium.com/crowdbotics/how-to-add-a-navigation-menu-in-django-admin-770b872a9531
