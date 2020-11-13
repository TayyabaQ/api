import requests
import pandas as pd
import csv,usaddress


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'

           }
file1 = open('barcodes.txt', 'r')
Lines = file1.readlines()
FILE = 'tax-ids-to-test.csv'
#df = pd.read_excel(FILE)
df = pd.read_csv(FILE)
result = pd.DataFrame(columns=["no",'name'])
start = 0
end = len(df)
check = input("Enter 1 to search with Taxid or 2 to search with name\n")
filename = str(start)+'_'+str(end)+'_' + FILE.split('.',1)[0]+'_SearchbyTaxid.csv'
if check == 2:
    filename = str(start)+'_'+str(end)+'_' + FILE.split('.',1)[0]+'_SearchbyName.csv'
for i in range(start,end):
    #print(str(i),'>>>>>>>>>>>>>>>>...')
    myquery = str(df.at[i,'UUID'])
    if check == '1':
        page =requests.get('https://shumaila.herokuapp.com/searchbytaxid?taxid='+str(df.at[i,'UUID'])).json()
        #page =requests.get('http://127.0.0.1:5000/searchbytaxid?taxid='+str(df.at[i,'UUID'])).json()
    
    elif check == '2':        
        page =requests.get('https://shumaila.herokuapp.com/searchbyname?barcode='+str(inbar)+'&name='+str(name)).json()
        #page =requests.get('http://127.0.0.1:5000/searchbyname?barcode='+str(inbar)+'&name='+str(name)).json()
    
    print(myquery)
    print(page)
    if page['status'] == "Not Found" or page['status'] == 'Error' or page['status'] == "Not Matched":             
        #print("NOT FOUND")
        result.at[i, 'no'] = str(i)
        result.at[i, 'UUID'] = str(str(df.at[i,'UUID']))
        result.at[i, 'barcode'] = 'N/A'
        result.at[i, 'title'] = 'N/A'
        result.at[i, 'einnumber'] = 'N/A'
        result.at[i, 'street'] = 'N/A'
        result.at[i, 'city'] = 'N/A'
        result.at[i, 'state'] = 'N/A'
        result.at[i, 'pcode'] = 'N/A'
        result.at[i, 'phone'] = 'N/A'
        result.at[i, 'status'] = str(page['status'])        
        result.to_csv(filename, index=False, encoding='utf8')
        
    elif page['status'] == "Found":
        result.at[i, 'no'] = str(i)
        result.at[i, 'UUID'] = str(str(df.at[i,'UUID']))
        result.at[i, 'barcode'] = str(page['Result']['barcode'])
        result.at[i, 'title'] = str(page['Result']['name'])
        result.at[i, 'einnumber'] = str(page['Result']['ein_number'])
        result.at[i, 'street'] = str(page['Result']['street'])
        result.at[i, 'city'] = str(page['Result']['city'])
        result.at[i, 'state'] = str(page['Result']['state'])
        result.at[i, 'pcode'] = str(page['Result']['zip'])
        result.at[i, 'phone'] = str(page['Result']['phone'])
        result.at[i, 'status'] = str(page['status'])
        result.to_csv(filename, index=False, encoding='utf8')
