from django.test import TestCase
from django.test import TestCase
from sign.models import Event,Guest
from django.contrib.auth.models import User
from sign.models import Event,Guest

# Create your tests here

class ModelTest(TestCase):
    def setUp(self):
        Event.objects.create(id=1,name='qilin1020',limit=2000,status=True,address='hanzhou',start_time='2018-07-17 17:35:00')
        Guest.objects.create(id=1,event_id=1,realname='dog',phone='18202736877',email='dog@mail.com',sign=False)

    def test_models_event(self):
        result = Event.objects.get(name='qilin1020')
        self.assertEqual(result.address,'hanzhou')
        self.assertTrue(result.status)

    def test_models_guest(self):
        result = Guest.objects.get(phone='18202736877')
        self.assertEqual(result.realname,'dog')
        self.assertFalse(result.sign)

class IndexPageTest(TestCase):

    '''测试登陆页'''
    def test_index_page_renders_index_template(self):
        response = self.client.get('/index/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'index.html')

class LoginActionTest(TestCase):
    '''测试登陆行为'''
    def setUp(self):
        User.objects.create_user('admin','admin@mail.com','admin123456')

    def test_add_admin(self):
        '''测试添加用户'''
        response = User.objects.get(username='admin')
        self.assertEqual(response.username,'admin')
        self.assertEqual(response.email,'admin@mail.com')

    def test_login_action_username_password_null(self):
        '''测试用户密码为空'''
        test_data = {'username':'','password':''}
        response = self.client.post('/login_action/',data=test_data)
        self.assertEqual(response.status_code,200)
        self.assertIn(b'username or password error!',response.content)

    def test_login_action_username_password_error(self):
        '''测试用户密码错误'''
        test_data = {'username':'abc','password':'123'}
        response = self.client.post('/login_action/',data=test_data)
        self.assertEqual(response.status_code,200)
        self.assertIn(b'username or password error!',response.content)

    def test_login_action_success(self):
        ''''测试成功登陆'''
        test_data = {'username':'admin','password':'admin123456'}
        response = self.client.post('/login_action/',data=test_data)
        self.assertEqual(response.status_code,302)


class EventManageTest(TestCase):
    '''发布会管理'''
    def setUp(self):
        User.objects.create_user('admin','admin@mail.com','admin123456')
        Event.objects.create(name='ryzen',limit=2000,address='hangzhou',status=1,start_time='2018-07-18 12:20:00')
        self.login_user = {'username':'admin','password':'admin123456'}

    def test_event_manage_success(self):
        '''测试发布会'''
        response = self.client.post('/login_action/',data=self.login_user)
        response = self.client.post('/event_manage/')
        self.assertEqual(response.status_code,200)
        self.assertIn(b'ryzen',response.content)
        self.assertIn(b'hangzhou',response.content)

    def test_event_manage_search_success(self):
        '''测试发布搜索'''
        response = self.client.post('/login_action/',data=self.login_user)
        response = self.client.post('/event_manage/',{'name':'ryzen'})
        self.assertEqual(response.status_code,200)
        self.assertIn(b'ryzen',response.content)
        self.assertIn(b'hangzhou',response.content)

class GuestManageTest(TestCase):
    '''用户管理'''
    def setUp(self):
        User.objects.create_user('admin','admin@mail.com','admin123456')
        Event.objects.create(id=1,name='ryzen', limit=2000, address='hangzhou', status=1, start_time='2018-07-18 12:20:00')
        Guest.objects.create(realname='rx450',phone='18202736877',email='rx450@mail.com',sign=0,event_id=1)
        self.login_user={'username':'admin','password':'admin123456'}
    def test_event_manage_success(self):
        '''测试嘉宾信息'''
        response = self.client.post('/login_action/',data=self.login_user)
        response = self.client.post('/guest_manage/')
        self.assertEqual(response.status_code,200)
        self.assertIn(b'rx450',response.content)
        self.assertIn(b'18202736877',response.content)

    def test_guest_manage_search_success(self):
        '''测试嘉宾搜索'''
        response = self.client.post('/login_action/',data=self.login_user)
        response = self.client.post('/guest_manage/',{'name':'rx450'})
        self.assertEqual(response.status_code,200)
        self.assertIn(b'rx450',response.content)
        self.assertIn(b'18202736877',response.content)

class SignIndexActionTest(TestCase):
    '''测试签到'''
    def setUp(self):
        User.objects.create_user('admin','admin@mail.com','admin123456')
        Event.objects.create(id=1,name='ryzen', limit=2000, address='hangzhou1', status=1, start_time='2018-07-20 12:20:00')
        Event.objects.create(id=2,name='intel', limit=2000, address='hangzhou', status=1, start_time='2018-07-18 12:20:00')
        Guest.objects.create(realname='rx450',phone='18202736877',email='rx450@mail.com',sign=0,event_id=1)
        Guest.objects.create(realname='gtx1060',phone='17805068613',email='gtx1060@mail.com',sign=1,event_id=2)
        self.login_user = {'username':'admin','password':'admin123456'}

    def tests_sign_index_action_phone_null(self):
        '''测试手机号为空'''
        response = self.client.post('/login_action/',data=self.login_user)
        response = self.client.post('/sign_index_action/1/',{'phone':''})
        self.assertEqual(response.status_code,200)
        self.assertIn(b'phone error',response.content)

    def test_sign_index_action_event_id_or_phone_error(self):
        '''测试手机号或发布会id错误'''
        response = self.client.post('/login_action/',data=self.login_user)
        response = self.client.post('/sign_index_action/2/',{'phone':'18202736877'})
        self.assertEqual(response.status_code,200)
        self.assertIn(b'event id or phone error.',response.content)

    def test_sign_index_action_user_has_sign_in(self):
        '''测试用户已经签到'''
        response = self.client.post('/login_action/',data=self.login_user)
        response = self.client.post('/sign_index_action/2/',{'phone':'17805068613'})
        self.assertEqual(response.status_code,200)
        self.assertIn(b'user has sign in',response.content)

    def test_sign_index_action_sign_in_success(self):
        '''测试用户成功签到'''
        response = self.client.post('/login_action/',data=self.login_user)
        response = self.client.post('/sign_index_action/1/',{'phone':'18202736877'})
        self.assertEqual(response.status_code,200)
        self.assertIn(b'sign in success!',response.content)

