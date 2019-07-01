from django.apps import AppConfig
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from .signals import request_cleanup

class CourseConfig(AppConfig):
    name = 'course'
