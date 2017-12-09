import falcon

class UssdResource:
    def on_get(self,req,resp):
        response="Test"
        resp.body=response



        
