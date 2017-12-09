#This contains the deployable content for the whole project

import falcon

#General
from utils.middlewares import USSDMiddleWare


from ussd.resources import UssdResource


def get_app():
    app=falcon.API(middleware=[USSDMiddleWare()])

    #add routes
    app.add_route('/ussd',UssdResource())
    return app

application=get_app()