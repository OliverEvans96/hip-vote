# File Name: urls.py
#                           GNU GPL LICENSE                            #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
#                                                                      #
# Copyright Oliver Evans 2017 <oliverevans96@gmail.com>                #
#                                                                      #
# This program is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the         #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>. #
#                                                                      #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', login_required(views.IndexView.as_view(),login_url='/account/login'), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', login_required(views.DetailView.as_view(),login_url='/account/login'), name='detail'),
    url(r'^(?P<pk>[0-9]+)/results/$', login_required(views.ResultsView.as_view(),login_url='/account/login'), name='results'),
    url(r'^(?P<pk>[0-9]+)/confirm/$', login_required(views.ResultsView.as_view(),login_url='/account/login'), name='confirm'),
    url(r'^(?P<pk>[0-9]+)/vote/$', login_required(views.vote,login_url='/account/login'), name='vote'),
]
