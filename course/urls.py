from django.conf.urls import include, url
from django.urls import path
from rest_framework.routers import DefaultRouter
from course import views

from rest_framework import renderers
#from rest_framework.schemas import get_schema_view # new



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

#schema_view = get_schema_view(title='Pastebin API') # new


# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
# NOTE : pk = course_SRS_Title
urlpatterns = [
    url(r'^api/', include(router.urls)),
    # --------------- Course list/detail view -------------------
    path('courses/', views.CourseViewSet.as_view(
        {'get': 'list'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-course-list'),
    path('courses/<str:pk>/', views.CourseViewSet.as_view(
        {'get': 'retrieve'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-course-detail'),

    #path('courses/<int:pk>/request', views.CourseViewSet.as_view(
    #    {'get': 'retrieve'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
    #     name='UI-course-detail'),
    # --------------- Request list/detail view -------------------
    path('requests/', views.RequestViewSet.as_view(
        {'get': 'list'},renderer_classes=[renderers.TemplateHTMLRenderer]),
         name='UI-request-list'),
    path('requests/<str:pk>/', views.RequestViewSet.as_view(
        {'get': 'retrieve'}, renderer_classes=[renderers.TemplateHTMLRenderer]),
        name='UI-request-detail'),


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
    # --------------- UPDATE LOG view -------------------
    #path('bulkupdates/', views.UpdateLogViewSet.as_view(
    #    {'get':'list'},renderer_classes=[renderers.TemplateHTMLRenderer]),
    #    name='UI-updatelog-list'),
]
#path('course', views.CourseViewSet.as_view({'get': 'list'})),
