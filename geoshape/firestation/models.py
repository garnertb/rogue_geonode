import datetime
import json
import requests
import sys
import csv
import os
import us

from .managers import PriorityDepartmentsManager

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, MultiPolygon
from django.core.validators import MaxValueValidator
from django.core.urlresolvers import reverse
from django.db.transaction import rollback
from django.db.utils import IntegrityError
from geoshape.firecares_core.models import Address
from phonenumber_field.modelfields import PhoneNumberField
from geoshape.firecares_core.models import Country
from geoshape.core.validators import validate_choice
from genericm2m.models import RelatedObjectsDescriptor

class USGSStructureData(models.Model):
    """
    Models structure data from the USGS National Map.

    Schema from: http://services.nationalmap.gov/arcgis/rest/services/structures/MapServer/1?f=json
    """
    DATA_SECURITY_CHOICES = [(0, 'Unknown'),
                             (1, 'Top Secret'),
                             (2, 'Secret'),
                             (3, 'Confidential'),
                             (4, 'Restricted'),
                             (5, 'Unclassified'),
                             (6, 'Sensitive')]

    DISTRIBUTION_POLICY_CHOICES = [('A1', 'Emergency Service Provider - Internal Use Only'),
                                   ('A2', 'Emergency Service Provider - Bitmap Display Via Web'),
                                   ('A3', 'Emergency Service Provider - Free Distribution to Third Parties'),
                                   ('A4', 'Emergency Service Provider - Free Distribution to Third Parties Via'
                                          ' Internet'),
                                   ('B1', 'Government Agencies or Their Delegated Agents - Internal Use Only'),
                                   ('B2', 'Government Agencies or Their Delegated Agents - Bitmap Display Via Web'),
                                   ('B3', 'Government Agencies or Their Delegated Agents - Free Distribution to Third'
                                          ' Parties'),
                                   ('B4', 'Government Agencies or Their Delegated Agents - Free Distribution to Third'
                                          ' Parties Via Internet'),
                                   ('C1', 'Other Public or Educational Institutions - Internal Use Only'),
                                   ('C2', 'Other Public or Educational Institutions - Bitmap Display Via Web'),
                                   ('C3', 'Other Public or Educational Institutions - Free Distribution to Third'
                                          ' Parties'),
                                   ('C4', 'Other Public or Educational Institutions - Free Distribution to Third'
                                          ' Parties Via Internet'),
                                   ('D1', 'Data Contributors - Internal Use Only'), ('D2', 'Data Contributors - '
                                                                                           'Bitmap Display Via Web'),
                                   ('D3', 'Data Contributors - Free Distribution to Third Parties'),
                                   ('D4', 'Data Contributors - Free Distribution to Third Parties Via Internet'),
                                   ('E1', 'Public Domain - Internal Use Only'), ('E2', 'Public Domain - Bitmap'
                                                                                       ' Display Via Web'),
                                   ('E3', 'Public Domain - Free Distribution to Third Parties'),
                                   ('E4', 'Public Domain - Free Distribution to Third Parties Via Internet')]

    FCODE_CHOICES = [(81000, 'Transportation Facility'),
                     (81006, 'Airport Terminal'),
                     (81008, 'Air Support / Maintenance Facility'),
                     (81010, 'Air Traffic Control Center / Command Center'),
                     (81011, 'Boat Ramp / Dock'),
                     (81012, 'Bridge'),
                     (81014, 'Bridge:  Light Rail / Subway'),
                     (81016, 'Bridge:  Railroad'),
                     (81018, 'Bridge:  Road'),
                     (81020, 'Border Crossing / Port of Entry'),
                     (81022, 'Bus Station / Dispatch Facility'),
                     (81024, 'Ferry Terminal / Dispatch Facility'),
                     (81025, 'Harbor / Marina'),
                     (81026, 'Helipad / Heliport / Helispot'),
                     (81028, 'Launch Facility'),
                     (81030, 'Launch Pad'),
                     (81032, 'Light Rail Power Substation'),
                     (81034, 'Light Rail Station'),
                     (81036, 'Park and Ride / Commuter Lot'),
                     (81038, 'Parking Lot Structure / Garage'),
                     (81040, 'Pier / Wharf / Quay / Mole'),
                     (81042, 'Port Facility'),
                     (81044, 'Port Facility: Commercial Port'),
                     (81046, 'Port Facility: Crane'),
                     (81048, 'Port Facility: Maintenance and Fuel Facility'),
                     (81050, 'Port Facility: Modal Transfer Facility'),
                     (81052, 'Port Facility: Passenger Terminal'),
                     (81054, 'Port Facility: Warehouse Storage / Container Yard'),
                     (81056, 'Railroad Facility'),
                     (81058, 'Railroad Command / Control Facility'),
                     (81060, 'Railroad Freight Loading Facility'),
                     (81062, 'Railroad Maintenance / Fuel Facility'),
                     (81064, 'Railroad Roundhouse / Turntable'),
                     (81066, 'Railroad Station'),
                     (81068, 'Railroad Yard'),
                     (81070, 'Rest Stop / Roadside Park'),
                     (81072, 'Seaplane Anchorage / Base'),
                     (81073, 'Snowshed'),
                     (81074, 'Subway Station'),
                     (81076, 'Toll Booth / Plaza'),
                     (81078, 'Truck Stop'),
                     (81080, 'Tunnel'),
                     (81082, 'Tunnel:  Light Rail / Subway'),
                     (81084, 'Tunnel:  Road'),
                     (81086, 'Tunnel:  Railroad'),
                     (81088, 'Weigh Station / Inspection Station')]

    ISLANDMARK_CHOICES = [(1, 'Yes'),
                          (2, 'No'),
                          (0, 'Unknown')]

    POINTLOCATIONTYPE_CHOICES = [(0, 'Unknown'),
                                 (1, 'Centroid'),
                                 (2, 'Egress or Entrance'),
                                 (3, 'Turn-off location'),
                                 (4, 'Approximate')]

    ADMINTYPE_CHOICES = [(0, 'Unknown'),
                         (1, 'Federal'),
                         (2, 'Tribal'),
                         (3, 'State'),
                         (4, 'Regional'),
                         (5, 'County'),
                         (6, 'Municipal'),
                         (7, 'Private')]


    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objectid = models.IntegerField(unique=True, null=True, blank=True)
    permanent_identifier = models.CharField(max_length=40, null=True, blank=True)
    source_featureid = models.CharField(max_length=40, null=True, blank=True)
    source_datasetid = models.CharField(max_length=40, null=True, blank=True)
    source_datadesc = models.CharField(max_length=100, null=True, blank=True)
    source_originator = models.CharField(max_length=130, null=True, blank=True)
    data_security = models.IntegerField(blank=True, null=True, choices=DATA_SECURITY_CHOICES)
    distribution_policy = models.CharField(max_length=4, choices=DISTRIBUTION_POLICY_CHOICES, null=True, blank=True)
    loaddate = models.DateTimeField(null=True, blank=True)
    ftype = models.CharField(blank=True, null=True, max_length=50)
    fcode = models.IntegerField(blank=True, null=True, choices=FCODE_CHOICES)
    name = models.CharField(max_length=100, null=True, blank=True)
    islandmark = models.IntegerField(null=True, blank=True, choices=ISLANDMARK_CHOICES, verbose_name='Landmark')
    pointlocationtype = models.IntegerField(null=True, blank=True, choices=POINTLOCATIONTYPE_CHOICES,
                                            verbose_name='Point Type')
    admintype = models.IntegerField(null=True, blank=True, choices=ADMINTYPE_CHOICES)
    addressbuildingname = models.CharField(max_length=60, null=True, blank=True, verbose_name='Building Name')
    address = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    gnis_id = models.CharField(max_length=10, null=True, blank=True)
    foot_id = models.CharField(max_length=40, null=True, blank=True)
    complex_id = models.CharField(max_length=40, null=True, blank=True)
    globalid = models.CharField(max_length=38, null=True, blank=True)
    geom = models.PointField()
    objects = models.GeoManager()

    def __unicode__(self):
        return u'{state}, {city}, {name}'.format(name=self.name, state=self.state, city=self.city)

    def full_address(self):
        return u'{address}, {city}, {state}, {zipcode}'.format(address=self.address, city=self.city, state=self.state,
                                                               zipcode=self.zipcode)

    class Meta:
        ordering = ('state', 'city', 'name')


    @classmethod
    def count_differential(cls):
        """
        Reports the count differential between the upstream service and this table.
        """
        url = 'http://services.nationalmap.gov/arcgis/rest/services/govunits/MapServer/{0}/query?' \
              'where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&' \
              'spatialRel=esriSpatialRelIntersects&relationParam=&outFields=&returnGeometry=true' \
              '&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=true&orderByFields=' \
              '&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&' \
              'returnDistinctValues=false&f=pjson'

        response = requests.get(url.format(cls.service_id))

        if response.ok:
            response_js = json.loads(response.content)
            upstream_count = response_js.get('count')

            if upstream_count:
                local_count = cls.objects.all().count()
                print 'The upstream service has: {0} features.'.format(upstream_count)
                print 'The local model {1} has: {0} features.'.format(local_count, cls.__name__)
                return local_count - upstream_count


