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
import time

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

def checknpiname(pname, address):
    myresult = []; types=""
    street, city, state, pcode = getusaddress(address)
    queryname = str(pname).replace(" ","%20").replace("'S","").replace("'s","").split("(")[0].strip()
    url = "https://npiprofile.com/search-advanced.php?sNPI=&sEntity_Type_Code=2&sTaxonomy_Code=&sProvider_First_Name=&sProvider_Last_Name_Legal_Name=&sProvider_Business_Name="+queryname+"&sProvider_Address="+street.strip()+"&sProvider_City="+city.strip()+"&sProvider_State="+state.strip()+"&sProvider_Postal_Code=&sProvider_Telephone_Number=&sIsPecos="
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'}
    print(queryname,",", street,",", city, ",",state)
    myquery = ''
    if len(pname) > 2:
        page = requests.post(url, headers=headers)
        soup = BeautifulSoup(page.text,'html.parser')
        divlist = soup.findAll('td',{'data-title':'NPI'})
        types = 1
        if len(divlist) == 0:
            urls = "https://npiprofile.com/search-advanced.php?sNPI=&sEntity_Type_Code=2&sTaxonomy_Code=&sProvider_First_Name=&sProvider_Last_Name_Legal_Name=&sProvider_Business_Name="+queryname+"&sProvider_Address=&sProvider_City="+city.strip()+"&sProvider_State="+state.strip()+"&sProvider_Postal_Code=&sProvider_Telephone_Number=&sIsPecos="
            page = requests.post(urls)
            soup = BeautifulSoup(page.text,'html.parser')
            divlist = soup.findAll('td',{'data-title':'NPI'})
            print(len(divlist))
            types = 2
            if len(divlist) == 0:
                url = "https://npiprofile.com/search-advanced.php?sNPI=&sEntity_Type_Code=2&sTaxonomy_Code=&sProvider_First_Name=&sProvider_Last_Name_Legal_Name=&sProvider_Business_Name="+queryname+"&sProvider_Address=&sProvider_City=&sProvider_State="+state.strip()+"&sProvider_Postal_Code=&sProvider_Telephone_Number=&sIsPecos="
                page = requests.post(url, headers=headers)
                soup = BeautifulSoup(page.text,'html.parser')
                divlist = soup.findAll('td',{'data-title':'NPI'})
                print(len(divlist))
                types = 3
                if len(divlist) == 0:
                    url = "https://npiprofile.com/search-advanced.php?sNPI=&sEntity_Type_Code=2&sTaxonomy_Code=&sProvider_First_Name=&sProvider_Last_Name_Legal_Name=&sProvider_Business_Name="+queryname+"&sProvider_Address=&sProvider_City=&sProvider_State=&sProvider_Postal_Code=&sProvider_Telephone_Number=&sIsPecos="
                    page = requests.post(url, headers=headers)
                    soup = BeautifulSoup(page.text,'html.parser')
                    divlist = soup.findAll('td',{'data-title':'NPI'})
                    print(len(divlist))
                    types = 4
                    if len(divlist) == 0:
                        url = "https://npiprofile.com/search-advanced.php?sNPI=&sEntity_Type_Code=2&sTaxonomy_Code=&sProvider_First_Name=&sProvider_Last_Name_Legal_Name=&sProvider_Business_Name=&sProvider_Address="+street.strip()+"&sProvider_City="+city.strip()+"&sProvider_State="+state.strip()+"&sProvider_Postal_Code=&sProvider_Telephone_Number=&sIsPecos="
                        page = requests.post(url, headers=headers)
                        soup = BeautifulSoup(page.text,'html.parser')
                        divlist = soup.findAll('td',{'data-title':'NPI'})
                        print(len(divlist))
                        types = 5
                        if len(divlist) == 0:
                            return json.dumps({'status':'Not Found'})
    npi = soup.findAll('td',{'data-title':'NPI'})
    name = soup.findAll('td',{'data-title':'Name'})
    typess = [types for n in range(0,len(name))]
    for n in range(0,len(npi)):
        myresult.append({'provider_npi':str(npi[n].get_text()),'provider_name':str(name[n].get_text()),'type':str(typess[n])})
    if len(myresult) > 0:
        return json.dumps({'status':'Found','Result':myresult})
    else:
        return json.dumps({'status':'Not Matched'})
