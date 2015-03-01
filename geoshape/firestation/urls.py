from .views import FireStationDetailView, DepartmentDetailView, SpatialIntersectView
from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'firestations/(?P<pk>\d+)/?$', FireStationDetailView.as_view(), name='firestation_detail'),
                       url(r'firestations/(?P<state>\w+)/?$', SpatialIntersectView.as_view(), name='firestation_detail'),
                       url(r'(?P<pk>\d+)/?$', DepartmentDetailView.as_view(), name='jurisdiction_detail'),
                       )

