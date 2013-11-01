import functools
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client, TestCase, LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

class ROGUETests(TestCase):

    def test_jpeg_decoder(self):
        """
        Ensure the jpeg decoder is installed.

        The jpeg decoder (libjpeg) is a django-avatar dependency that can be installed with your operating system's
        package installer.  This test case fails if the decoder is not installed.
        """

        try:
            from PIL.Image import core
            decoder = getattr(core, "jpeg_decoder")
        except IOError:
            self.fail("JPEG Decoder not installed.")
        except ImportError:
            pass


def login_user(fn):
    """
    A convenience decorator used to login users in test methods.
    """
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        self.selenium.get('%s%s' % (self.live_server_url, '/account/login/'))

        WebDriverWait(self.selenium, 20) \
            .until(lambda d: d.find_element_by_xpath("//input[@id='id_username']").is_enabled())

        username_input = self.selenium.find_element_by_css_selector(".controls>#id_username")
        password_input = self.selenium.find_element_by_css_selector(".controls>#id_password")
        print self.username, self.password
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.selenium.find_element_by_css_selector('.form-actions>button').click()
        return fn(self, *args, **kwargs)

    return wrapped


class SeleniumTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
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

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/account/login/'))

        WebDriverWait(self.selenium, 20)\
            .until(lambda d: d.find_element_by_xpath("//input[@id='id_username']").is_enabled())

        username_input = self.selenium.find_element_by_css_selector(".controls>#id_username")
        password_input = self.selenium.find_element_by_css_selector(".controls>#id_password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.selenium.find_element_by_css_selector('.form-actions>button').click()

        #self.assertEqual(self.selenium.current_url[:-1], self.live_server_url)


    def test_create_new_map(self):
        # This isn't quite working yet.
        self.selenium.get('%s%s' % (self.live_server_url, reverse('maploom-map-new')))
        WebDriverWait(self.selenium, 20).until(
            lambda driver: driver.find_element_by_tag_name('body'), timeout=10)

        logger.debug('>>>>>> GEOSERVER {0}'.format(settings.OGC_SERVER['default']['LOCATION']))
        self.selenium.find_element_by_css_selector('#saveMap').click()
        self.selenium.find_element_by_css_selector('#mapTitle').send_keys('Title')
        self.selenium.find_element_by_css_selector('#mapAbstract').send_keys('Abstract')
        self.selenium.find_element_by_css_selector('#save-map>.modal-footer>.btn-primary').click()

