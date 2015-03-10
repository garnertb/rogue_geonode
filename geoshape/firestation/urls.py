from .views import FireStationDetailView, DepartmentDetailView, Stats, FireDepartmentListView
from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'fire-stations/(?P<pk>\d+)/?$', FireStationDetailView.as_view(), name='firestation_detail'),
                       url(r'fire-departments/(?P<pk>\d+)/?$', DepartmentDetailView.as_view(), name='firedepartment_detail'),
                       url(r'fire-departments/?$', FireDepartmentListView.as_view(), name='firedepartment_list'),
                       url(r'fire-departments/(?P<state>\w+)/?$', FireDepartmentListView.as_view(), name='firedepartment_list'),
                       url(r'(?P<pk>\d+)/?$', DepartmentDetailView.as_view(), name='jurisdiction_detail'),
                       url(r'stats/fire-stations/?$', Stats.as_view(), name='firestation_stats'),
                       )

