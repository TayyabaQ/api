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
            barcode =validation_data.get("delivery_point_barcode","")
            address_metadata = validation_data.get("metadata",{})
            address_analysis = validation_data.get("analysis",{})
            co = validation_data.get("components",{})
            lat = address_metadata.get("latitude","")
            _long = address_metadata.get("longitude","")
            county = address_metadata.get("county_fips","")
            code = address_analysis.get("dpv_match_code","")
            if not barcode:
                barcode = "N/A"
                
            metadata = f"barcode:{barcode}|lat:{lat}|long:{_long}|county:{county}|matchcode:{code}"
        except Exception as e:
                        #print(e)
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

def Remove(duplicate):
    final_list = []
    for num in duplicate:
        if num.strip() not in final_list:
            final_list.append(num.strip())
    return ', '.join(final_list)

def getusaddress(addr):
    address = usaddress.parse(addr)
    m = 0;street = "";city = "";state = "";pcode = ""
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
    return (street, city , state, pcode)

def checknpiid(npiid):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'}
    url = 'https://npiprofile.com/npi/'
    if len(npiid) < 2:
        return json.dumps({'status':'Error'})
    myquery = ''
    npi = "N/A"; provider_name="N/A"; ploc="N/A"; pmail = "N/A"; npientity="N/A"; otherorg = "N/A"; othername="N/A"; taxcode="N/A"; classif="N/A"; phone = "N/A"; fax = "N/A";lastupdated="N/A"
    query=str(npiid)
    page = requests.post(str(url)+query, headers=headers)
    soup = BeautifulSoup(page.text,'html.parser')
    table = soup.find( "table", {"id":"table-npi-provider-information"} )
    if table == None:
        return json.dumps({'status':'Not Found'})
    rows=list()
    for row in table.findAll("tr"):
        rows.append(row)
    for n in range(0,len(rows)):
            n = rows[n].get_text()
            if "NPI" in n and " " not in n:
                    npi = n.replace("NPI","")
            if "Provider Name" in n:
                    provider_name = n.replace("Provider Name", "")
            if "Provider Location Address" in n:
                    ploc = n.replace("Provider Location Address", "")
            if "Provider Mailing Address" in n:
                    pmail = n.replace("Provider Mailing Address", "")
            if "NPI Entity Type" in n:
                    npientity = n.replace("NPI Entity Type", "")
            if "Other Organization Name" in n:
                    otherorg = n.replace("Other Organization Name", "")
            if "Other Name Type" in n:
                    othername = n.replace("Other Name Type", "")
            if "Last Update" in n:
                    lastupdated = n.replace("Last Update Date","")
    table = soup.find( "table", {"id":"table-primary-taxonomy"} )
    rows=list()
    for row in table.findAll("tr"):
        rows.append(row)
    for n in range(0,len(rows)):
            n = rows[n].get_text()
            if "Taxonomy Code" in n:
                taxcode = n.replace("Taxonomy Code","")
            if "Classification" in n:
                classif = n.replace("Classification", "")
    phone = soup.find( "div", {"id":"npi-addresses"} )
    try:
        fax = phone.get_text().split("Phone:")[1].strip().split("\n")[0].split("Fax")[1].strip().replace(":","").strip()
    except:
        fax = "N/A"
    try:
        phone = phone.get_text().split("Phone:")[1].strip().split("\n")[0].split("Fax")[0].strip()
    except:
        phone = "N/A"
    street, city , state, pcode = getusaddress(ploc)
    street1, city1 , state1, pcode1 = getusaddress(pmail)
    try:
        input_data = read_input_values(myquery,street,city,state)
        ploc_barcode= str(smarty_streets_validation(input_data))
        try:
            ploc_barcode = barcode.split('.',1)[0]
        except:
            pass
    except:
        ploc_barcode = "N/A"
    return json.dumps({'status':'Found','Result':{'provider_npi':str(npi),'provider_name':provider_name,'provider_loc_add':ploc,'provider_mail_add':pmail,'npi_entity_type':npientity,
                                                  'other_org_name':otherorg, 'other_name_type':othername, 'taxonomy_code':taxcode, 'classification':classif, 'business_phone': phone,
                                                      'business_fax':fax, 'ploc_barcode':ploc_barcode, 'last_updated':lastupdated}})
