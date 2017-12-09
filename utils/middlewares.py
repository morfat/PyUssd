
import falcon
import redis as R



class USSDMiddleWare:
    """ This is the USSD middleware """

    def __init__(self,):
        self._redis=R.StrictRedis(host="localhost", port=6379)
        self.msisdn=None
       

        

       
    def process_request(self,req,resp):
        #default params are msisdn,service_code,session_id,ussd_string
        self.msisdn=req.params.get('msisdn')
        
        
    def process_resource(self,req,resp,resource,params):
        resource.redis=self._redis
        resource.msisdn=self.msisdn
        session=self._redis.hgetall(self.msisdn)
        if not session:
            session={}
        resource.session=session



    def process_response(self,req,resp,resource,req_succeeded): #called immediately before the response is returned.
        self._redis.hmset(self.msisdn,resource.session)
        self._redis.expire(self.msisdn,300) #expire after  seconds



    
