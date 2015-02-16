from django.conf.urls import patterns, url
from overlay import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^init/', views.initServer, name='init'),
	url(r'^query/', views.query, name='query'),
	url(r'^peer/', views.peer, name='peer'),
)
