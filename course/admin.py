from django.contrib import admin
from . models import *
from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.conf import settings
"""
can implement EXACT search by instructor username, course code, or course title

"""


#admin.site.site_url = settings.URL_PREFIX

class AdditionalEnrollmentInline(admin.StackedInline):
    model = AdditionalEnrollment
    extra = 2
    autocomplete_fields = ['user']



class CourseAdmin(admin.ModelAdmin):
    list_display =['course_code','course_name','get_instructors','get_subjects','get_schools','course_term','course_activity','requested']

    list_filter = (
        ('course_activity','course_term','course_schools')
    )
    search_fields = ('instructors__username','course_code','course_name')
    #readonly_fields = ['created','updated','owner','course_code','course_section','course_term','year','course_number','course_subject'] # maybe add requested to here.
    autocomplete_fields = ['crosslisted','instructors','multisection_request','crosslisted_request']

    fieldsets = (
        (None, {
            'fields': ('course_code','course_name',
            ('course_subject','course_number','course_section','year','course_term'),
            'instructors', 'course_schools', 'course_activity')
        }),
        ('Crosslist info', {
            'fields': ('crosslisted','primary_crosslist','course_primary_subject'),
        }),
        ('Request Info', {
            'fields': ('requested','request','requested_override', 'multisection_request','crosslisted_request',),
        }),
        ('Metadata', {
            'fields': ('created','updated','owner'),
        }),
    )



    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "course":
            kwargs["queryset"] = Course.objects.filter(course_schools__abbreviation=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created','updated','owner','course_code','course_section','course_term','year','course_number','course_subject','requested','request']
        else:
            return ['created','updated','owner','course_code']

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
    readonly_fields = ['created','updated','masquerade','additional_sections']
    inlines = [AdditionalEnrollmentInline]
    autocomplete_fields = ['owner','course_requested']

    fieldsets = (
        (None, {
            'fields': ('course_requested','copy_from_course','title_override','additional_sections',
            'additional_instructions','reserves','status','canvas_instance')
        }),
        ('Metadata', {
            'fields': ('created','updated','owner','masquerade'),
        }),
    )

    def additional_sections(self, instance):
        return instance.additional_sections.course_code


    #def formfield_for_manytomany(self, db_field, request, **kwargs):
    #    if db_field.name == "request":
    #        kwargs["queryset"] = Course.objects.filter(course_schools__abbreviation=request.user)
    #    return super().formfield_for_manytomany(db_field, request, **kwargs)

    def requestors(self,object):
        print("object.masquerade",object.masquerade)
        if object.masquerade == None:
            return object.owner.username
        elif object.masquerade != '':
            return object.owner.username + " (" + object.masquerade +") "
        else:
            return object.owner.username

    def save_model(self, request, obj, form, change):
        #print("checkin save")
        #obj.owner = request.user
        obj.save()


class CanvasSiteAdmin(admin.ModelAdmin):
    autocomplete_fields = ['owners','added_permissions','request_instance']
    list_display= ['name','get_owners','get_added_permissions']
    search_fields = ('owners__username','added_permissions__username','name')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]

class AutoAddAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']

# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)


admin.site.register(Course, CourseAdmin)
admin.site.register(Request,RequestAdmin)
admin.site.register(Notice)
admin.site.register(School)
admin.site.register(Activity)
admin.site.register(Subject)
admin.site.register(AutoAdd,AutoAddAdmin)
admin.site.register(UpdateLog)
admin.site.register(PageContent)
admin.site.register(CanvasSite,CanvasSiteAdmin)


# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Admin_site

# https://medium.com/@hakibenita/how-to-turn-django-admin-into-a-lightweight-dashboard-a0e0bbf609ad

#https://medium.com/crowdbotics/how-to-add-a-navigation-menu-in-django-admin-770b872a9531
