
from course.models import Course, Notice, Request, School, Subject, AutoAdd
from course.serializers import CourseSerializer, UserSerializer, NoticeSerializer, RequestSerializer, SchoolSerializer, SubjectSerializer, AutoAddSerializer
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from course.permissions import IsOwnerOrReadOnly

from rest_framework.reverse import reverse

from rest_framework import viewsets
from rest_framework.decorators import action, api_view


from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.views.generic import TemplateView
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import path
from course import views

from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from rest_framework.pagination import PageNumberPagination
import requests as py_requests
import re
from urllib import parse
#class CourseView(TemplateView):
#    template_name = "index.html"


"""
For more 'Detailed descriptions, with full methods and attributes, for each
of Django REST Framework's class-based views and serializers'see: http://www.cdrf.co/

"""

#self.request.QUERY_PARAMS.get('appKey', None)



# for more on viewsets see: https://www.django-rest-framework.org/api-guide/viewsets/
# (slightly helpful ) or see: http://polyglot.ninja/django-rest-framework-viewset-modelviewset-router/

def validate_pennkey(pennkey):
    # assumes usernames are valid pennkeys

    try:
        user = User.objects.get(username=pennkey)
    except User.DoesNotExist:
        user = None
    return user


def set_session(request):
    print("home request.data",request.data)
    #if request.session.get('on_behalf_of','None'):
    #    on_behalf_of = request.session['on_behalf_of']
    #else:
    #    on_behalf_of = None
    try:
        on_behalf_of = request.data['on_behalf_of']
        print("found on_behalf_of in request.data ", on_behalf_of)
        if on_behalf_of: # if its not none -> if exists then see if pennkey works
            if validate_pennkey(on_behalf_of) == None: #if pennkey is good the user exists
                print("not valid input")
                messages.error(request,'Invalid Pennkey')
                on_behalf_of = None
    except KeyError:
        pass

    # check if user is in the system

    request.session['on_behalf_of'] = on_behalf_of
    print("masquerading as:", request.session['on_behalf_of'])






class CourseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions. see http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html
    """
    # # TODO:
    # [ ] create and test permissions
    # [x] on creation of request instance mutatate course instance so courese.requested = True
    #[ ] ensure POST is only setting masquerade

    #lookup_field = 'course_SRS_Title'
    #lookup_value_regex = '[0-9a-f]{32}'

    queryset = Course.objects.all()#.order_by() # order by
    serializer_class = CourseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    #filter_backends = (DjangoFilterBackend,)
    filter_fields = ('course_SRS_Title','course_name', 'course_activity','instructors','course_schools','course_subjects',)

    def perform_create(self, serializer):
        print("CourseViewSet.perform_create: request.POST", self.request.POST)
        print("CourseViewSet.perform_create: request.meta", self.request.META) # could use 'HTTP_REFERER': 'http://127.0.0.1:8000/courses/'
        print("CourseViewSet.perform_create: request.query_params", self.request.query_params)
        print('CourseViewSet.perform_create lookup field', self.lookup_field)
        print("CourseViewSet.perform_create", self.request.data)
        serializer.save(owner=self.request.user)


    # below allows for it to be passed to the template !!!!
    # I AM NOT SURE IF THIS IS OKAY WITH AUTHENTICATION
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        print("1")
        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'course_list.html'
                print("template_name",response.template_name)
                response.data = {'results': response.data,'paginator':self.paginator}
            print("request.accepted_renderer.format",request.accepted_renderer.format)
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            print("template_name",response.template_name)
            response.template_name = 'course_list.html'
            print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response

    def retrieve(self, request, *args, **kwargs):
        print('CourseViewSet.retreive lookup field', self.lookup_field)
        response = super(CourseViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            print("bye george(detail)!\n",response.data)
            return Response({'course': response.data}, template_name='course_detail.html')
        return response

    def post(self, request,*args, **kwargs):
        #need to check if the post is for masquerade
        print(request.get_full_path())
        set_session(request)
        return(redirect(request.get_full_path()))




class RequestViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions. see http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html
    """
    # # TODO:
    # [ ] create and test permissions
    # [x] on creation of request instance mutatate course instance so courese.requested = True
    #[ ] ensure POST is only setting masquerade

    queryset = Request.objects.all()#.order_by() # order by
    serializer_class = RequestSerializer
    filter_fields = ('copy_from_course','status','owner','course_requested',)
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,
    #                      IsOwnerOrReadOnly,)
    def create(self, request, *args, **kwargs):
        """
        Currently this function creates Request instances made from the UI view and the api view
        Therefore there needs to be diambiguation that routes to the UI list view or the api list view
        after creation. Since the POST action is always made to the /api/ endpoint i cannot check what
        the accepted_renderer.format is b/c it will always be api.
            To do this I am tryint to pass a query_param with the UI POST action
            however this may not be the best method perhaps something that has to do with
            sessions would be a better and safer implementation.
        """

        print("views.py in create: request.data", request.data)
        try:
            masquerade = request.session['on_behalf_of']
        except KeyError:
            masquerade = ''
        print("masqueraded as:", masquerade)

        #print("in create: request.POST", request.POST)
        #print("in create: request.meta", request.META) # could use 'HTTP_REFERER': 'http://127.0.0.1:8000/courses/'
        #print("in create: request.query_params", request.query_params)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("oahewgoaihw f", serializer.validated_data)
        print("sad", serializer)
        serializer.validated_data['masquerade'] = masquerade
        self.perform_create(serializer)
        print("its gonna b ok")
        headers = self.get_success_headers(serializer.data)

        # updates the course instance #
        course = Course.objects.get(course_SRS_Title=request.data['course_requested'])# get Course instance
        course.requested = True
        course.save()
        print(course.course_SRS_Title, course.requested)
        # update course instance
        # this allow for the redirect to the UI and not the API endpoint. 'view_type' should be defined in the form that submits this request
        if 'view_type' in request.data:
            if request.data['view_type'] == 'UI':
                return redirect('UI-course-list')
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


        #if self.request.query_params['view_type'] == 'UI':
        #HttpResponseRedirect(redirect_to='http://127.0.0.1:8000/courses/')
        #return redirect('UI-course-list')


    def perform_create(self, serializer):
        print("Request perform_create")

        serializer.save(owner=self.request.user)
        print("no prob here")
        serializer.save(masquerade="HECK")
        print(serializer)
        print("2. no prob here")

    # below allows for it to be passed to the template !!!!
    # I AM NOT SURE IF THIS IS OKAY WITH AUTHENTICATION
    def list(self, request, *args, **kwargs):
        print('rrr', self.lookup_field)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        print("1")
        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'request_list.html'
                print("template_name",response.template_name)
                response.data = {'results': response.data,'paginator':self.paginator}
            print("request.accepted_renderer.format",request.accepted_renderer.format)
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            print("template_name",response.template_name)
            response.template_name = 'request_list.html'
            print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response





    def retrieve(self, request, *args, **kwargs):
        print("ok in ret self,,",self.request.session.get('on_behalf_of','None'))
        print("ok in ret,,", request.session.get('on_behalf_of','None'))
        print("Request.retrieve")
        print(request.data)
        response = super(RequestViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            #print("bye george(UI-request-detail)!\n",response.data)
            return Response({'data': response.data}, template_name='request_detail.html')
        return response



    def destroy(self, request, *args, **kwargs):
        print("OH MY GOLLY GEEE")

    def post(self, request,*args, **kwargs):
        #if request.user.is_authenticated()
        #need to check if the post is for masquerade
        if request.data['on_behalf_of']:
            print(request.get_full_path())
            print("ok self,,",self.request.session.get('on_behalf_of','None'))
            print("ok no self,,",request.session.get('on_behalf_of','None'))
            set_session(request)
            return(redirect(request.get_full_path()))

class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions. (READONLY)
    """
    # only admins ( user.is_staff ) can do anything with this data
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer






class SchoolViewSet(viewsets.ModelViewSet):
    """
    This viewset only provides custom `list` actions
    """
    # # TODO:
    #[ ] ensure POST is only setting masquerade
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

#    def perform_create(self, serializer):
#        serializer.save(owner=self.request.user)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        print("1")
        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'schools_list.html'
                print("template_name",response.template_name)
                response.data = {'results': response.data,'paginator':self.paginator}
            print("request.accepted_renderer.format",request.accepted_renderer.format)
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            print("template_name",response.template_name)
            response.template_name = 'schools_list.html'
            print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response

    def post(self, request,*args, **kwargs):

        #if request.user.is_authenticated():

        #need to check if the post is for masquerade
        print(request.get_full_path())
        set_session(request)
        return(redirect(request.get_full_path()))

class SubjectViewSet(viewsets.ModelViewSet):
    """
    This viewset only provides custom `list` actions
    """
    # # TODO:
    #[ ] ensure POST is only setting masquerade

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

#    def perform_create(self, serializer):
#        serializer.save(owner=self.request.user)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        print("1")
        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'subjects_list.html'
                response.data = {'results': response.data,'paginator':self.paginator}
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            print("template_name",response.template_name)
            response.template_name = 'subjects_list.html'
            print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response

    def post(self, request,*args, **kwargs):

        #if request.user.is_authenticated():
        #need to check if the post is for masquerade
        print(request.get_full_path())
        set_session(request)
        return(redirect(request.get_full_path()))


class NoticeViewSet(viewsets.ModelViewSet):
    """
    THIS IS A TEMPORARY COPY
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

    def perform_create(self, serializer):
        print("NoticeViewSet - perform_create trying to create Notice")
        #print(self.request.user) == username making request
        serializer.save(owner=self.request.user)


class HomePage(APIView):
    # TODO
    # [ ] add table for site_request and srs_course
    # [x] add base case of empty responses
    # [ ] add method for setting session info
    # [ ] ensure POST is only setting masquerade
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home_content.html'


    def get(self, request, *args, **kwargs):
        # # TODO:
        # [ ] Check that valid pennkey
        # [ ] handles if there are no notice instances in the db
        try:
            notice = Notice.objects.latest()
            print(Notice.notice_text)
        except Notice.DoesNotExist:
            notice = None

        return Response({'data':
            {'notice':notice,
            'site_requests':'',
            'srs_course':'',
            'username':request.user}})
    # get the user id and then do three queries to create these tables
    # 1. Site Requests
    # 2. SRS Courses
    # 3. Canvas Sites

#    def post(self, request,*args, **kwargs):
#        return redirect(request.path)



    def post(self, request,*args, **kwargs):
        #if request.user.is_authenticated():
        #need to check if the post is for masquerade
        print(request.get_full_path())
        set_session(request)
        return(redirect(request.get_full_path()))


    #print(redirect("/"))
    #return redirect("/")



class AutoAddViewSet(viewsets.ModelViewSet):
    """
    THIS IS A TEMPORARY COPY
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = AutoAdd.objects.all()
    serializer_class = AutoAddSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        print("1")
        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'autoadd_list.html'
                print("template_name",response.template_name)
                response.data = {'results': response.data,'paginator':self.paginator}
            print("request.accepted_renderer.format",request.accepted_renderer.format)
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            print("template_name",response.template_name)
            response.template_name = 'autoadd_list.html'
            print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response


def send_email(request):
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    from_email = request.POST.get('from_email', '')
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, ['admin@example.com'])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponseRedirect('/contact/thanks/')
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse('Make sure all fields are entered and valid.')
    """"
    send_mail(
        'Subject here',
        'Here is the message.',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,)
    SEE MORE: https://docs.djangoproject.com/en/2.1/topics/email/
    """
