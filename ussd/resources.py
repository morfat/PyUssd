import falcon
import requests
import pickle
import operator


def display_response(response,choice_error_message=None,response_data_len=None):
  

    controls="\n00: Home \n0: Previous"
    
    display=response.get("message")
    if choice_error_message:
        display="CON "+choice_error_message
    
    for m in response.get('menus'):
       

        if m.get('id')=='0':
            display+='\n'+"%s"%(m.get('label'))
        else:
            display+='\n'+"%s: %s"%(m.get('id'),m.get('label'))

    if response_data_len==1:
        display='\n'+display
    else:
        display='\n'+display+controls
    return display


def make_http_request(url,params,session):
    response_data_list=None
    request=requests.post(url=url,json=params) #call external
    response=request.json()
    
    if session:
        response_data_list=session.get('response_data_list')
        response_data_list.append(response)
        session.update({"session_id":params.get('session_id'),"response_data_list":response_data_list})
    else:
        response_data_list=[response]
        session={"session_id":params.get('session_id'),"response_data_list":response_data_list}
    return (session,response,)

                

class UssdResource:
    MAX_SCREEN_CHARS=90-30 #Maximu screen dispplay in chars.. 30 chars   #for navigation of 97,98 and 99.

    def call_client_url(self,url,data):
        response=requests.post(url=url,json=data)
        return response.json()


    def get_ussd_input(self,operator_ussd_string):
        ussd_input=None
        if operator_ussd_string:
            ussd_input_list=str(operator_ussd_string).split('*')
            #if this ussd has subcode
            if len(ussd_input_list)==1:
                if not self.service_sub_code:
                    ussd_input=ussd_input_list[0]
            elif len(ussd_input_list)>1:
                ussd_input=ussd_input_list[-1]
        return ussd_input

    def paginate_client_response(self,response_data,ussd_input):
        #@TODO implement ordering for response .. here before modifying
        menus=response_data.get("menus")
        menus.sort(key=operator.itemgetter("id")) #sort menus by id
        message=response_data.get("message")

        message_len=len(message) #message is applied on first menu only
        

        screens=1
        new_response_data={"menus":response_data.get("menus"),"screens":1,"url":response_data.get("url"),
                          "client_session":response_data.get("client_session"),"current_screen":1}


        available_chars=self.MAX_SCREEN_CHARS-message_len
        
       
        screen=''
        for m in menus:
            menu=''
            
            if m.get('choice')=='0':
               menu="\n%s"%(m.get('name'))
            else:
                menu="\n%s: %s"%(m.get('choice'),m.get('name'))

            #check menu length
            available_chars=available_chars-len(menu)
            if available_chars>0:
                if len(screen)==0:
                    #inital screen . add heading
                    screen+=message+menu
                else:
                    screen+=menu
            else:
                #we need newer page
                screen=menu
                available_chars=self.MAX_SCREEN_CHARS-message_len
                screens=screens+1
            
            new_response_data.update({"screen_%s"%(screens):screen,"screens":screens})
        
        print (new_response_data)

        return new_response_data



    def on_get(self,req,resp):
        """ Sample Required Response from client : 
          #id is needed for ordering. display is made in order of id ASC.

                    {"menus":[{"id":1,choice":"1","name":"Manchester Vs Arsenal","info":{"game_id":"12345"}},
                              {"id":2,choice":"2","name":"Chelsea Vs Magma","info":{}},
                              {"id":3,choice":"3","name":"Orlando Vs Kelio","info":{}},
                             ],
                    "message":"CON Next 5 Games",
                    "client_session":{},
                    "url":"http://127.0.0.1:9000/footballFixture"
                     }

        """
        #we can access self.redis,self.service_endpoint,self.service_session_key,self.service_sub_code in this class

        #get input
        ussd_input=self.get_ussd_input(req.params.get('ussd_string'))
        #print (ussd_input)
        
        #get session object
        session=self.redis.get(self.service_session_key)

        #default request data
        request_data={'operator_session_id':req.params.get('session_id'),'msisdn':req.params.get('msisdn'),
                      'ussd_input':ussd_input,
                      "info":{}, #this is as from client. we return as per request
                      "client_session":{} #this is from  client session. we return as per request
                      }

        if not session:
            #new request, lets call external API.
            response_data=self.call_client_url(url=self.service_endpoint,data=request_data)

            #paginate response to create sample 

            paginated_data=self.paginate_client_response(response_data,ussd_input)
           

            resp.media=paginated_data







                
        """

        #get session info
        session=self.redis.get(self.service_session_key)
       
        #sample request to client API
        request_data={'operator_session_id':session_id,
                      'msisdn':msisdn,
                      'choice':ussd_choice,
                      "info":{},
                      "client_session":{},
                      }
    
        #sample response from client API
        
        display=None

        if session:
            p_session=pickle.loads(session)
            choice=request_data.get('choice')
            response_data_list=p_session.get('response_data_list')

            if choice=='0':
                #previous
                response=response_data_list[-2] #get previous
                response_data_list=response_data_list[:-1]
                p_session.update({"session_id":session_id,"response_data_list":response_data_list})
                resp.body=display_response(response,response_data_len=len(response_data_list))
            elif choice=='00':
                response=response_data_list[0] #get initial display
                response_data_list=[response]
                p_session.update({"session_id":session_id,"response_data_list":response_data_list})
                resp.body=display_response(response,response_data_len=len(response_data_list))
            else:
                #print (response_data_list)

                prev_response=response_data_list[-1] #get last element. do not use pop here
                #get the link
                #print (prev_response)

                prev_menus=prev_response.get("menus")

                menu_d=None
            
                for menu in prev_menus:
                    print (choice,menu.get('id'))
                    if choice==menu.get('id'):
                        #call external with this
                        menu_d=menu
                        break
                
                #call if available
                if not menu_d:
                    #no choice made
                    resp.body=display_response(prev_response,choice_error_message="Incorrect Input")
                else:
                    url=prev_response.get("url",endpoint_url)
                    client_session=prev_response.get('client_session')
                    info=menu_d.get("info")
                    request_data.update({"info":info,"client_session":client_session})

                    p_session,response=make_http_request(url,request_data,p_session)
                    resp.body=display_response(response)
        else:
            url=endpoint_url
            p_session,response=make_http_request(url,request_data,None)
            #assign for display
            resp.body=display_response(response,response_data_len=0)

        """

        #update or se session
        #self.redis.set(self.service_session_key,pickle.dumps(p_session))
        
    
       



        
