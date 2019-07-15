from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework.routers import DefaultRouter
from course import views
from rest_framework_swagger.views import get_swagger_view
from rest_framework import renderers
from django.views.generic.base import TemplateView
#from rest_framework.schemas import get_schema_view # new

schema_view = get_swagger_view(title='Pastebin API')



# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'notices', views.NoticeViewSet)
router.register(r'requests', views.RequestViewSet)
router.register(r'schools', views.SchoolViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'autoadds', views.AutoAddViewSet)
"""
The example above would generate the following URL patterns:

URL pattern: ^users/$ Name: 'user-list'
URL pattern: ^users/{pk}/$ Name: 'user-detail'
URL pattern: ^courses/$ Name: 'course-list'
URL pattern: ^courses/{pk}/$ Name: 'course-detail'

-list goes to list()
-detail goes to retrieve()

This is fine because I want the API to be very generic

"""
# URL SHOULD REALLY USE REGEX
#SRS_SECTION_REGEX = re.compile(
#    r'^(?P<subject>[A-Z]{2,4})(?P<course_number>\d{3}|)-?(?P<section_number>\d{3}|)-(?P<term>20[01][0-9][ABC])$')
#)
#schema_view = get_schema_view(title='Pastebin API') # new


# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
# NOTE : pk = course_SRS_Title
urlpatterns = [
    # --------------- Documentation url/view -------------------
    path('documentation/',TemplateView.as_view(template_name='documentation.html'),name='documentation'),
    path('userlookup/',TemplateView.as_view(template_name='user_lookup.html'),name='documentation'),


    url(r'^api/', include(router.urls)),
    url(r'^api_doc/', schema_view),
    # --------------- Course list/detail view -------------------
    path('courses/', views.CourseViewSet.as_view(
        {'get': 'list'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-course-list'),
    path('courses/<course_code>/', views.CourseViewSet.as_view(
        {'get': 'retrieve'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-course-detail'),

    #path('courses/<int:pk>/request', views.CourseViewSet.as_view(
    #    {'get': 'retrieve'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
    #     name='UI-course-detail'),

    # --------------- Request list/detail view -------------------
    path('requests/', views.RequestViewSet.as_view(
        {'get': 'list','post':'create'},renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-request-list'),
    path('requests/<str:pk>/', views.RequestViewSet.as_view(
        {'get': 'retrieve','put': 'update'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
        name='UI-request-detail'),
    path('requests/<str:pk>/edit/', views.RequestViewSet.as_view(
        {'get': 'retrieve'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
        name='UI-request-detail-edit'),
    path('requests/<str:pk>/success/', views.RequestViewSet.as_view(
        {'get': 'retrieve'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
        name='UI-request-detail-success'),

    # --------------- School list/detail view -------------------
    path('schools/', views.SchoolViewSet.as_view(
        {'get':'list',},renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-school-list'),
    path('schools/<str:pk>/', views.SchoolViewSet.as_view(
        {'get': 'retrieve', 'put': 'update'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
        name='UI-school-detail'),

    # --------------- Subject list view -------------------
    path('subjects/', views.SubjectViewSet.as_view(
        {'get':'list'},renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-subject-list'),
    path('subjects/<str:pk>/', views.SubjectViewSet.as_view(
        {'get': 'retrieve', 'put': 'update'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
        name='UI-subject-detail'),

    # --------------- AUTOADDS view -------------------
    path('autoadds/', views.AutoAddViewSet.as_view(
        {'get':'list','post':'create','delete':'list'},renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-autoadd-list'), # adding 'delete': 'list' is hacky but saves me from writiing a detail page in UI
    #path('users/<?:pennkey>/', UserDetail.asview(),name='user-detail'),
    # --------------- HOMEPAGE view -------------------
    path('', views.HomePage.as_view(), name='home'),
    # --------------- CONTACT view -------------------
    path('contact/', views.contact, name='contact'),
    # --------------- USERINFO view -------------------
    path('accounts/userinfo/', views.userinfo, name='userinfo'),
    # --------------- UPDATE LOG view -------------------
    path('logs/', views.UpdateLogViewSet.as_view(
        {'get':'list'},renderer_classes=[renderers.TemplateHTMLRenderer]),
        name='UI-updatelog-list'),

    # --------------- Temporary Email view -------------------
    path('emails/', views.temporary_email_list, name='temporary_email'),
    path('emails/<value>/', views.my_email, name='my_email'),

    # --------------- login url/view -------------------
    path('accounts/login/', auth_views.LoginView.as_view(
            template_name='login.html',
            extra_context={'next': '/',},
            ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
            template_name='logout.html',
            ), name='logout'),

]
#path('course', views.CourseViewSet.as_view({'get': 'list'})),
