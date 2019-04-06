from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
import datetime
import django.core.exceptions

# This model is to represent a Course object in the CRF
# the meta-data that is important with this is information that will help the course be
# discoverable in the CRF2. all of these objects with be populated from the data
# provided by the Registrar.

# https://docs.djangoproject.com/en/2.1/ref/models/fields/#choices

# add help text: https://docs.djangoproject.com/en/2.1/ref/models/fields/#help-text


"""
class User(User):
    pass # since its already defined in Courses with the serializer
    #username == pennkey


    # most will be done like: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username
"""
#class Instructor(models.auth.User):
"""
        this class expands on the User model
"""

#    def __str__(self):
#        return self.username

class School(models.Model):
    """
    mapping of School (i.e. 'Arts & Sciences') to SubjectArea objects
    requires list_asView but not individual object view
    """

    name = models.CharField(max_length=50,unique=True)
    abbreviation = models.CharField(max_length=10,unique=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.abbreviation)

class Subject(models.Model):
    """
    mapping of Subject (i.e. 'ANAT' -> Anatomy ) to SubjectArea objects
    requires list_asView but not individual object view
    """

    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10,unique=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.abbreviation)

class CanvasSite(models.Model):
    """
    this contains all the relevant info about the canvas site once it has been created
    """
    url = models.URLField()



class CourseManager(models.Manager):
    def has_request(self):
        return super().get_queryset().filter(requested=True)

    #def submitted(self)





class Course(models.Model):

    SPRING = 'A'
    SUMMER = 'B'
    FALL = 'C'

    # dont change these variable names -- used in views.py
    TERM_CHOICES = (
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
        (FALL, 'Fall'))

    ACTIVITY_CHOICES = (
        ('LEC', 'Lecture'),
        ('SEM', 'Seminar'),
        ('LAB', 'Laboratory')
    )

    created = models.DateTimeField(auto_now_add=True)
    #id = models.CharField(max_length=250) # this is a number
    # models.ForeignKey('auth.User', related_name='requests', on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', related_name='created', on_delete=models.CASCADE) #this is who edited it
    updated = models.DateTimeField(auto_now=True)
    instructors = models.ManyToManyField(User,related_name='courses',blank=True) # should be allowed to be null --> "STAFF"
    course_term = models.CharField(
        max_length=1,choices = TERM_CHOICES,) # self.course_term would == self.SPRING || self.FALL || self.SUMMER
    course_activity = models.CharField(
        max_length=3,choices = ACTIVITY_CHOICES,)

    # course_SRS_Title must not allow spaces
    course_code = models.CharField(max_length=250,unique=True, primary_key=True, blank=False) # unique and primary_key means that is the lookup_field
    course_subjects = models.ManyToManyField(Subject,related_name='courses') # one to many
    course_schools = models.ManyToManyField(School,related_name='courses')# one to many
    course_name = models.CharField(max_length=250) # Human Readable Name i.e. Late Antique Arts
    crosslisted = models.ManyToManyField("self", blank=True, symmetrical=True, default=None)

    requested =  models.BooleanField(default=False)# False -> not requested



    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        """
        some text
        """
        print("saving Course instance")
        print("self.pk",self.pk)
        super().save(*args,**kwargs) #super(Course, self)
        # here is where you do the updating of cross listed instances

    #def set_crosslistings(self):

    def get_request(self):
        possibilities = self.crosslisted.all()
        print("possibilities",possibilities)
        try:
            print("course",self)
            requestinfo = self.request
            return requestinfo
        except Request.DoesNotExist:
            print("Request.DoesNotExist!")

        for course in possibilities:
            try:
                print("course",course)
                requestinfo = course.request
                return requestinfo
            except Request.DoesNotExist:
                print("Request.DoesNotExist!")

        #return error
        
    def get_subjects(self):
        return ",\n".join([sub.abbreviation for sub in self.course_subjects.all()])


    def get_schools(self):
        return ",\n".join([sch.abbreviation for sch in self.course_schools.all()])


    def get_instructors(self):
        #check if blank?
        print("lets go to funkie town",self.instructors.all(), )
        if not self.instructors.all().exists():
            return("STAFF")
        return ",\n".join([inst.username for inst in self.instructors.all()])


    def __str__(self):
        return self.course_code

    def __unicode__(self):
        return self.course_code

    objects = models.Manager()
    CourseManager = CourseManager()



    #def get_absolute_url(self):
    #    """
    #    get_absolute_url should return a string of the url that is
    #    associated with that particular model instance. This is
    #    especially useful in templates and redirect responses.
    #    """
    #    # determine which view?
    #    return reverse('vegetable', pks={pk: self.pk})


