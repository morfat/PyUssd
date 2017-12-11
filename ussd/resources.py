import falcon
import requests
import pickle
import operator

import copy

            
class UssdResource:
    MAX_SCREEN_CHARS=90-30 #Maximu screen dispplay in chars.. 30 chars   #for navigation of 97,98 and 99.


    def get_display_screen(self,req,ussd_input,session):
        #for when user enters 97,98 or 99

        
        
        screen=''
        b_n_h_controls='\n97: Back \n98: Next \n99: Home'
        b_h_controls='\n97: Back \n99: Home'
        n_controls='\n98: Next'


        if (ussd_input=='99' or ussd_input is None) and session:
            #this says go to home. check if at home or not.
            response_data_list=session.get("response_data_list")
            response_data=response_data_list[0]
            screen=response_data.get("screen_1")
            screens=response_data.get("screens")
            if screens>1:
                #we add navigation for next.
                screen+=n_controls

            response_data.update({"current_screen":1})

            response_data_list=[response_data]
            session.update({"response_data_list":response_data_list})

        elif ussd_input=='98':
            #this means navigational next
            #get current screen
            response_data_list=session.get("response_data_list")
            response_data=response_data_list.pop()
            screens=response_data.get("screens")
            current_screen=response_data.get("current_screen")
            if current_screen<screens:
                current_screen=current_screen+1
                screen=response_data.get("screen_%s"%(current_screen))
                #check if this is last screen
                if not current_screen==screens:
                    screen+=b_n_h_controls
                else:
                    screen+=b_h_controls
            
            response_data.update({"current_screen":current_screen})
            response_data_list.append(response_data)
            session.update({"response_data_list":response_data_list})

        elif ussd_input=='97':
            #this means previous/back. it can be back in screens or back in whole menulist.
            response_data_list=session.get("response_data_list")
            response_data=response_data_list.pop()
            screens=response_data.get("screens")
            current_screen=response_data.get("current_screen")
            if screens==1:
                #this is normal , back. we move one step backwards.
                #we pop another
                response_data=response_data_list.pop()
                screens=response_data.get("screens")
                current_screen=response_data.get("current_screen")
                screen=response_data.get("screen_1")

                response_data.update({"current_screen":1})
                if screens>1:
                    #we add navigation for next.
                    if len(response_data_list)==0:
                        #this was homepage
                        screen+=n_controls
                        response_data_list=[response_data]
                    else:
                        screen+=b_n_h_controls
                        response_data_list.append(response_data)
                else:
                    #this one has just one screen
                    #chec if it is home page
                    if len(response_data_list)>0:
                        #not homegae. so we add back and home only
                        screen+=b_h_controls
                        response_data_list.append(response_data)
                    else:
                        response_data_list=[response_data]
            else:
                #we are in same paginated. just moving back one step.
                current_screen=current_screen-1
                if current_screen==0:
                    #move to previous page
                    current_screen=1
                    response_data=response_data_list[-1]


                response_data.update({"current_screen":current_screen})
                screen=response_data.get("screen_%s"%(current_screen))
                if current_screen==1:
                    #we moved to initial. check if there is other menus back.
                    if len(response_data_list)>1:
                        screen+=b_n_h_controls
                    else:
                        screen+=n_controls
                else:
                    screen+=b_n_h_controls
                response_data_list.append(response_data)

            session.update({"response_data_list":response_data_list})

        else:
            session,screen=self.get_menu_display_screen(req,ussd_input,session)

        return (session,screen,)

    def get_menu_display_screen(self,req,ussd_input=None,session=None):
        #default request data
        request_data={'operator_session_id':req.params.get('session_id'),'msisdn':req.params.get('msisdn'),
                      'ussd_input':ussd_input,
                      "info":{}, #this is as from client. we return as per request
                      "client_session":{} #this is from  client session. we return as per request
                      }

        
        screen=''
        b_n_h_controls='\n97: Back \n98: Next \n99: Home'
        b_h_controls='\n97: Back \n99: Home'
        n_controls='\n98: Next'

        if not session or not ussd_input:
            #new request, lets call external API.
            response_data=self.call_client_url(url=self.service_endpoint,data=request_data)

            #paginate response to create sample 

            paginated_data=self.paginate_client_response(response_data)
            session={"operator_session_id":req.params.get('session_id'), "response_data_list":[paginated_data]}
            #display
            screens=paginated_data.get("screens")
            screen=paginated_data.get("screen_1")
            if screens>1:
                screen+=n_controls
        else:
            #check if input is valid
            response_data_list=session.get("response_data_list")
            response_data=response_data_list[-1]
            url=response_data.get("url")

            screen=response_data.get("screen_1")
           
            menus=response_data.get("menus")
            menu_d={}
            for m in menus:
                if m.get("choice")==ussd_input:
                    menu_d=m
                    break
            
            #check if menu found.
            if menu_d:
                #call external url on the given data
                request_data.update({"client_session":response_data.get("client_session"),"info":menu_d.get("info")})
                response_data=self.call_client_url(url=url,data=request_data)

                #paginated

                response_data=self.paginate_client_response(response_data)
                response_data_list.append(response_data)
                session.update({"response_data_list":response_data_list})
                #generate displa
                screens=response_data.get("screens")
                screen=response_data.get("screen_1")
                if screens>1:
                    screen+=b_n_h_controls
                else:
                    screen+=b_h_controls

            else:
                #display invalid choice
                screen="Invalid Choice !"+screen

        return (session,screen,)
            

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

    def paginate_client_response(self,response_data):
        #@TODO implement ordering for response .. here before modifying
        menus=response_data.get("menus")
        menus.sort(key=operator.itemgetter("id")) #sort menus by id
        message=response_data.get("message")

        message_len=len(message) #message is applied on first menu only
        

        screens=1

        new_response_data=copy.deepcopy(response_data)
        new_response_data.update({"screens":1,"current_screen":1})

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
        
       
        return new_response_data



    def on_get(self,req,resp):

        """
        Sample Request to client:

          {'operator_session_id':"123455",'msisdn':"254700",
                      'ussd_input':"2",
                      "info":{}, #this is as from client. we return as per request
                      "client_session":{} #this is from  client session. we return as per request
          }
        
        
         Sample Required Response from client : 
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
        #session={"response_data_list":[]}

        session=self.redis.get(self.service_session_key)
        
        if session:
            session_p=pickle.loads(session)
        else:
            session_p=None

        session_d,screen=self.get_display_screen(req,ussd_input,session_p)

        #update session
        self.redis.set(self.service_session_key,pickle.dumps(session_d))

        resp.body=screen
        
    
       



        
