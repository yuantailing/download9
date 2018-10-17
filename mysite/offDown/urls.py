from django.conf.urls import url

from . import views

urlpatterns = [
   # url(r'^$', views.index, kwargs={'domain': 'Blink'}, name='index'),
   # url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
   # url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
   # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^login/$', views.login, name = 'login'),
    url(r'^github_oauth_authorize', views.github_oauth_authorize, name = 'github_oauth_authorize'),
    url(r'^$', views.index, name = 'index'),
    url(r'^logout/$', views.logout, name = 'logout'),
    url(r'^new/byurl/$', views.new_byurl, name = 'new_byurl'),
   # url(r'^new/$', views.new, name = 'new'),
    url(r'^new2/$', views.new2, name = 'new2'),
    url(r'^del/$', views.deleteTask, name = 'deleteTask'),
    url(r'^oauth_redirect/$', views.oauth, name = 'oauth'),
    url(r'^search/$', views.search, name = 'search'),
    url(r'^new/bytorrent/$', views.new_bytorrent, name = 'new_bytorrent'),
   # url(r'^newTorrent/$', views.newTorrent, name = 'newTorrent'),
    url(r'^regist/$', views.regist, name = 'regist'),
    url(r'^gets/$', views.getStatus, name = 'getStatus'),
    url(r'^newTorrent2/$', views.newTorrent2, name = 'newTorrent2'),
    #url(r'^new/bytorrent/$', views.new_bytorrent, name = 'new_bytorrent'),
]


'''
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]
'''