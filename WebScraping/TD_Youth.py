import azure.cosmos.cosmos_client as cosmos_client
from bs4 import BeautifulSoup
import requests
import re
from itertools import groupby
from objdict import ObjDict
import json

#Cosmos DB Configuration info
config = {
    'ENDPOINT': 'https://tohacks-sql.documents.azure.com:443/',
    'PRIMARYKEY': 'rVffuZftq16dKAIkAfsh81tdgo2UUjogYtpeSv0WtWGWWogovgjLKtlHBhkq1OKoLkmc5FV9UbpxfLv1hVhVUg==',
    'DATABASE': 'TOHacks Data',
    'CONTAINER': 'Options'
}

# Initialize the Cosmos client and relevant links
client = cosmos_client.CosmosClient(url_connection=config['ENDPOINT'], auth={
                                    'masterKey': config['PRIMARYKEY']})
database_link = 'dbs/' + 'TOHacks Data'
collection_link = database_link + '/colls/' + 'Options'

#Account variable arrays
Account_Names = []  #Account Names
Monthly_Fees = [] #What are the monthly fees
Account_Type = [] #Is it student or youth account
Debit_Type = [] #unlimited or how many free per month
Debit_Fees = [] #What are the overage fees
Etransfers = [] #how many a month
Etransfer_Fees = [] #overage fees
Interest = [] #what is the monthly interest

#RBC Chequing Account webpage for Youth & Student
page = requests.get("https://www.td.com/ca/en/personal-banking/products/bank-accounts/savings-accounts/youth-account/")
link = "https://www.td.com/ca/en/personal-banking/products/bank-accounts/savings-accounts/youth-account/"
#Get HTML Content related to Chequing Account Names
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_="td-container")
stringo = str(ok)

debits = stringo.split(',') #split into array for each type of account

temp = debits[0]
if('class="td-container"' in temp ):
    start = stringo.find('core" typeof="tri:BannerProduct">')
    temp = stringo[start+31:]
    start = temp.find('TD')
    temp = temp[start:]
    end = temp.find("nt")
    Account_Names.append(temp[:end+2])

if("Youth" in temp[:end+2]):
    Account_Type.append("youth")
else:
    Account_Type.append("student")

Interest.append("0.05")

ok = soup.find_all(class_="td-rte-margin-bottom-medium")
stringo = str(ok)

if("transactions"in stringo):
        temp = stringo
        if("unlimited" in temp):
            Debit_Type.append("unlimited")
            Debit_Fees.append("0")
            Etransfer_Fees.append("0")
            Etransfers.append("unlimited")

if("fee" in stringo):
    temp = stringo
    ok=temp.find("transaction fees")
    ok2 = temp[ok-20:ok+20]
    if(len(Monthly_Fees)==0):
        if("no" in ok2):
            Monthly_Fees.append("no")
        else:
            Monthly_Fees.append("yes")


#print(Monthly_Fees)
#print(Debit_Fees)
#print(Debit_Type)
#print(Etransfer_Fees)
#print(Etransfers)
#print(Account_Names)
#print(Interest)
#debugging
#file = open("dump","w+")
#file.write(stringo)
#file.close()

#Parse everything into a JSON object
data = ObjDict()

j=0
while ( j < len(Account_Names)):
    data['name']=Account_Names[j]
    data['type']=Account_Type[j]
    data['monthly_fee']=Monthly_Fees[j]
    data['etrans_num']=Etransfers[j]
    data['etrans_fee']= Etransfer_Fees[j]
    data['trans_num']= Debit_Type[j]
    data['trans_fee']=Debit_Fees[j]
    data['interest']=Interest[j]
    data['link']=link
    #json_data = data.dumps()
    j=j+1
    #After creating the json, upload the object to the database
    client.CreateItem(collection_link,data) #upload the data to the database