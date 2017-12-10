#This contains settings for the whole project access


#import other settings

from .local_settings import *

USSD={
    'code':'421',
    'sub_code':'22', #if no subscode, let it be assigned to None
    'endpoint':'http://127.0.0.1:9000/ussd'
}