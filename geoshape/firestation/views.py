from .models import FireStation, FireDepartment
from django.views.generic import DetailView, ListView, TemplateView
from geoshape.usgs.models import StateorTerritoryHigh, CountyorEquivalent, IncorporatedPlace
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from random import randint

class DepartmentDetailView(DetailView):
    model = FireDepartment
    template_name = 'firestation/department_detail.html'
    page = 1
    objects_per_page = 10

    def get_context_data(self, **kwargs):
        context = super(DepartmentDetailView, self).get_context_data(**kwargs)

        page = self.request.GET.get('page')

        paginator = Paginator(context['firedepartment'].firestation_set.all(), self.objects_per_page)

        try:
            stations = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            stations = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            stations = paginator.page(paginator.num_pages)

        context['firestations'] = stations
        context['residential_fires'] = map(lambda year: (year, randint(0, 500)), reversed(range(2002, 2014)))
        return context


class FireStationDetailView(DetailView):
    model = FireStation


class FireDepartmentListView(ListView):
    model = FireDepartment
    paginate_by = 100
    queryset = FireDepartment.priority_departments.all()

    def get_queryset(self):
        queryset = super(FireDepartmentListView, self).get_queryset()
        if self.kwargs.get('state'):
            queryset = queryset.filter(state__iexact=self.kwargs['state'])
        return queryset.order_by('name')


class SpatialIntersectView(ListView):
    model = FireStation
    template_name = 'firestation/department_detail.html'
    context_object_name = 'firestations'

    def get_queryset(self):
        self.object = get_object_or_404(StateorTerritoryHigh, state_name__iexact=self.kwargs.get('state'))
        return FireStation.objects.filter(geom__intersects=self.object.geom)

    def get_context_data(self, **kwargs):
        context = super(SpatialIntersectView, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context


class SetDistrictView(DetailView):
    model = CountyorEquivalent
    template_name = 'firestation/set_department.html'

    def get_context_data(self, **kwargs):
        context = super(SetDistrictView, self).get_context_data(**kwargs)
        context['stations'] = FireStation.objects.filter(geom__intersects=self.object.geom)
        context['incorporated_places'] = IncorporatedPlace.objects.filter(geom__intersects=self.object.geom)
        next_fs = FireStation.objects.filter(department__isnull=True, state='VA').order_by('?')

        if next_fs:
            context['next'] = CountyorEquivalent.objects.filter(geom__intersects=next_fs[0].geom)[0]
        return context

    def post(self, request, *args, **kwargs):
        county = self.get_object()
        try:
            fd = FireDepartment.objects.get(content_type=ContentType.objects.get_for_model(CountyorEquivalent),
                                            object_id=county.id)
        except FireDepartment.DoesNotExist:
            fd = FireDepartment.objects.create(name='{0} {1} Fire Department'.format(county.county_name, county.get_fcode_display()), content_object=county,
                                               geom=county.geom)
            fd.save()
            FireStation.objects.filter(geom__intersects=county.geom).update(department=fd)
            return HttpResponseRedirect(reverse('set_fire_district', args=[county.id]))


class Stats(TemplateView):
    template_name='firestation/firestation_stats.html'

    def get_context_data(self, **kwargs):
        context = super(Stats, self).get_context_data(**kwargs)
        context['stations'] = FireStation.objects.all()
        context['departments'] = FireDepartment.objects.all()
        context['stations_with_fdid'] = FireStation.objects.filter(fdid__isnull=False)
        context['stations_with_departments'] = FireStation.objects.filter(department__isnull=False)
        context['departments_with_government_unit'] = FireDepartment.objects.filter(object_id__isnull=True)
        return context

class Home(TemplateView):
    template_name = 'firestation/home.html'
