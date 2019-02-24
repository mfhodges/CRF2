from django.db import models
from django.conf import settings

from django.contrib.auth.models import User

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

    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.abbreviation)

class Subject(models.Model):
    """
    mapping of Subject (i.e. 'ANAT' -> Anatomy ) to SubjectArea objects
    requires list_asView but not individual object view
    """

    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.abbreviation)





class Course(models.Model):

    SPRING = 'A'
    SUMMER = 'B'
    FALL = 'C'
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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created', on_delete=models.CASCADE) #this is who edited it
    updated = models.DateTimeField(auto_now=True)
    instructors = models.ManyToManyField(User,related_name='courses')
    course_term = models.CharField(
        max_length=1,choices = TERM_CHOICES,) # self.course_term would == self.SPRING || self.FALL || self.SUMMER
    course_activity = models.CharField(
        max_length=3,choices = ACTIVITY_CHOICES,)

    # course_SRS_Title must not allow spaces
    course_SRS_Title = models.CharField(max_length=250,unique=True, primary_key=True, blank=False) # unique and primary_key means that is the lookup_field

    course_subjects = models.ManyToManyField(Subject,related_name='courses') # one to many
    course_schools = models.ManyToManyField(School,related_name='courses')# one to many
    course_name = models.CharField(max_length=250) # Human Readable Name i.e. Late Antique Arts

    requested =  models.BooleanField(default=False)# False -> not requested


    """
    course_section = models.CharField(max_length=250) # need a validator on this

    course_activity = models.CharField(max_length=250)# need a validator on this

    course_instructor = models.ForeignKey('auth.User', related_name='courses', on_delete=models.CASCADE) # this is not correct!
    course_ = models.CharField(max_length=250)# need a validator on this
    """


    """
    course_section = //i.e. AFRC050 402 2019A - must be unique
    course_term = // A , B , or C
    course_year = //
    course_SRS_Title = // name of course
    course_subject_area = // This will be its own model with views!, can be many
    course_school = // This will be its own model with views! , can be many
    course_activity = // choice field ('LEC',...)
    course_crosslistings = // Link to other Course objects! , can be many
    course_instructor = // this will be its own model, can be many

    ### CANVAS SITE DETAILS ###
    # this stuff gets pulled n synced from Canvas and is different from the information
    # about the Canvas site in the Request object

    course_site_url = // url to the canvas site
    """
    #
    #
    class Meta:
        ordering = ('created',)


    def save(self, *args, **kwargs):
        """
        some text
        """

        super(Course, self).save(*args,**kwargs)

    def __str__(self):
        return self.course_SRS_Title # this should be changed to the SRS name



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


class Request(models.Model):
    REQUEST_PROCESS_CHOICES =(
        ('COMPLETED','Completed'),
        ('IN_PROCESS', 'In Process'),
        ('CANCELED' , 'Canceled'),
        ('APPROVED', 'Approved'),
        ('SUBMITTED', 'Submitted'),)
        # The first element in each tuple is the actual value to be set on the model,
        #and the second element is the human-readable name.

    course_requested = models.OneToOneField(
        Course,
        on_delete=models.CASCADE)
        #primary_key=True) # once the course is deleted the request will be deleted too.

    copy_from_course =models.CharField(max_length=100, null=True)
    # this should be a list of courses they have rights too
    # SuperUsers have access to all courses



    status = models.CharField(max_length=20, choices=REQUEST_PROCESS_CHOICES,default='SUBMITTED' )

    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='requests', on_delete=models.CASCADE , default=None)#should not delete when user is deleted

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        """
        some text
        """

        super(Request, self).save(*args,**kwargs)


    def __str__(self):
        return " \"%s\" site request" % ( self.course_requested.course_SRS_Title)

#class SubjectArea(models.Model):
"""
 mapping of Subject area code and name. boolean value of displayed in CRF2 or not
 requires list_asView but not individual object view
"""







#class User(models.User):
#"""
# needs Name , pennkey, email and Role ( maybe not role bc that could be another class ?)
# permissions of each user should be defined by the subclass
# https://docs.djangoproject.com/en/2.1/ref/contrib/auth/#user-model
#"""
#    full_name = models.CharField(verbose_name='full name', max_length=100)# Full name i.e. 'John Doe'
#
#    pennkey = models.TextField()#needs validator
#    email = models.EmailField()

#    def save(self, *args, **kwargs):
#        """
#        some text
#        """
#        super(User, self).save(*args,**kwargs)


# THIS CLASS SHOULD EXPAND ON USER MODEL !
#class Instructor(models.Model):
#"""
# name and associated pennkey
# doesnt require view
# should have function that gets all course objects from CRF2 db for a particular sem
#"""

#class Request(models.Model):
#"""
# COPY BELOW
#   class Article(models.Model):
#    STATUSES = Choices(
#        (0, 'draft', _('draft')),
#        (1, 'published', _('published'))   )
#    status = models.IntegerField(choices=STATUSES, default=STATUSES.draft)
#"""
#   def save(self, *args, **kwargs):
#       self.request = # a func that generates the text for the api call to make the course ( doesnt actually execute )
#                   # hence the api call is generated when the request object is saved but not excuted until approved
#       super(Request, self).save(*args, **kwargs)





#class (models.Model):
#"""
#
#"""





"""
Below is is how the course to subject `ownership` should be handled since There
can be multiple 'Groups'/'SubjectAreas' for a 'Person'/'Course'

class Person(models.Model):
    name = models.CharField(max_length=50)

class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(
        Person,
        through='Membership',
        through_fields=('group', 'person'),
    )

class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    inviter = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="membership_invites",
    )
    invite_reason = models.CharField(max_length=64)
"""
