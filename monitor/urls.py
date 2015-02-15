from django.conf.urls import patterns, url
from monitor import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^load/', views.view_load, name='view_load'),
	url(r'^bw/', views.view_bw, name='view_bw'),
)
