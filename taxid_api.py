from flask import Flask
from flask import request
from waitress import serve
import json, datetime
from searchbytaxid import checktaxid
from searchbyname import checkbarcodeid
app = Flask(__name__)


################################################ Error Handling Messages #################################################  


def errstr(flag):
    
    e = 'Something went really wrong. Sorry for Inconvenience !!!'
        
    return json.dumps({'status':'Error'})

########################################## Routing Functions #############################################################
''' This function do the calculations '''
@app.route("/")
def index():
    return errstr(0)    
     

@app.route("/searchbyname")
def searchbyname():
    try:
        return(checkbarcodeid(str(request.args.get('barcode')),str(request.args.get('name'))))
    except:
        pass
    return json.dumps({'status':'Error'})

@app.route("/searchbytaxid")
def searchbytaxid():
    try:   
        return(checktaxid(str(request.args.get('taxid'))))
    except:
        pass 
    return json.dumps({'status':'Error'})

@app.route("/searchbynpi")
def searchbynpi():
    try:   
        return(checknpiid(str(request.args.get('npiid'))))
    except:
        pass 
    return json.dumps({'status':'Error'})
  
 
###################################################### Main #############################################################
    
''' This is main that invokes the app '''

if __name__ == "__main__":    
    serve(app, host='0.0.0.0', port=5000)
    #app.run(threaded=True, port=5000)
    


