
import falcon
import redis as R
from PyUssd.settings import USSD 


class USSDMiddleWare:
    """ This is the USSD middleware """

    def __init__(self,):
        self._redis=R.StrictRedis(host="localhost", port=6379)
        self.service_code=USSD.get('code')
        self.service_sub_code=USSD.get('sub_code')
        self.service_endpoint=USSD.get('endpoint') 
        self.service_session_key=None
    
    def process_request(self,req,resp):
        #default params are msisdn,service_code,session_id,ussd_string
        self.service_session_key=str(self.service_code)+str(self.service_sub_code)+req.params.get('msisdn')

    def process_resource(self,req,resp,resource,params):
        resource.redis=self._redis
        resource.service_endpoint=self.service_endpoint
        resource.service_session_key=self.service_session_key
        resource.service_sub_code=self.service_sub_code




    def process_response(self,req,resp,resource,req_succeeded): #called immediately before the response is returned.
        #self._redis.hmset(self.msisdn,resource.session)
        #self._redis.expire(self.msisdn,300) #expire after  seconds
        pass




    
