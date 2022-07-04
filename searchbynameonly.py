import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv,usaddress
import os
import csv
from urllib.request import urlopen
from urllib.parse import urlencode
import pandas as pd
from urllib.request import Request
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv,usaddress
import os
import csv
from urllib.request import urlopen
from urllib.parse import urlencode
import pandas as pd
from urllib.request import Request
import json

def read_input_values(provider_id,street,city,state):
    results = {}
    results[provider_id] = {}
    metadata_type = "mail_address"
    if metadata_type == "mail_address":
        metadata_type = "mailing_address"
        results[provider_id]["metadata_type"] = metadata_type
        results[provider_id]["address_1"] = street
        results[provider_id]["city"] = city
        results[provider_id]["address_state"] = state
        
    return results

def create_address_validation_url(info):
    smarty_streets_auth_id = "0a78cf64-8c40-b69b-fb42-7d1ed41adec2"
    smarty_streets_auth_token = "cppiDIBCvr9XtbMXrSmn"
    base_endpoint = "https://us-street.api.smartystreets.com/street-address"
    address_2 = info.get("address_2")
    if not address_2:
            address_2 = ""
    standard_request_params = {
    "auth-id":smarty_streets_auth_id,
    "auth-token":smarty_streets_auth_token,
    "candidates":1,
    "match":"invalid",
    "street":info.get("address_1","") + " " + address_2,
    "city":info.get("city",None),
    "state":info.get("address_state",None)
    }
    request_params = {key:str(value).strip() for key,value in standard_request_params.items() if value}
    return f"{base_endpoint}?{urlencode(request_params)}"


def make_address_validation_request(info):
    url = create_address_validation_url(info)
    headers = {
    "Content-Type":"application/json",
    "Host":"us-street.api.smartystreets.com"
    }
    timeout = 30
    req = Request(url,None, {"Content-Type":"application/json","Host":"us-street.api.smartystreets.com"})
    r = urlopen(req,timeout=timeout)
    if not str(r.getcode()).startswith("2"):
            raise Exception("Errors were encountered while trying to validate address via SmartyStreets.")
    return json.load(r)[0]

def smarty_streets_validation(input_data):
    results = [];a=[];error=""
    for provider_id,provider_data in input_data.items():
        try:
            validation_data = make_address_validation_request(provider_data)
            address_metadata = validation_data.get("metadata",{})
            address_analysis = validation_data.get("analysis",{})
            co = validation_data.get("components",{})
            barcode =validation_data.get("delivery_point_barcode","")
            lat = address_metadata.get("latitude","")
            _long = address_metadata.get("longitude","")
            county = address_metadata.get("county_fips","")
            code = address_analysis.get("dpv_match_code","")
            if not barcode:
                barcode = "N/A"
            metadata = f"barcode:{barcode}|lat:{lat}|long:{_long}|county:{county}|matchcode:{code}"
                
        except:
                       
            error = 'yes'
        if error=='yes':
            del1="N/A"
            del2="N/A"
            cit="N/A"
            sta="N/A"
            zipc="N/A"
            bar="N/A"
        else:
            del1= validation_data.get('delivery_line_1')
            del2 =validation_data.get('delivery_line_2')
            cit = co.get('city_name')
            sta = co.get('state_abbreviation')
            zipc = co.get('zipcode')
            bar = validation_data.get('delivery_point_barcode')
                
        results.append([provider_id,provider_data["metadata_type"],metadata])
        record = {'delivery_line_1': del1,
                                  'line_2': del2,
                                  'city_name': cit,
                                  'state_abbreviation': sta,
                                  'zipcode': zipc,
                                  'barcode':bar}
        
    return bar




def checkbarcodeid(name):
    myresult = []
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'

           }
    myquery = ''
    url = 'https://eintaxid.com/search-ajax.php'
    
    if len(name) < 2:
        return json.dumps({'status':'Error'})
    
    
    inputstr = name
    if len(inputstr) > 2:
        myquery = str(inputstr)
        myobj = {'query': str(inputstr)}
        page = requests.post(url, data = myobj,headers=headers)
        soup = BeautifulSoup(page.text,'html.parser')
        divlist = soup.findAll('div',{'class':'panel-body'})
      
        if len(divlist) == 0:
            return json.dumps({'status':'Not Found'})
    
   

    
    for div in divlist:
        mycheck = 0
        companylink = 'https://eintaxid.com' + soup.find('a')['href']
        content = div.text.lstrip()
        
        title = content.split('EIN Number',1)[0]
        
        if title.lower().strip() == name.lower().strip():
            mycheck = 1
        einnumber = content.split('EIN Number: ',1)[1].split('Address',1)[0]
        address = content.split('Address: ',1)[1].split('Phone',1)[0]
        phone = content.split('Phone: ',1)[1]
        fulladdress = address
        try:
            zipcode= fulladdress.split(' ')[-1].split('-')[0]
            fulladdress = fulladdress.replace(fulladdress.split(' ')[-1],zipcode)
        except:
            pass
        address = usaddress.parse(address)
        m = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while m < len(address):
            temp = address[m]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            m += 1

        street = street.lstrip().replace(',','')
        city = city.lstrip().replace(',','')
        state = state.lstrip().replace(',','')
        pcode = pcode.lstrip().replace(',','')
        try:
            input_data = read_input_values(myquery,street,city,state)
            barcode= str(smarty_streets_validation(input_data))
           
            try:
                barcode = barcode.split('.',1)[0]
            except:
                pass
        except:
           
            barcode = 'Error'
            
           
        

        
        
        if  mycheck == 1:
            myresult.append({'name':title,'barcode':barcode,'ein_number':str(einnumber),'Address':fulladdress,'phone':phone.strip()})
            
                        
    if len(myresult) > 0:
        #print(result)
        return json.dumps({'status':'Found','Result':myresult})
    else:
        
        return json.dumps({'status':'Not Matched'})


