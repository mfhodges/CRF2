from django.test import TestCase


# run with python3 manage.py tests


"""
I need to get several api tokens for different Canvas User Types in order to fully test
permissions !

There also needs to be an admin panel to edit user Permissions
"""



from course.models import Course

class Course.Tests(TestCase):
    """ Course model tests"""

    def test_str(self):
        course = Course(
        # fill in content
        )

        self.assertEquals(
            str(course),
            'something'
        )
