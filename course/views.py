
from course.models import Course, Notice, Request, School, Subject
from course.serializers import CourseSerializer, UserSerializer, NoticeSerializer, RequestSerializer, SchoolSerializer, SubjectSerializer
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



"""
# below is not needed now that a router is being used
@api_view(['GET'])
#@renderer_classes((JSONRenderer,))
def api_root(request, format=None):
    response = Response({
        'users': reverse('user-list', request=request, format=format),
        'courses': reverse('course-list', request=request, format=format),
        'notices': reverse('notice-list', request=request, format=format)
    })
    return response

    #'courses': reverse('course-list', request=request, format=format)

    # reverse(viewname, *args, **kwargs)
    # 1. using reverse function to return fully qualified URLs
    # 2. URL patterns are identified by convenience names that we will declare in urls.py
"""


# for more on viewsets see: https://www.django-rest-framework.org/api-guide/viewsets/
# (slightly helpful ) or see: http://polyglot.ninja/django-rest-framework-viewset-modelviewset-router/

#these functions should exist somewhere else !

def get_links(response,request):
    parsed_links = py_requests.utils.parse_header_links(response['Link'].rstrip('>').replace('>,<', ',<'))
    reformatted_links = d = { item['rel']: {'url':item['url'], 'value':get_page_number(item['url'])} for item in parsed_links }

    url = request.get_full_path()
    reformatted_links['current']= {'url':url, 'value':get_page_number(url)}
    return reformatted_links

def get_page_number(url):
    try:
        value = parse.parse_qs(parse.urlsplit(url).query)['page'][0]
    except KeyError:
        value = 1
    return value

def get_last_page_number(response):
    pages = get_links(response)
    try:
        params = parse.parse_qs(parse.urlsplit(pages['last']).query)

        return pages, params['page'][0] # will be string
    except KeyError:
        return pages, None

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
        print('request',request.data)
        response = super(CourseViewSet, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            #num_pages = -(-response.data['count']//10) # this should get 10 from settings.py
            #response.data.update({'total_pages': num_pages})
            print("bye george(list)!\n",response.data)
            #parsed_links, last_page = get_last_page_number(response)
            last_page = None
            parsed_links = get_links(response,request)
            print("last_page", last_page)
            print("parsed_links", parsed_links)

            return Response({'data': response.data, 'pagination':parsed_links}, template_name='course_list.html')
        print("Coursviewset", response.data)
        print(response)
        print(response.data)
        print(response.items())
        print(request.content_type)
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


        response = super(RequestViewSet, self).list(request, *args, **kwargs)
        print("in the list... ")
        #def get_paginated_response(self, data): GenericAPIView
        if request.accepted_renderer.format == 'html':
            #num_pages = -(-response.data['count']//10) # this should get 10 from settings.py
            #response.data.update({'total_pages': num_pages})

            #print("bye george(UI-request-list)!\n",response.data)
            return Response({'data': response.data}, template_name='request_list.html')
        return response

    def retrieve(self, request, *args, **kwargs):
        print("ok in ret self,,",self.request.session.get('on_behalf_of','None'))
        print("ok in ret,,", request.session.get('on_behalf_of','None'))
        print("Request.retrieve")
        response = super(RequestViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            #print("bye george(UI-request-detail)!\n",response.data)
            return Response({'data': response.data}, template_name='request_detail.html')
        return response


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
        print("ohhhhhhhhh")

        response = super(SchoolViewSet, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':

            print("SchoolViewSet HTML-UI")
            #num_pages = -(-response.data['count']//10) # this should get 10 from settings.py
            #response.data.update({'total_pages': num_pages})

            print("bye george(UI-school-list)!\n",response.data)
            return Response({'data': response.data}, template_name='schools_list.html')
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
        print("ohhhhhhhhh")

        response = super(SubjectViewSet, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            print("SubjectViewSet HTML-UI")
            #num_pages = -(-response.data['count']//10) # this should get 10 from settings.py
            #response.data.update({'total_pages': num_pages})
            print("bye george(UI-subject-list)!\n",response.data)
            return Response({'data': response.data}, template_name='subjects_list.html')
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