#checkbarcodeid('american bank')


def read_input_values(provider_id,street,city,state):
    results = {}
    results[provider_id] = {}
    metadata_type = "mail_address"
    if metadata_type == "mail_address":
        metadata_type = "mailing_address"
        results[provider_id]["metadata_type"] = metadata_type
        results[provider_id]["address_1"] = street
        results[provider_id]["city"] = city
        results[provider_id]["address_state"] = state
        
    return results

def create_address_validation_url(info):
    smarty_streets_auth_id = "0a78cf64-8c40-b69b-fb42-7d1ed41adec2"
    smarty_streets_auth_token = "cppiDIBCvr9XtbMXrSmn"
    base_endpoint = "https://us-street.api.smartystreets.com/street-address"
    address_2 = info.get("address_2")
    if not address_2:
            address_2 = ""
    standard_request_params = {
    "auth-id":smarty_streets_auth_id,
    "auth-token":smarty_streets_auth_token,
    "candidates":1,
    "match":"invalid",
    "street":info.get("address_1","") + " " + address_2,
    "city":info.get("city",None),
    "state":info.get("address_state",None)
    }
    request_params = {key:str(value).strip() for key,value in standard_request_params.items() if value}
    return f"{base_endpoint}?{urlencode(request_params)}"


def make_address_validation_request(info):
    url = create_address_validation_url(info)
    headers = {
    "Content-Type":"application/json",
    "Host":"us-street.api.smartystreets.com"
    }
    timeout = 30
    req = Request(url,None, {"Content-Type":"application/json","Host":"us-street.api.smartystreets.com"})
    r = urlopen(req,timeout=timeout)
    if not str(r.getcode()).startswith("2"):
            raise Exception("Errors were encountered while trying to validate address via SmartyStreets.")
    return json.load(r)[0]

def smarty_streets_validation(input_data):
    results = [];a=[];error=""
    for provider_id,provider_data in input_data.items():
        try:
            validation_data = make_address_validation_request(provider_data)
            address_metadata = validation_data.get("metadata",{})
            address_analysis = validation_data.get("analysis",{})
            co = validation_data.get("components",{})
            barcode =validation_data.get("delivery_point_barcode","")
            lat = address_metadata.get("latitude","")
            _long = address_metadata.get("longitude","")
            county = address_metadata.get("county_fips","")
            code = address_analysis.get("dpv_match_code","")
            if not barcode:
                barcode = "N/A"
            metadata = f"barcode:{barcode}|lat:{lat}|long:{_long}|county:{county}|matchcode:{code}"
                
        except:
                       
            error = 'yes'
        if error=='yes':
            del1="N/A"
            del2="N/A"
            cit="N/A"
            sta="N/A"
            zipc="N/A"
            bar="N/A"
        else:
            del1= validation_data.get('delivery_line_1')
            del2 =validation_data.get('delivery_line_2')
            cit = co.get('city_name')
            sta = co.get('state_abbreviation')
            zipc = co.get('zipcode')
            bar = validation_data.get('delivery_point_barcode')
                
        results.append([provider_id,provider_data["metadata_type"],metadata])
        record = {'delivery_line_1': del1,
                                  'line_2': del2,
                                  'city_name': cit,
                                  'state_abbreviation': sta,
                                  'zipcode': zipc,
                                  'barcode':bar}
        
    return bar




def checkbarcodeid(name):
    myresult = []
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'

           }
    myquery = ''
    url = 'https://eintaxid.com/search-ajax.php'
    
    if len(name) < 2:
        return json.dumps({'status':'Error'})
    
    
    inputstr = name
    if len(inputstr) > 2:
        myquery = str(inputstr)
        myobj = {'query': str(inputstr)}
        page = requests.post(url, data = myobj,headers=headers)
        soup = BeautifulSoup(page.text,'html.parser')
        divlist = soup.findAll('div',{'class':'panel-body'})
      
        if len(divlist) == 0:
            return json.dumps({'status':'Not Found'})
    
   

    
    for div in divlist:
        mycheck = 0
        companylink = 'https://eintaxid.com' + soup.find('a')['href']
        content = div.text.lstrip()
        
        title = content.split('EIN Number',1)[0]
        if title.lower().strip() == name.lower().strip():
            mycheck = 1
        einnumber = content.split('EIN Number: ',1)[1].split('Address',1)[0]
        address = content.split('Address: ',1)[1].split('Phone',1)[0]
        phone = content.split('Phone: ',1)[1]
        fulladdress = address
        try:
            zipcode= fulladdress.split(' ')[-1].split('-')[0]
            fulladdress = fulladdress.replace(fulladdress.split(' ')[-1],zipcode)
        except:
            pass
        address = usaddress.parse(address)
        m = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while m < len(address):
            temp = address[m]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            m += 1

        street = street.lstrip().replace(',','')
        city = city.lstrip().replace(',','')
        state = state.lstrip().replace(',','')
        pcode = pcode.lstrip().replace(',','')
        try:
            input_data = read_input_values(myquery,street,city,state)
            barcode= str(smarty_streets_validation(input_data))
           
            try:
                barcode = barcode.split('.',1)[0]
            except:
                pass
        except:
           
            return json.dumps({'status':'Error'})
            
           
        

        
        
        if  mycheck == 1:
            myresult.append({'name':title,'barcode':barcode,'ein_number':str(einnumber),'Address':fulladdress,'phone':phone.strip()})
            
                        
    if len(myresult) > 0:
        
        return json.dumps({'status':'Found','Result':myresult})
    else:
        
        return json.dumps({'status':'Not Matched'})


#checkbarcodeid('3M company')

