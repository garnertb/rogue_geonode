import functools
import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client, TestCase, LiveServerTestCase
from django.test.utils import override_settings
from geonode.maps.models import Map
from geonode.utils import ogc_server_settings
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.webdriver import WebDriver, FirefoxProfile
from selenium.webdriver.support.wait import WebDriverWait
import time
from urlparse import urlsplit


def login_user(fn):
    """
    A convenience decorator used to login users in test methods.
    """
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        self.login()
        return fn(self, *args, **kwargs)

    return wrapped


class SeleniumTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.profile = FirefoxProfile()
        cls.selenium = WebDriver(cls.profile)
        super(SeleniumTests, cls).setUpClass()

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin'
        self.user, created = User.objects.get_or_create(username=self.username, is_superuser=True)

        if created:
            self.user.set_password(self.password)
            self.user.save()

    def login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/account/login/'))

        WebDriverWait(self.selenium, 20)\
            .until(lambda d: d.find_element_by_xpath("//input[@id='id_username']").is_enabled())

        username_input = self.selenium.find_element_by_css_selector(".controls>#id_username")
        password_input = self.selenium.find_element_by_css_selector(".controls>#id_password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.selenium.find_element_by_css_selector('.form-actions>button').click()

        location = ogc_server_settings.rest.replace('http://', 'http://{0}:{1}@'.format(self.username,
                                                                                        self.password))
        #self.selenium.get(location)
        #location = 'http://{0}:{1}@localhost:8080/geoserver/rest'.format(self.username, self.password)
            #print location
            #import ipdb; ipdb.set_trace()
            #self.selenium.get(location)

    def save_map(self, title, abstract='No Abstract'):
        self.selenium.find_element_by_css_selector('#saveButton').click()

        WebDriverWait(self.selenium, 20).until(
            lambda driver: driver.find_element_by_xpath("//div[@id='saveMap']").is_displayed())

        self.selenium.find_element_by_xpath("//input[@id='mapTitle']").send_keys(title)
        self.selenium.find_element_by_xpath("//textarea[@id='mapAbstract']").send_keys(abstract)
        self.selenium.find_element_by_css_selector('#save-map>.modal-footer>button:nth-of-type(3)').click()

    @login_user
    def test_create_new_map(self):
        """
        Tests creating and saving a new map.
        """

        title = 'Test Map'
        abstract = 'Test Abstract'
        layer_names = ['Incidente', 'Vitales']

        self.selenium.get('%s%s' % (self.live_server_url, reverse('maploom-map-new')))
        WebDriverWait(self.selenium, 20).until(
            lambda driver: driver.find_element_by_tag_name('body'))

        self.selenium.find_element_by_css_selector('#saveButton').click()

        WebDriverWait(self.selenium, 20).until(
            lambda driver: driver.find_element_by_xpath("//div[@id='saveMap']").is_displayed())

        self.save_map(title=title, abstract=abstract)

        # Check the title has updated
        self.assertEqual(self.selenium.find_element_by_css_selector('#map-name>div').text, title)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('maps_browse')))
        WebDriverWait(self.selenium, 20).until(
            lambda driver: driver.find_element_by_tag_name('body'))


        maps = Map.objects.filter(title=title)
        self.assertTrue(len(maps) > 0)
        map = maps[0]
        self.assertEqual(abstract, map.abstract)


        # Add some layers
        #self.selenium.find_element_by_xpath("//div[@tooltip='Add Layer']").click()
        #
        #WebDriverWait(self.selenium, 20).until(
        #    lambda driver: driver.find_element_by_xpath("//div[@id='add-layers']").is_displayed())
        #
        #add_layer_modal = self.selenium.find_element_by_xpath("//div[@id='add-layers']")
        #
        #for layer in layer_names:
        #    add_layer_modal.find_element_by_xpath("//input[@id='layer-filter']").send_keys(layer)
        #    ll = self.selenium.find_element_by_xpath("//ul[@id='layer-list']")
        #    ll.find_element_by_css_selector('.loom-check-button').click()
        #    add_layer_modal.find_element_by_xpath("//button[@translate='add_btn']").click()

    @login_user
    def test_add_remote_server(self):

        remote_server = 'http://geoserver2.rogue.lmnsolutions.com/geoserver/wms'
        layer_names = ['Incidente']
        url = urlsplit(remote_server)

        with self.settings(PROXY_ALLOWED_HOSTS=getattr(settings, 'PROXY_ALLOWED_HOSTS', ()) + (url.hostname,)):

            self.selenium.get('%s%s' % (self.live_server_url, reverse('maploom-map-new')))
            WebDriverWait(self.selenium, 20).until(
                lambda driver: driver.find_element_by_tag_name('body'))

            self.selenium.find_element_by_xpath("//div[@tooltip='Add Layer']").click()

            WebDriverWait(self.selenium, 20).until(
                lambda driver: driver.find_element_by_xpath("//div[@id='add-layers']").is_displayed())


            add_layer_modal = self.selenium.find_element_by_xpath("//div[@id='add-layers']")
            add_layer_modal.find_elements_by_css_selector('.btn')[0].click()
            self.selenium.find_element_by_xpath("//a[@data-target='#add-server-dialog']").click()

            add_server_dialog = self.selenium.find_element_by_xpath("//div[@id='add-server-dialog']")

            WebDriverWait(self.selenium, 20).until(
                lambda driver: driver.find_element_by_xpath("//div[@id='add-server-dialog']").is_displayed())

            add_server_dialog.find_element_by_css_selector('#server-name').send_keys('Remote Server')
            add_server_dialog.find_element_by_xpath("//input[@name='serverurl']").send_keys(remote_server)
            add_server_dialog.find_elements_by_css_selector('.modal-footer>button')[1].click()

            for layer in layer_names:
                add_layer_modal.find_element_by_xpath("//input[@id='layer-filter']").send_keys(layer)
                ll = self.selenium.find_element_by_xpath("//ul[@id='layer-list']")

                WebDriverWait(self.selenium, 20).until(
                    lambda driver: driver.find_element_by_css_selector('.loom-check-button').is_displayed())

                ll.find_element_by_css_selector('.loom-check-button').click()
                add_layer_modal.find_element_by_xpath("//button[@translate='add_btn']").click()

            #WebDriverWait(self.selenium, 20).until(
            #    lambda driver: driver.find_element_by_css_selector('#saveButton').is_displayed())

            #self.save_map('Remote Services', 'Map with remote services.')


    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()