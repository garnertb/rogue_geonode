from .models import FireStation, FireDepartment, Staffing
from django.contrib.gis import admin


class FireStationAdmin(admin.OSMGeoAdmin):
    list_display = ['state', 'name']
    list_filter = ['state', 'ftype']
    search_fields = ['name', 'state', 'city']
    readonly_fields = ['permanent_identifier', 'source_featureid', 'source_datasetid', 'objectid', 'globalid',
                       'gnis_id', 'foot_id', 'complex_id']


class FireStationInline(admin.TabularInline):
    model = FireStation
    fk_name = 'department'
    extra = 0
    readonly_fields = ['permanent_identifier', 'source_featureid', 'source_datasetid', 'objectid', 'globalid',
                       'gnis_id', 'foot_id', 'complex_id']


class FireDepartmentAdmin(admin.OSMGeoAdmin):
    inlines = [FireStationInline]


class ResponseCapabilityAdmin(admin.OSMGeoAdmin):
    pass


admin.site.register(FireStation, FireStationAdmin)
admin.site.register(FireDepartment, FireDepartmentAdmin)
admin.site.register(Staffing, ResponseCapabilityAdmin)
