# PyUssd
USSD Implemented in Python 


#Deployment

Run:  gunicorn -c PyUssd/config_gunicorn.py PyUssd.wsgi:application
      
#Setup

  1. If menu id is 0, it is treated as prompt and its id is not displayed.
  2. As  for messages, always reply with CON or END.


#Request and Reponse

1.Sample Request to client:

  {'operator_session_id':"123455",'msisdn':"254700",
                      'ussd_input':"2",
                      "info":{}, #this is as from client. we return as per request
                      "client_session":{} #this is from  client session. we return as per request
  }

        
        
2. Sample Required Response from client : 
  . id is needed for ordering. display is made in order of id ASC.

  {"menus":[{"id":1,choice":"1","name":"Manchester Vs Arsenal","info":{"game_id":"12345"}},
                              {"id":2,choice":"2","name":"Chelsea Vs Magma","info":{}},
                              {"id":3,choice":"3","name":"Orlando Vs Kelio","info":{}},
                             ],
                    "message":"CON Next 5 Games",
                    "client_session":{},
                    "url":"http://127.0.0.1:9000/footballFixture"
  }

