from django.conf.urls import patterns, url
from qoe import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^init/', views.initQoE, name='init'),
	url(r'^query/', views.query, name='query'),
)
