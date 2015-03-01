import requests
import json
map_services = range(11, 20)
map_services.pop(map_services.index(17))

services = {}

for map_service in map_services:
    url = "http://services.nationalmap.gov/arcgis/rest/services/govunits/MapServer/{0}?f=pjson".format(map_service)
    resp = requests.get(url)
    content = json.loads(resp.content)
    services[map_service] = content

esri_mapping = {
    'esriFieldTypeOID': 'IntegerField',
    'esriFieldTypeInteger': 'IntegerField',
    'esriFieldTypeString': 'CharField',
    'esriFieldTypeDate': 'DateField',
    'esriFieldTypeDouble': 'DoubleField',
    'esriFieldTypeGlobalID': 'CharField'
}

class ORM(object):
    integer_field = 'IntegerField'
    string_field = 'CharField'
    date_field = 'DateField'
    date_time_field = 'DateTimeField'
    double_field = 'DoubleField'

    def init(self):
        pass

class ArcGISORM(object):
    integer_field = 'esriFieldTypeOID'
    string_field = 'esriFieldTypeString'
    date_field = 'esriFieldTypeDate'
    double_field = 'esriFieldTypeDouble'

    def init(self):
        pass


class DjangoORM(ORM):
    pass


class ArcGISServerField(object):

    def __init__(self, name=None, type=None, length=None, domain=None, alias=None, **kwargs):
        self.name = name.lower()
        self.field_type = type
        self.length = length
        self.domain = domain
        self.alias = alias

    def get_choices(self):
        options = {}

        if self.domain:
            if self.domain.get('type') == 'codedValue':
                choices = []
                for choice in self.domain.get('codedValues'):
                    choices.append((choice['code'], choice['name']))
                options[self.domain['name'].replace(' ', '_').lower()] = choices

        return options

    def to_django(self):
        django_type = esri_mapping.get(self.field_type)
        options = {'null':True, 'blank':True}

        if self.length:
            options['max_length'] = self.length

        if self.alias and self.alias.lower() != self.name.lower():
            options['verbose_name'] = self.alias

        choices = self.get_choices()

        if choices:
            options['choices'] = choices.keys()[0]

        option_string = ', '.join(['{0}={1}'.format(param, value) for param, value in options.items()])
        return '{0} = models.{1}({2})'.format(self.name, django_type, option_string)

class Model(object):

    def __init__(self, fields):
        self.fields = fields
        self.output = ''

def esri_field_to_django(field):
    response = '{name} = models.{type}'
    field_type = esri_mapping.get(field['type'])
    params = {}
    if field.get('alias'):
        params

    return response.format(name=field['name'], type=field_type)

fields = {}

for service, data in services.items():
    print "class {0}(USGSBase): ".format(data['name'].replace(' ', ''))
    print "    service_id = {0}".format(service)
    field_strs = []
    for field in data['fields']:

        if field['name'].lower() in ['shape_area', 'shape_length', 'shape', u'source_originator', u'globalid', u'source_featureid', u'data_security', u'permanent_identifier', u'loaddate', u'gnis_name', u'distribution_policy',
                                     u'areasqkm', u'source_datadesc', u'source_datasetid', u'gnis_id', 'ftype']:
            continue

        try:
            fields[field["name"]] += 1
        except KeyError:
            fields[field["name"]] = 0

        new_field = ArcGISServerField(**field)
        choices = new_field.get_choices()
        if choices:
            print "    {0} = {1}".format(choices.keys()[0], choices.values()[0])
        field_strs.append("    " + new_field.to_django())

    print '\n'.join(field_strs)
    print '    geom = models.PolygonField()'



    print
    print
    print

x = []
for field, value in fields.items():
    if value == 7:
        x.append(field.lower())
print x