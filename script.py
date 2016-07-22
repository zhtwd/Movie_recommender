from server import app
import unittest
import json

class FlaskServerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass 

    @classmethod
    def tearDownClass(cls):
        pass 

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        self.app.testing = True 

    def tearDown(self):
        pass 

    def test_home_status_code(self):
        result = self.app.get('/') 
        self.assertEqual(result.status_code, 200) 
    
    def test_post_follow(self):
        with open('follows.json') as test_file:
            test_cases = json.load(test_file)
            for operation in test_cases[u'operations']:
                rv = self.app.post('/follow', data=json.dumps({
                    'from': operation[0],
                    'to': operation[1]
                    }), content_type = 'application/json')
                self.assertEqual(rv.status_code, 200)

    def test_post_watch(self):
        with open('watch.json') as test_file:
            test_cases = json.load(test_file)
            for user in test_cases['userIds']:
                for movie in test_cases['userIds'][user]:
                    rv = self.app.post('/watch', data=json.dumps({
                        'user': user,
                        'movie': movie
                        }), content_type = 'application/json')
                    self.assertEqual(rv.status_code, 200)

    def test_get_recommendation(self):
        with open('follows.json') as test_file:
            test_cases = json.load(test_file)
            for operation in test_cases[u'operations']:
                rv = self.app.post('/follow', data=json.dumps({
                    'from': operation[0],
                    'to': operation[1]
                    }), content_type = 'application/json')
        with open('watch.json') as test_file:
            test_cases = json.load(test_file)
            for user in test_cases['userIds']:
                for movie in test_cases['userIds'][user]:
                    rv = self.app.post('/watch', data=json.dumps({
                        'user': user,
                        'movie': movie
                        }), content_type = 'application/json')

        rv = self.app.get('/recommendations?user=a')
        print ("Recommendation result for user a is", 
                json.loads(rv.data)['list'])
        self.assertEqual(rv.status_code, 200)


if __name__ == "__main__":
    unittest.main()
