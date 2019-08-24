from groupbuyorganizer import web_app
from groupbuyorganizer.events.models import *
from groupbuyorganizer.admin.models import *



if __name__ == '__main__':

    # web_app.run(debug=True)
    web_app.run(debug=True, host='0.0.0.0', port='80') #todo change at release