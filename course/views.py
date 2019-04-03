
from course.models import * #Course, Notice, Request, School, Subject, AutoAdd
from course.serializers import * #CourseSerializer, UserSerializer, NoticeSerializer, RequestSerializer, SchoolSerializer, SubjectSerializer, AutoAddSerializer
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from course.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser

from rest_framework.reverse import reverse

from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from django.contrib.auth.decorators import login_required

from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.views.generic import TemplateView
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import path
from course import views

from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework.utils.urls import replace_query_param, remove_query_param
from django_filters import rest_framework as filters


from course.forms import ContactForm, EmailChangeForm
from django.template.loader import get_template
import datetime
from course import email_processor
#class CourseView(TemplateView):
#    template_name = "index.html"


"""
For more 'Detailed descriptions, with full methods and attributes, for each
of Django REST Framework's class-based views and serializers'see: http://www.cdrf.co/

"""

#self.request.QUERY_PARAMS.get('appKey', None)


######### API METHODS ########
# PUT/PATCH -> PARTIAL UPDATE
# POST -> CREATE

# for more on viewsets see: https://www.django-rest-framework.org/api-guide/viewsets/
# (slightly helpful ) or see: http://polyglot.ninja/django-rest-framework-viewset-modelviewset-router/

def validate_pennkey(pennkey):
    # assumes usernames are valid pennkeys
    try:
        user = User.objects.get(username=pennkey)
    except User.DoesNotExist:
        user = None
    return user



class MixedPermissionModelViewSet(viewsets.ModelViewSet):
   '''
   Mixed permission base model allowing for action level
   permission control. Subclasses may define their permissions
   by creating a 'permission_classes_by_action' variable.

   Example:
   permission_classes_by_action = {'list': [AllowAny],
                                   'create': [IsAdminUser]}
   '''
   permission_classes_by_action = {}
   def get_permissions(self):
      try:
        # return permission_classes depending on `action`
        return [permission() for permission in self.permission_classes_by_action[self.action]]
      except KeyError:
        # action is not set return default permission_classes
        return [permission() for permission in self.permission_classes]





class CourseFilter(filters.FilterSet):
    #activity =
    #filter_fields = ('course_activity','instructors__username','course_schools__abbreviation','course_subjects__abbreviation',) #automatically create a FilterSet class
    # https://github.com/philipn/django-rest-framework-filters/issues/102
    #pls see: https://django-filter.readthedocs.io/en/master/ref/filters.html
    activity = filters.ChoiceFilter(choices=Course.ACTIVITY_CHOICES, field_name='course_activity', label='Activity')
    instructor = filters.CharFilter(field_name='instructors__username', label='Instructor')
    school = filters.CharFilter(field_name='course_schools__abbreviation',label='School (abbreviation)')
    subject = filters.CharFilter(field_name='course_subjects__abbreviation', label='Subject (abbreviation)')
    term = filters.ChoiceFilter(choices=Course.TERM_CHOICES, field_name='course_term', label='Term')
    class Meta:
        model = Course
        fields = ['activity','instructor','school','subject','term']


class CourseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions. see http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html
    """
    # # TODO:
    # [ ] create and test permissions
    # [x] on creation of request instance mutatate course instance so courese.requested = True
    #[ ] ensure POST is only setting masquerade
    lookup_field = 'course_code'
    queryset = Course.objects.filter(~Q(course_subjects__visible=False)).exclude(course_schools__visible=False,) #this should be filtered by the
    serializer_class = CourseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly,)
    filterset_class = CourseFilter
    search_fields = ['$course_name', '$course_code']
    # for permission_classes_by_action see: https://stackoverflow.com/questions/35970970/django-rest-framework-permission-classes-of-viewset-method
    permission_classes_by_action = {'create': [IsAdminUser],
                                    'list': [IsAuthenticatedOrReadOnly],
                                    'retreive':[IsOwnerOrReadOnly,IsAdminUser],
                                    'update':[IsAdminUser],
                                    'partial_update':[IsAdminUser],
                                    'delete':[IsAdminUser]}


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
        print("query_set", queryset)
        page = self.paginate_queryset(queryset)

        #print(",,",self.filter_backends[0].get_filterset(request,self.get_queryset(),self))
        for backend in list(self.filter_backends):
            #django_filters.rest_framework.backends.DjangoFilterBackend - https://github.com/carltongibson/django-filter/blob/master/django_filters/rest_framework/backends.py
            print("...",backend.filterset_base.form) # <class 'django_filters.rest_framework.filterset.FilterSet'>
            print("...1",backend.filterset_base.get_form_class)
            #print("...1",backend.filterset_base.filters)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'course_list.html'
                print(request.get_full_path())
                print("kwargs",kwargs)
                print("args",args)

                # https://github.com/encode/django-rest-framework/blob/master/rest_framework/utils/urls.py

                print('filterfield', CourseFilter.Meta.fields)
                print('request.query_params', request.query_params.keys())
                response.data = {'results': response.data,'paginator':self.paginator, 'filter':CourseFilter, 'request':request}
            print("yeah ok1",response.items())

            return response
        """
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            response.template_name = 'course_list.html'
            response.data = {'results': response.data}
        print("yeah ok2",response.items())
        return response
        """

    def retrieve(self, request, *args, **kwargs):
        print('CourseViewSet.retreive lookup field', self.lookup_field)
        response = super(CourseViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            print("bye george(detail)!\n",response.data)
            course_instance = self.get_object()
            print("iii",course_instance)
            # okay so at this point none of this is working soe

            # should check if requested and if so get that request obj! is this efficient ??
            if course_instance.requested == True:
                # course detail needs form history

                #NOTE there must be an associated course and if there isnt... we r in trouble!
                request_instance = course_instance.get_request()
                print("hfaweuifh ",request_instance)
                this_form =''
            else:
                # course detail needs to get form
                # URGENT is this creating many copies of the ob?
                this_form = RequestSerializer(data={'course_requested':self.get_object()})
                print("ok")
                this_form.is_valid()
                print("this_form",this_form.data)
                request_instance =''
            return Response({'course': response.data, 'request_instance':request_instance,'request_form':this_form ,'style':{'template_pack': 'rest_framework/vertical/'}}, template_name='course_detail.html')
        return response


class RequestFilter(filters.FilterSet):
    #activity =
    #filter_fields = ('course_activity','instructors__username','course_schools__abbreviation','course_subjects__abbreviation',) #automatically create a FilterSet class
    # https://github.com/philipn/django-rest-framework-filters/issues/102
    #pls see: https://django-filter.readthedocs.io/en/master/ref/filters.html
    status = filters.ChoiceFilter(choices=Request.REQUEST_PROCESS_CHOICES, field_name='status', label='Status')
    requestor = filters.CharFilter(field_name='owner__username', label='Requestor') # does not include masquerade! and needs validator on input!
    date = filters.DateTimeFilter(field_name='created',label='Created')
    #school = filters.CharFilter(field_name='course_schools__abbreviation',label='School (abbreviation)')
    #subject = filters.CharFilter(field_name='course_subjects__abbreviation', label='Subject (abbreviation)')
    #term = filters.ChoiceFilter(choices=Course.TERM_CHOICES, field_name='course_term', label='Term')
    class Meta:
        model = Request
        fields = ['status','requestor','date']
        #fields = ['activity','instructor','school','subject','term']


class RequestViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions. see http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html
    """
    # # TODO:
    # [ ] create and test permissions
    # [x] on creation of request instance mutatate course instance so courese.requested = True
    #[ ] ensure POST is only setting masquerade

    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    filterset_class = RequestFilter
    search_fields = ['$course_requested__course_name', '$course_requested__course_code']
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,
    #                      IsOwnerOrReadOnly,)
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retreive':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}

    def create(self, request, *args, **kwargs):
        """
        functions like a signal
            whenever a request is created this function updates the course instance and updates the crosslisted courses.
        """
        # putting this function inside create because it should only be accessible here.
        def update_course(self,course):
            course.requested = True
            course.save()
            if course.crosslisted:
                for crosslisted in course.crosslisted.all():
                    crosslisted.requested = True
                    crosslisted.request = course.request
                    print(":::::",crosslisted.request , course.request)
                    crosslisted.save()
            print(course.course_code, course.requested)
            #get crosslisted courses
            crosslisted = course.crosslisted
            print(crosslisted,"help me!!!")


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

        print("request.data", request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['masquerade'] = masquerade
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # updates the course instance #
        course = Course.objects.get(course_code=request.data['course_requested'])# get Course instance
        update_course(self,course)
        # update course instance
        # this allow for the redirect to the UI and not the API endpoint. 'view_type' should be defined in the form that submits this request

        # the following should have redirect pages which say something like "you have created X see item, go back to list"
        if 'view_type' in request.data:
            if request.data['view_type'] == 'UI-course-list':
                return redirect('UI-course-list')
            if request.data['view_type'] == 'UI-request-detail':
                return redirect('UI-request-detail', pk=course.course_code)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


        #if self.request.query_params['view_type'] == 'UI':
        #HttpResponseRedirect(redirect_to='http://127.0.0.1:8000/courses/')
        #return redirect('UI-course-list')


    def perform_create(self, serializer):
        print("Request perform_create")
        serializer.save(owner=self.request.user)
        print("no prob here")
        serializer.save(masquerade="test")# NOTE fix this!
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
            print(serializer.data)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'request_list.html'
                print("template_name",response.template_name)
                response.data = {'results': response.data,'paginator':self.paginator, 'filter': RequestFilter}
            print("request.accepted_renderer.format",request.accepted_renderer.format)
            return response
        """
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            print("template_name",response.template_name)
            response.template_name = 'request_list.html'
            print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response
        """


    def check_request_update_permissions(request,response_data):
        request_status = response_data['status']
        request_owner = response_data['owner']
        request_masquerade = response_data['masquerade']
            # owner is also considered masquerade
        if request_status == "SUBMITTED": permissions = {'staff':['lock','cancel','edit'],'owner':['cancel','edit']}
        elif request_status == "APPROVED": permissions = {'staff':['cancel','edit'],'owner':['cancel']}
        elif request_status == "LOCKED": permissions = {'staff':['cancel','edit','unlock'],'owner':['']}
        elif request_status == "CANCELED": permissions = {'staff':['lock'],'owner':['']}
        elif request_status == "IN_PROCESS": permissions = {'staff':[''],'owner':['']}
        elif request_status == "COMPLETED": permissions = {'staff':[''],'owner':['']}
        else: permissions = {'staff':[''],'owner':['']} # throw error!???
        if request.user.is_staff:
            return permissions['staff']
        if request.user.username == request_owner or (request.user.username == request_masquerade and request_masquerade !=''):
            print("yeahh buddy",request.user.username)
            return permissions['owner']
        return ''



    def retrieve(self, request, *args, **kwargs):
        """
            can retreive for /requests/<COURSE_CODE>/ or /requests/<COURSE_CODE/edit
        """
        print("ok in retreive self,,",self.request.session.get('on_behalf_of','None'))
        print("ok in ret,,", request.session.get('on_behalf_of','None'))
        print("Request.retrieve")
        print(request.data)

        response = super(RequestViewSet, self).retrieve(request, *args, **kwargs)
        print("response",response.data)
        if request.accepted_renderer.format == 'html':
            #print("bye george(UI-request-detail)!\n",response.data)
            permissions = RequestViewSet.check_request_update_permissions(request, response.data)

            if 'edit' in request.path.split('/') : # this is possibly the most unreliable code ive ever written
                # we want the edit form


                # CHECK PERMISSIONS -> must be creator and not be masquerading as creator
                # CHECK IF request status is submitted ( for requestor ) or submitted/locked( for admin)
                return Response({'request_instance': response.data,'permissions':permissions}, template_name='request_detail_edit.html')
            return Response({'request_instance': response.data, 'permissions':permissions}, template_name='request_detail.html')
        return response

    def destroy(self, request, *args, **kwargs):
        print("OH MY GOLLY GEEE we r deleteing")
        instance = self.get_object()
        # Must get Course and set .request to true
        course = Course.objects.get(course_code=instance.course_requested)# get Course instance
        course.requested = False
        course.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def post(self, request,*args, **kwargs):
        #if request.user.is_authenticated()
        #need to check if the post is for masquerade
        # '' is different than None ... if the key isnt present the .get() returns None
        """
        if request.data.get('on_behalf_of')=='':
            print(request.get_full_path())
            print("ok self,,",self.request.session.get('on_behalf_of','None'))
            print("ok no self,,",request.session.get('on_behalf_of','None'))
            set_session(request)
            return redirect(request.get_full_path())
        """

    def update(self, request, *args, **kwargs):
        print("in update")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        print(":^)")
        print("request.data update!",request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        print(":^) !")
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        #Lets check if we need to send an email?
        if 'status' in request.data:
            if request.data['status'] =='LOCKED':
                #lets send that email babie !!!!
                email_processor.admin_lock(context={'request_detail_url':request.build_absolute_uri(reverse('UI-request-detail',kwargs={'pk':request.data['course_requested']})) , 'course_code': request.data['course_requested']})

        if 'view_type' in request.data:
            if request.data['view_type'] == 'UI-request-detail':
                print("LLL")
                permissions = RequestViewSet.check_request_update_permissions(request, {'owner':instance.owner,'masquerade':instance.masquerade,'status':instance.status})
                return Response({'request_instance':serializer.data,'permissions':permissions}, template_name='request_detail.html')
                #return redirect('UI-request-detail', pk=request.data['course_requested'])

        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions. (READONLY)
    """
    # only admins ( user.is_staff ) can do anything with this data
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retreive':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}

    """
    # this is just to havet the pk be username and not id
    def retrieve(self, request, pk=None):
        print("IM DOING MY BEST")
        instance = User.objects.filter(username=pk)
        print(instance)


        serializer = self.get_serializer(instance)
        return Response(serializer.data)

        return Response(serializer.data)
    """




class SchoolViewSet(viewsets.ModelViewSet):
    """
    This viewset only provides custom `list` actions
    """
    # # TODO:
    #[ ] ensure POST is only setting masquerade
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retreive':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}

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
        """
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            print("template_name",response.template_name)
            response.template_name = 'schools_list.html'
            print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response
        """

    def post(self, request,*args, **kwargs):
        print("posting")
        #if request.user.is_authenticated():

        """
        #need to check if the post is for masquerade
        print(request.get_full_path())
        set_session(request)
        return(redirect(request.get_full_path()))
        """

    def update(self, request, *args, **kwargs):
        print("update?")
        print("args",args)
        print("kwargs", kwargs)
        print("request.data", request.data)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        if request.data.get('view_type',None) == 'UI':
            print("its happening")

        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        print("this is dumb",request.method)
        response = super(SchoolViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            #print("bye george(UI-request-detail)!\n",response.data)
            return Response({'data': response.data}, template_name='school_detail.html')
        return response


class SubjectViewSet(viewsets.ModelViewSet):
    """
    This viewset only provides custom `list` actions
    """
    # # TODO:
    #[ ] ensure POST is only setting masquerade

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retreive':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}
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
        """
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'html':
            print("template_name",response.template_name)
            response.template_name = 'subjects_list.html'
            print("template_name",response.template_name)
            response.data = {'results': response.data}
        return response
        """

    def post(self, request,*args, **kwargs):
        #if request.user.is_authenticated():
        """
        #need to check if the post is for masquerade
        print(request.get_full_path())
        set_session(request)
        return(redirect(request.get_full_path()))
        """

    def retrieve(self, request, *args, **kwargs):
        print(request.data)
        response = super(SubjectViewSet, self).retrieve(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            #print("bye george(UI-request-detail)!\n",response.data)
            return Response({'data': response.data}, template_name='subject_detail.html')
        return response




class NoticeViewSet(viewsets.ModelViewSet):
    """
    THIS IS A TEMPORARY COPY
    """
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retreive':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}
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
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retreive':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}

    def get(self, request, *args, **kwargs):
        # # TODO:
        # [ ] Check that valid pennkey
        # [ ] handles if there are no notice instances in the db
        print("in home")
        try:
            notice = Notice.objects.latest()
            print(Notice.notice_text)
        except Notice.DoesNotExist:
            notice = None
            print("no notices")


        # for courses do instructors.courses since there is a manytomany relationship
        return Response({'data':
            {'notice':notice,
            'site_requests':'',
            'srs_course':'',
            'username':request.user}})

    # get the user id and then do three queries to create these tables
    # you should get the user id of the auth.user or if they are masquerading get the id of that user
    # 1. Site Requests
    # 2. SRS Courses
    # 3. Canvas Sites

#    def post(self, request,*args, **kwargs):
#        return redirect(request.path)


    def set_session(request):
        print("set_session request.data",request.data)
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


    def post(self, request,*args, **kwargs):
        #if request.user.is_authenticated():
        #need to check if the post is for masquerade
        print("posting in home")
        print("\trequest.get_full_path()",request.get_full_path())
        print("\trequest.META[''HTTP_REFERER'']",request.META['HTTP_REFERER'])
        HomePage.set_session(request)
        return(redirect(request.META['HTTP_REFERER']))




class AutoAddViewSet(viewsets.ModelViewSet):
    """
    provides list create and destroy actions only
    no update or detail actions.
    """
    queryset = AutoAdd.objects.all()
    serializer_class = AutoAddSerializer
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retreive':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        print("autoadd data",serializer.data) # {'url': 'http://127.0.0.1:8000/api/autoadds/1/', 'user': 'username_8', 'school': 'AN', 'subject': 'abbr_2', 'id': 1, 'role': 'ta'}
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        email_processor.autoadd_contact({'user':serializer.data['user'], 'role':serializer.data['role'], 'school':School.objects.get(abbreviation=serializer.data['school']).name, 'subject':Subject.objects.get(abbreviation=serializer.data['subject']).name})
        print("got here")
        if request.accepted_renderer.format == 'html':
            response.template_name = 'admin/autoadd_list.html'
            return(redirect('UI-autoadd-list'))
        return response


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        print("1")

        if page is not None:

            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data) #http://www.cdrf.co/3.9/rest_framework.viewsets/ModelViewSet.html#paginate_queryset
            print("template_name",response.template_name)
            if request.accepted_renderer.format == 'html':
                response.template_name = 'admin/autoadd_list.html'
                print("template_name",response.template_name)
                print("qqq",repr(AutoAddSerializer))
                print("qqqq",AutoAddSerializer.fields)
                response.data = {'results': response.data,'paginator':self.paginator,'serializer':AutoAddSerializer}
            print("request.accepted_renderer.format",request.accepted_renderer.format)
            print("yeah ok1",response.items())
            return response

    def destroy(self, request, *args, **kwargs):
        print("ss")
        instance = self.get_object()
        self.perform_destroy(instance)
        print("ok", request.path)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        if 'UI' in request.data:
            if request.data['UI'] == 'true':
                print("eya")
                response.template_name = 'admin/autoadd_list.html'
                return(redirect('UI-autoadd-list'))
        return response








class UpdateLogViewSet(viewsets.ModelViewSet):
    """
    THIS IS A TEMPORARY COPY
    This viewset automatically provides `list` and `detail` actions.
    """
    #permission_classes = (IsAdminUser,)
    queryset = UpdateLog.objects.all()
    serializer_class = UpdateLogSerializer
    permission_classes_by_action = {'create': [],
                                    'list': [],
                                    'retreive':[],
                                    'update':[],
                                    'partial_update':[],
                                    'delete':[]}
    # CHECK PERMISSIONS!
    def list(self, request, *args, **kwargs):
        print("yeah ok")
        return Response({'data': ''}, template_name='admin/log_list.html')





# --------------- USERINFO view -------------------

#@login_required(login_url='/accounts/login/')
def userinfo(request):
    form = EmailChangeForm(request.user)
    print(request.method)
    if request.method=='POST':
        print("we in the POST")
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('userinfo') # this should redirect to success page
    return render(request, "user_info.html", {'form':form})

# --------------- CONTACT view -------------------
# add to your views
def contact(request):
    form_class = ContactForm
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            contact_name = request.POST.get('contact_name', '')
            contact_email = request.POST.get('contact_email', '')
            form_content = request.POST.get('content', '')

            # Email the profile with the
            # contact information
            context = {'contact_name': contact_name,'contact_email': contact_email,'form_content': form_content,}
            email_processor.feedback(context)
            return redirect('contact')
    return render(request, 'contact.html', {'form': form_class,})


# --------------- Temporary Email view -------------------
"""
This view is only for beta testing of the app
"""
import os
from os import listdir
def temporary_email_list(request):
    filelist = os.listdir('course/static/emails/')

    return render(request, 'email/email_log.html', {'filelist':filelist})

from django.http import HttpResponse
def my_email(request,value):

    email = open("course/static/emails/"+value, "rb").read()

    return render(request, 'email/email_detail.html', {'email':email.decode("utf-8")} )




#SEE MORE: https://docs.djangoproject.com/en/2.1/topics/email/
