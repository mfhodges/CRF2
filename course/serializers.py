from rest_framework import serializers
from course.models import Course, Notice, Request, School, Subject
from django.contrib.auth.models import User


# Serializer Classes provide a way of serializing and deserializing
# the model instances into representations such as json. We can do this
# by declaring serializers that work very similar to Django forms
#








class CourseSerializer(serializers.HyperlinkedModelSerializer):
    """

    """

    # # TODO:
    # [ ] make sure that course_SRS_Title is unique ! -- it is used to link later

    #this adds a field that is not defined in the model

    owner = serializers.ReadOnlyField(source='owner.username')

    # cant uncomment following line without resolving lookup for Request
    course_SRS_Title = serializers.CharField()
    request_info = serializers.HyperlinkedRelatedField(many=False, lookup_field='course_requested',view_name='request-detail',read_only=True)

    #request_status = serializers.HyperlinkedIdentityField(view_name='course-request', format='html')


    # Eventually the queryset should also filter by Group = Instructors
    instructors = serializers.SlugRelatedField(many=True,queryset=User.objects.all(), slug_field='username')
    course_schools = serializers.SlugRelatedField(many=True,queryset=School.objects.all(), slug_field='abbreviation')
    course_subjects = serializers.SlugRelatedField(many=True,queryset=Subject.objects.all(), slug_field='abbreviation')
    #request_details = RequestSerializer(many=True,read_only=True)

    class Meta:
        model = Course
        fields = '__all__' # or a list of field from model like ('','')
        extra_kwargs = {
            #'url' : {'view_name':'UI-course-detail', 'lookup_field':'course_SRS_Title',
            #        'view_name':'courses-detail', 'lookup_field':'course_SRS_Title'}

        }



    def create(self, validated_data):
        """
        Create and return a new 'Course' instance, given the validated_data.
        """
        print("CourseSerializer validated_data", validated_data)
        instructors_data = validated_data.pop('instructors')
        schools_data = validated_data.pop('course_schools')
        subjects_data = validated_data.pop('course_subjects')
        course = Course.objects.create(**validated_data)
        ##
        ## must loop through adding instructors individually because we cannot do direct assignment
        ##
        for instructor_data in instructors_data:
            print(instructor_data.username, instructor_data)
            course.instructors.add(instructor_data)

        for school_data in schools_data:
            print("school_data",school_data)
            course.course_schools.add(school_data)

        for subject_data in subjects_data:
            print("subject data", subject_data)

        #print(course.data)
        return course

    # this allows the object to be updated!
    def update(self, instance, validated_data):
        """
        Update and return an existing 'Course' instance, given the validated_data.
        """
        print("validated_data", validated_data)
        instance.course_SRS_Title = validated_data.get('course_SRS_Title', instance.course_SRS_Title)

        instance.requested = validated_data.get('requested',instance.requested)
        #print("whoohooohho",instance.instructors, validated_data.get('instructors',instance.instructors))

        # since theses are nested they need to be treated a little differently
        instance.course_schools.set(validated_data.get('course_schools', instance.course_schools))
        instance.instructors.set(validated_data.get('instructors',instance.instructors))
        instance.save()
        print("instance",instance)
        return instance

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    viewset is read only therefore serializer does not support PUT/PATCH
    """

    #courses = serializers.HyperlinkedRelatedField(many=True, view_name='course-detail', read_only=True)
    requests = serializers.HyperlinkedRelatedField(many=True, view_name='request-detail',read_only=True)

    #course_list = CourseSerializer(many=True,read_only=True)
    # this allows to link all the courses with a user
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'username', 'courses','requests')#,'course_list')
        # because courses is a REVERSE relationship on the User model,
        # it will not be included by default when using the ModelSerializer class
        # so we needed to add an explicit field for it.



class RequestSerializer(serializers.HyperlinkedModelSerializer):
    #this adds a field that is not defined in the model
    #url = serializers.HyperlinkedIdentityField(view_name='UI-requests', looku
    print("how???")
    owner = serializers.ReadOnlyField(source='owner.username')
    course_info = CourseSerializer(source='course_requested', read_only=True)

    #course_requested = serializers.SlugRelatedField(many=False,queryset=Course.objects.exclude(requested=True), slug_field='course_SRS_Title')

    # the following line is needed to create the drop down

    #test = CourseSerializer()
    course_requested = serializers.SlugRelatedField(many=False,queryset=Course.objects.all(), slug_field='course_SRS_Title')

    # IF REQUEST STATUS IS CHANGED TO CANCELED IT SHOULD BE DISASSOCIATED FROM COURSE INSTANCE
    # IN ORDER TO PRESERVE THE ONE TO ONE COURSE -> REQUEST RELATIONSHIP
    # IF REQUEST IS MADE THE COURSE INSTANCE SHOULD CHANGE COURSE.REQUESTED to TRUE
    class Meta:
        model = Request
        fields = '__all__' # or a list of field from model like ('','')
        #exclude = ('course_requested',)
        #depth=2

    def create(self, validated_data):
        """
        Create and return a new 'Request' instance, given the validated_data.
        Also get associtated Course instance and set course.requested ==True
        """
        # it must also get associated Course instance and set course.requested = True

        # check that the course is good to be requested
        # - not already requested
        # - user making request is an instructor or acting on behalf of other user


        #course_requested_data = validated_data.pop('course_requested')
        # check that this course.requested==False
        #print("course_requested_data", course_requested_data)
        print(validated_data)

        request_object = Request.objects.create(**validated_data)
        #validated_data['course_requested'].requested = False

        print("RequestSerializer.create", validated_data)
        return request_object

    # this allows the object to be updated!
    def update(self, instance, validated_data):
        """
        Update and return an existing 'Request' instance, given the validated_data.
        """
        # TODO
        # [ ]must check that the course is not already requested?
        # [ ] better/more thorough validation
        instance.course_status = validated_data.get('status',instance.status)

        print("instance.status", instance.status)

        #instance.course = validated_data.get('course_requested', instance.course_requested)
        instance.save()
        return instance


class SchoolSerializer(serializers.HyperlinkedModelSerializer):
    """

    """

    class Meta:
        model = School
        fields = '__all__'

    def create(self,validated_data):
        """
        Create and return a new 'School' instance, given the validated data.
        """
        return School.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing 'School' instance given the validated_data.
        """
        print("ATTEMPTING TO UPDATE SCHOOL")
        print("conext['format']",self.context['format'])

        instance.name = validated_data.get('name', instance.name)
        instance.abbreviation = validated_data.get('abbreviation', instance.abbreviation)
        instance.visible = validated_data.get('visible', instance.visible)
        instance.save()

        return instance

class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    """

    """

    class Meta:
        model = Subject
        fields = '__all__'

    def create(self,validated_data):
        """
        Create and return a new 'Subject' instance, given the validated data.
        """
        return Subject.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing 'Subject' instance given the validated_data.
        """
        print("ATTEMPTING TO UPDATE SUBJECT")
        print("conext['format']",self.context['format'])

        instance.name = validated_data.get('name', instance.name)
        instance.abbreviation = validated_data.get('abbreviation', instance.abbreviation)
        instance.visible = validated_data.get('visible', instance.visible)
        instance.save()

        return instance



class NoticeSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    id = serializers.ReadOnlyField()

    class Meta:
        model = Notice
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new 'Notice' instance, given the validated data.
        """
        return Notice.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing 'Notice' instance given the validated_data.
        """
        instance.notice_text = validated_data.get('notice_text', instance.notice_text)
        instance.save()
        return instance
