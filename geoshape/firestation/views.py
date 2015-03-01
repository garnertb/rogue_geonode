from .models import FireStation, FireDepartment
from django.views.generic import DetailView, ListView
from geoshape.usgs.models import StateorTerritoryHigh
from django.shortcuts import get_object_or_404


class DepartmentDetailView(DetailView):
    model = FireDepartment
    template_name = 'firestation/department_detail.html'


class SpatialIntersectView(ListView):
    model = FireStation
    template_name = 'firestation/department_detail.html'
    context_object_name = 'firestations'

    def get_queryset(self):
        self.state = get_object_or_404(StateorTerritoryHigh, state_name__iexact=self.kwargs.get('state'))
        return FireStation.objects.filter(geom__intersects=self.state.geom)

    def get_context_data(self, **kwargs):
        context = super(SpatialIntersectView, self).get_context_data(**kwargs)
        context['object'] = self.state
        return context

class FireStationDetailView(DetailView):
    model = FireStation
