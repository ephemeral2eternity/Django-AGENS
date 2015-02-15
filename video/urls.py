from django.conf.urls import patterns, url
from video import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^init/', views.initVideo, name='init'),
	url(r'^query/', views.query, name='query'),
	url(r'^add/', views.add, name='add'),
)
