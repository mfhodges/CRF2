"""crf2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include

from django.views.generic import TemplateView

from django.conf.urls import include, url

from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.contrib.staticfiles.templatetags.staticfiles import static


admin.site.site_header = 'Course Request Form Administration'
admin.site.site_title = 'ADMIN: Site Request'
# use re path to validate urls
# https://docs.djangoproject.com/en/2.1/topics/http/urls/#using-regular-expressions

urlpatterns = [

    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', include('course.urls')),

    # --------------- login url/view -------------------
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='login.html',
        extra_context={'next': '/',},
        ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        template_name='logout.html',
        ), name='logout'),

]
#path('course', CourseView.as_view()),
