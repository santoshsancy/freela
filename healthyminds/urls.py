from django.conf.urls import url
from django.contrib import admin

from django.contrib.auth.forms import AuthenticationForm

from healthyminds import views as healthyminds_views

urlpatterns = [
	url(r'^WhereToGo/$', healthyminds_views.where_to_go, name="where"),
	url(r'^Welcome/$', healthyminds_views.login_page, {'login_form': AuthenticationForm}, name="welcome"),
	url(r'^home/$', healthyminds_views.homepage, name='homepage'),
	url(r'^$', healthyminds_views.homepage, name='homepage'),

]
