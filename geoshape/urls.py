from django.conf.urls import patterns, include, url
from geonode.urls import urlpatterns as geonode_url_patterns
from geoshape.firestation.api import StaffingResource, FireStationResource
from maploom.geonode.urls import urlpatterns as maploom_urls
from tastypie.api import Api
from firestation.urls import urlpatterns as firestation_urls
from firestation.views import Home

v1_api = Api(api_name='v1')
v1_api.register(StaffingResource())
v1_api.register(FireStationResource())


urlpatterns = patterns('',
                       url(r'^$', Home.as_view(), name='firestation_home'),
                       (r'^file-service/', include('geoshape.file_service.urls')),
                       (r'^proxy/', 'geoshape.views.proxy'),
                       (r'^api/', include(v1_api.urls)),
                       )

urlpatterns += geonode_url_patterns
urlpatterns += maploom_urls
urlpatterns += firestation_urls