class FireDepartment(models.Model):
    """
    Models Fire Departments.
    """

    DEPARTMENT_TYPE_CHOICES = [
        ('Volunteer', 'Volunteer'),
        ('Mostly Volunteer', 'Mostly Volunteer'),
        ('Career', 'Career'),
        ('Mostly Career', 'Mostly Career'),
    ]

    REGION_CHOICES = [
        ('Northeast', 'Northeast'),
        ('West', 'West'),
        ('South', 'South'),
        ('Midwest', 'Midwest'),
        (None, '')
    ]

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)
    fdid = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    headquarters_address = models.ForeignKey(Address, null=True, blank=True, related_name='firedepartment_headquarters')
    mail_address = models.ForeignKey(Address, null=True, blank=True)
    headquarters_phone = PhoneNumberField(null=True, blank=True)
    headquarters_fax = PhoneNumberField(null=True, blank=True)
    department_type = models.CharField(max_length=20, choices=DEPARTMENT_TYPE_CHOICES, null=True, blank=True)
    organization_type = models.CharField(max_length=75, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    state = models.CharField(max_length=2)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, validators=[validate_choice(REGION_CHOICES)], null=True, blank=True)
    geom = models.MultiPolygonField(null=True, blank=True)
    objects = models.GeoManager()
    priority_departments = PriorityDepartmentsManager()
    dist_model_score = models.FloatField(null=True, blank=True, editable=False)
    government_unit = RelatedObjectsDescriptor()
    population = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('state', 'name')

    @property
    def government_unit_objects(self):
        """
        Memoize the government_unit generic key lookup.
        """
        if not getattr(self, '_government_unit_objects', None):
            self._government_unit_objects = self.government_unit.all().generic_objects()

        return self._government_unit_objects

    @property
    def fips(self):
        objs = self.government_unit_objects

        if objs:
            return [obj.fips for obj in objs if hasattr(obj, 'fips')]

        return []

    @property
    def geom_area(self):
        """
        Project the department's geometry into north america lambert conformal conic
        Returns km2
        """
        if self.geom:
            try:
                return self.geom.transform(102009, clone=True).area / 1000000
            except:
                return

    @property
    def similar_departments(self, ignore_regions_min=1000000):
        """
        Identifies similar departments based on the protected population size and region.
        """

        params = {}

        if self.population >= 250000:
            params['population__gte'] = 250000

        elif self.population < 2500:
            params['population__lt'] = 2500

        else:
            community_sizes = [
                (100000, 249999),
                (50000, 99999),
                (25000, 49999),
                (10000, 24999),
                (5000, 9999),
                (2500, 4999)]

            for lower_bound, upper_bound in community_sizes:
                if lower_bound <= self.population <= upper_bound:
                    params['population__lte'] = upper_bound
                    params['population__gte'] = lower_bound

                break

        similar = FireDepartment.objects.filter(**params)\
            .exclude(id=self.id)\
            .extra(select={'difference': "abs(population - %s)"}, select_params=[self.population])\
            .extra(order_by=['difference'])

        # Large departments may not have similar departments in their region.
        if self.population < ignore_regions_min:
            similar = similar.filter(region=self.region)

        return similar

    def set_geometry_from_government_unit(self):
        objs = self.government_unit_objects

        if objs:
            self.geom = MultiPolygon([obj.geom for obj in objs if getattr(obj, 'geom', None)])
            self.save()

    def set_population_from_government_unit(self):
        """
        Stores the population of government units on the FD object to speed up querying.
        """
        objs = self.government_unit_objects

        if objs:
            self.population = 0

            for gov_unit in objs:
                pop = getattr(gov_unit, 'population', None)

                if pop is not None:
                    self.population += pop

            self.save()

    def set_region(self, region):
        validate_choice(FireDepartment.REGION_CHOICES)(region)
        self.region = region
        self.save()

    def residential_structure_fire_counts(self):
        return self.nfirsstatistic_set.filter(metric='residential_structure_fires')

    @classmethod
    def load_from_usfa_csv(cls):
        """
        Loads Fire Departments from http://apps.usfa.fema.gov/census-download.
        """
        us, _ = Country.objects.get_or_create(name='United States of America', iso_code='US')

        with open(os.path.join(os.path.dirname(__file__), 'scripts/usfa-census-national.csv'), 'r') as csvfile:

            # This only runs once, since there isn't a good key to identify duplicates
            if not cls.objects.all().count():
                reader = csv.DictReader(csvfile)
                counter = 0
                for row in reader:
                    # only run once.
                    hq_address_params = {}
                    hq_address_params['address_line1'] = row.get('HQ Addr1')
                    hq_address_params['address_line2'] = row.get('HQ Addr2')
                    hq_address_params['city'] = row.get('HQ City')
                    hq_address_params['state_province'] = row.get('HQ State')
                    hq_address_params['postal_code'] = row.get('HQ Zip')
                    hq_address_params['country'] = us
                    headquarters_address, _ = Address.objects.get_or_create(**hq_address_params)
                    headquarters_address.save()

                    mail_address_params = {}
                    mail_address_params['address_line1'] = row.get('Mail Addr1')
                    mail_address_params['address_line2'] = row.get('Mail Addr2') or row.get('Mail PO Box')
                    mail_address_params['city'] = row.get('Mail City')
                    mail_address_params['state_province'] = row.get('Mail State')
                    mail_address_params['postal_code'] = row.get('Mail Zip')
                    mail_address_params['country'] = us
                    mail_address, _ = Address.objects.get_or_create(**mail_address_params)
                    mail_address.save()

                    params = {}
                    params['fdid'] = row.get('FDID')
                    params['name'] = row.get('Fire Dept Name')
                    params['headquarters_phone'] = row.get('HQ Phone')
                    params['headquarters_fax'] = row.get('HQ Fax')
                    params['department_type'] = row.get('Dept Type')
                    params['organization_type'] = row.get('Organization Type')
                    params['website'] = row.get('Website')
                    params['headquarters_address'] = headquarters_address
                    params['mail_address'] = mail_address
                    params['state'] = row.get('HQ State')

                    cls.objects.create(**params)
                    counter += 1

                assert counter == cls.objects.all().count()

    def get_absolute_url(self):
        return reverse('firedepartment_detail', kwargs=dict(pk=self.id))

    def find_jurisdiction(self):
        from geoshape.usgs.models import CountyorEquivalent, IncorporatedPlace, UnincorporatedPlace

        counties = CountyorEquivalent.objects.filter(state_name='Virginia')
        for county in counties:
            incorporated = IncorporatedPlace.objects.filter(geom__intersects=county.geom)
            unincoporated = UnincorporatedPlace.objects.filter(geom__intersects=county.geom)
            station = FireStation.objects.filter(geom__intersects=county.geom)

            print 'County', county.name
            print 'Incorporated Place', incorporated.count()
            print 'Unincorporated Place', unincoporated.count()
            print 'Stations:', station

    def __unicode__(self):
        return self.name


