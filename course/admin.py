from django.contrib import admin
from . models import *
from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

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


    def save_model(self, request, obj, form, change):
        #print("checkin save")
        obj.owner = request.user
        obj.save()

"""
can implement EXACT search by user that made the request or masquerade, course code

"""
class RequestAdmin(admin.ModelAdmin):
    list_display =['course_requested','status','requestors','created','updated',]
    list_filter = (
        ('status',)
    )
    search_fields = ('owner__username','masquerade','course_requested__course_code')
    readonly_fields = ['created','updated','masquerade']
    #def formfield_for_manytomany(self, db_field, request, **kwargs):
    #    if db_field.name == "request":
    #        kwargs["queryset"] = Course.objects.filter(course_schools__abbreviation=request.user)
    #    return super().formfield_for_manytomany(db_field, request, **kwargs)

    def requestors(self,object):
        if object.masquerade != '': return object.owner.username + " (" + object.masquerade +") "
        return object.owner.username

    def save_model(self, request, obj, form, change):
        #print("checkin save")
        obj.owner = request.user
        obj.save()




class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]

# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)


admin.site.register(Course, CourseAdmin)
admin.site.register(Request,RequestAdmin)
admin.site.register(Notice)
admin.site.register(School)
admin.site.register(Subject)
admin.site.register(AutoAdd)
admin.site.register(UpdateLog)


# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Admin_site

# https://medium.com/@hakibenita/how-to-turn-django-admin-into-a-lightweight-dashboard-a0e0bbf609ad

#https://medium.com/crowdbotics/how-to-add-a-navigation-menu-in-django-admin-770b872a9531