class Notice(models.Model):
    """
    this is a class that handles system wide notifications
    for earilest and latest methods see: https://simpleisbetterthancomplex.com/tips/2016/10/06/django-tip-17-earliest-and-latest.html
    """
    # TODO
    # [ ] fix __str__ and add better admin table view instead
    # [ ] put on request form not just home page

    creation_date = models.DateTimeField(auto_now_add=True)
    notice_heading = models.CharField(max_length=100)
    notice_text = models.TextField(max_length=1000) # this should be some html ?
    owner = models.ForeignKey('auth.User', related_name='notices', on_delete=models.CASCADE) #this is who edited it
    updated_date = models.DateTimeField(auto_now=True)


    class Meta:
        get_latest_by = 'updated_date' # allows .latest()


    def __str__(self):

        return "(#"+str(self.pk) + ") " + self.creation_date.strftime('%m-%d-%Y') +": \""+ self.notice_heading+ "\" by " + self.owner.username

#class RequestManager(models.Manager):
#    def submitted(self):



class Request(models.Model):
    REQUEST_PROCESS_CHOICES =(
        ('COMPLETED','Completed'),
        ('IN_PROCESS', 'In Process'),
        ('CANCELED' , 'Canceled'),
        ('APPROVED', 'Approved'),
        ('SUBMITTED', 'Submitted'),
        ('LOCKED','Locked'),)
        # The first element in each tuple is the actual value to be set on the model,
        #and the second element is the human-readable name.

    course_requested = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        primary_key=True) # once the course is deleted the request will be deleted too.

    copy_from_course =models.CharField(max_length=100, null=True,default=None) # previously content source
    # this should be a list of courses they have rights too
    # SuperUsers have access to all courses
    title_override = models.CharField(max_length=100,null=True,default=None) # previously SRS title override
    additional_instructions = models.TextField(blank=True,default=None, null=True)
    reserves = models.BooleanField(default=False)
    canvas_instance = models.ForeignKey(CanvasSite,related_name='canvas', on_delete=models.CASCADE,null=True, blank=True )

    # NOTE! needs something for multisection course sites!


    status = models.CharField(max_length=20, choices=REQUEST_PROCESS_CHOICES,default='SUBMITTED' )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey('auth.User', related_name='requests', on_delete=models.CASCADE)#should not delete when user is deleted
    masquerade = models.CharField(max_length=20,null=True)

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        """
        some text
        """
        print(self.status,args,kwargs)
        print("(Model.py) Request self.pk",self.pk)
        super(Request, self).save(*args,**kwargs)


    def __str__(self):
        return " \"%s\" site request" % ( self.course_requested.course_code)

#class SubjectArea(models.Model):
"""
 mapping of Subject area code and name. boolean value of displayed in CRF2 or not
 requires list_asView but not individual object view
"""



# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
# see section on Extending User Model Using a One-To-One Link
class AutoAdd(models.Model):
    ROLE_CHOICES = (
    ('ta','TA'),
    ('instructor','Instructor'),
    ('designer','Designer'),
    ('librarian','Librarian'),)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    school = models.ForeignKey(School,on_delete=models.CASCADE, blank=False)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE, blank=False)
    role = models.CharField(
            max_length=10,choices = ROLE_CHOICES,)

    #def __str__(self):
    #    return self.






class UpdateLog(models.Model):
    """
    this is how to store
    """
    MANAGER_CHOICES = (
    ('a','A'),
    ('b','B'),
    ('c','C'),
    )

    created = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    process= models.CharField(max_length=10,choices = MANAGER_CHOICES)