class FireStation(USGSStructureData):
    """
    Fire Stations.
    """
    service_id = 7

    fdid = models.CharField(max_length=10, null=True, blank=True)
    department = models.ForeignKey(FireDepartment, null=True, blank=True, on_delete=models.SET_NULL)
    station_number = models.IntegerField(null=True, blank=True)
    station_address = models.ForeignKey(Address, null=True, blank=True)
    district = models.MultiPolygonField(null=True, blank=True)
    objects = models.GeoManager()

    @classmethod
    def populate_address(cls):

        us, _ = Country.objects.get_or_create(iso_code='US')
        for obj in cls.objects.filter(station_address__isnull=True, address__isnull=False, zipcode__isnull=False):
            try:
                addr, _ = Address.objects.get_or_create(address_line1=obj.address, city=obj.city,
                                                        state_province=obj.state, postal_code=obj.zipcode,
                                                        country=us, defaults=dict(geom=obj.geom))
            except Address.MultipleObjectsReturned:
                objs = Address.objects.filter(address_line1=obj.address, city=obj.city, state_province=obj.state, postal_code=obj.zipcode,
                                                        country=us)
                import ipdb; ipdb.set_trace()
            obj.station_address = addr
            obj.save()
    @property
    def origin_uri(self):
        """
        This object's URI (from the national map).
        """
        return 'http://services.nationalmap.gov/arcgis/rest/services/structures/MapServer/7/{0}?f=json' \
            .format(self.objectid)

    @classmethod
    def load_data(cls):
        objects = requests.get('http://services.nationalmap.gov/arcgis/rest/services/structures/MapServer/7/query?'
                               'where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&'
                               'spatialRel=esriSpatialRelIntersects&relationParam=&outFields=&returnGeometry=true&'
                               'maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=true&returnCountOnly=false&'
                               'orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&'
                               'gdbVersion=&returnDistinctValues=false&f=json')

        current_ids = set(FireStation.objects.all().values_list('objectid', flat=True))
        object_ids = set(json.loads(objects.content)['objectIds']) - current_ids
        url = 'http://services.nationalmap.gov/arcgis/rest/services/structures/MapServer/7/{0}?f=json'
        us, _ = Country.objects.get_or_create(iso_code='US')

        for object in object_ids:
            try:

                if FireStation.objects.filter(objectid=object):
                    continue

                obj = requests.get(url.format(object))
                obj = json.loads(obj.content)
                data = dict((k.lower(), v) for k, v in obj['feature']['attributes'].iteritems())

                if obj['feature'].get('geometry'):
                    data['geom'] = Point(obj['feature']['geometry']['x'], obj['feature']['geometry']['y'])

                data['loaddate'] = datetime.datetime.fromtimestamp(data['loaddate']/1000.0)
                feat = cls.objects.create(**data)
                feat.save()
                print 'Saved object: {0}'.format(data.get('name'))
                print '{0} Firestations loaded.'.format(FireStation.objects.all().count())

            except KeyError:
                print '{0} failed.'.format(object)
                print url.format(object)

            except IntegrityError:
                print '{0} failed.'.format(object)
                print url.format(object)
                print sys.exc_info()

                try:
                    rollback()
                except:
                    pass

            except:
                print '{0} failed.'.format(object)
                print url.format(object)
                print sys.exc_info()

    @property
    def district_area(self):
        """
        Project the district's geometry into north america lambert conformal conic
        Returns km2
        """
        if self.district:
            try:
                return self.district.transform(102009, clone=True).area / 1000000
            except:
                return

    def get_absolute_url(self):
        return reverse('firestation_detail', kwargs=dict(pk=self.id))

    class Meta:
        verbose_name = 'Fire Station'


