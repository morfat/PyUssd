# PyUssd
USSD Implemented in Python 


#Deployment

Run:  gunicorn -c PyUssd/config_gunicorn.py PyUssd.wsgi:application
      
#Setup

  1. If menu id is 0, it is treated as prompt and its id is not displayed.
  2. As  for messages, always reply with CON or END.

a). Normal 

     {"menus":[{"id":"1","label":"Jacpot Bets","url":"http://127.0.0.1:9000/ussd/jackpot"},
                {"id":"2","label":"Football","url":"http://127.0.0.1:9000/ussd/football"},
                {"id":"3","label":"Other Sports","url":"http://127.0.0.1:9000/ussd/other-sports"}
                ],
      "message":"CON Welcome to Betting"
     }

b). Prompt
    
    {"menus":[{"id":"0","label":"Enter First Name","url":"http://127.0.0.1:9000/ussd/jackpot"},
                ],
      "message":"CON "
    }

c). Message:

     {"menus":[],
      "message":"END Thank you for registering"
     }

d). Confirmation example:
   
   {"menus":[{"id":"0","label":"Are you sure to register ?","url":"http://127.0.0.1:9000/ussd/jackpot"},
             {"id":"1","label":"Yes","url":"http://127.0.0.1:9000/ussd/football"},
             {"id":"2","label":"Cancel","url":"http://127.0.0.1:9000/ussd/other-sports"}
                ],
      "message":"CON "
    }
