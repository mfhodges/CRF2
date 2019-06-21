from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from configparser import ConfigParser


config = ConfigParser()
config.read('config/config.ini')


class Command(BaseCommand):
    help = 'Create random users'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of users to be created')
        parser.add_argument('-p', '--prefix', type=str, help='Define a username prefix')
        parser.add_argument('-a', '--admin', action='store_true', help='Create an admin account')
        parser.add_argument('-c', '--courseware', action='store_true', help='Quick add Courseware Support team as Admins')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        prefix = kwargs['prefix']
        admin = kwargs['admin']
        courseware = kwargs['courseware']

        for i in range(total):
            if prefix:
                username = '{prefix}_{random_string}'.format(prefix=prefix, random_string=get_random_string())
            else:
                username = get_random_string()

            if admin:
                User.objects.create_superuser(username=username, email='', password='123')
            elif courseware:

                for (key,value) in config.items('users'):
                    try:
                        User.objects.create_superuser(username=key,email='',password=value)
                    except:
                        print("didnt add user " + key)
            else:
                User.objects.create_user(username=username, email='', password='123')