class Staffing(models.Model):
    """
    Models response capabilities (apparatus and responders).
    """
    APPARATUS_CHOICES = [('Engine', 'Engine'),
                         ('Ladder/Truck/Aerial', 'Ladder/Truck/Aerial'),
                         ('Quint', 'Quint'),
                         ('Ambulance/ALS', 'Ambulance/ALS'),
                         ('Ambulance/BLS', 'Ambulance/BLS'),
                         ('Heavy Rescue', 'Heavy Rescue'),
                         ('Boat', 'Boat'),
                         ('Hazmat', 'Hazmat'),
                         ('Chief', 'Chief'),
                         ('Other', 'Other')]

    int_field_defaults = dict(null=True, blank=True, max_length=2, default=0, validators=[MaxValueValidator(99)])

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    firestation = models.ForeignKey(FireStation)
    apparatus = models.CharField(choices=APPARATUS_CHOICES, max_length=20, default='Engine')
    firefighter = models.PositiveIntegerField(**int_field_defaults)
    firefighter_emt = models.PositiveIntegerField(verbose_name='Firefighter EMT', **int_field_defaults)
    firefighter_paramedic = models.PositiveIntegerField(verbose_name='Firefighter Paramedic', **int_field_defaults)
    ems_emt = models.PositiveIntegerField(verbose_name='EMS-Only EMT', **int_field_defaults)
    ems_paramedic = models.PositiveIntegerField(verbose_name='EMS-Only Paramedic', **int_field_defaults)
    officer = models.PositiveIntegerField(verbose_name='Company/Unit Officer', **int_field_defaults)
    officer_paramedic = models.PositiveIntegerField(verbose_name='Company/Unit Officer Paramedic', **int_field_defaults)
    ems_supervisor = models.PositiveIntegerField(verbose_name='EMS Supervisor', **int_field_defaults)
    chief_officer = models.PositiveIntegerField(verbose_name='Cheif Officer', **int_field_defaults)

    def __unicode__(self):
        return '{0} response capability for {1}'.format(self.apparatus, self.firestation)

    class Meta:
        verbose_name_plural = 'Response Capabilities'


class NFIRSStatistic(models.Model):
    """
    Caches NFIRS stats.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    fire_department = models.ForeignKey(FireDepartment)
    metric = models.CharField(max_length=50, db_index=True)
    year = models.PositiveSmallIntegerField(db_index=True)
    count = models.PositiveSmallIntegerField(db_index=True)

    class Meta:
        unique_together = ['fire_department', 'year', 'metric']
        ordering = ['-year',]
