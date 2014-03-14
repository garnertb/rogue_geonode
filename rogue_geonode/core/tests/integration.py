import functools
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client, TestCase, LiveServerTestCase
from geonode.maps.models import Map
from geonode.utils import ogc_server_settings
from selenium.webdriver.firefox.webdriver import WebDriver, FirefoxProfile
from selenium.webdriver.support.wait import WebDriverWait
import time


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
        #cls.profile.set_preference("security.fileuri.strict_origin_policy", False)
        cls.selenium = WebDriver(cls.profile)
        super(SeleniumTests, cls).setUpClass()
        cls.username = 'admin'
        cls.password = 'admin'
        cls.user, created = User.objects.get_or_create(username=cls.username, is_superuser=True)

        if created:
            cls.user.set_password(cls.password)
            cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()

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

        self.selenium.find_element_by_xpath("//input[@id='mapTitle']").send_keys(title)
        self.selenium.find_element_by_xpath("//textarea[@id='mapAbstract']").send_keys(abstract)
        self.selenium.find_element_by_css_selector('#save-map>.modal-footer>button:nth-of-type(3)').click()

        # Check the title has updated
        self.assertEqual(self.selenium.find_element_by_css_selector('#map-name>div').text, title)

        #import ipdb; ipdb.set_trace()
        maps = Map.objects.filter(title=title)
        time.sleep(2)  # Race condition here.
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
