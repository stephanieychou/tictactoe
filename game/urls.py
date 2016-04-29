from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index')
#	url(r'^startGame/$', views.startGame, name='startGame'),
#	url(r'^makeMove/(?P<board_id>[0-9]+)$', views.makeMove, name='makeMove')
]
