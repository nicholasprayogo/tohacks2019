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
Minimum_Balance = [] #Is there a minimum balance, yes or no
Monthly_Fees = [] #What are the monthly fees
Account_Type = [] #Is it student or youth account
Debit_Type = [] #unlimited or how many free per month
Debit_Fees = [] #What are the overage fees
Etransfers = [] #how many a month
Etransfer_Fees = [] #overage fees
Interest = [] #what is the monthly interest


#CIBC Chequing Account webpage for Youth & Student
link = "https://www.cibc.com/en/personal-banking/bank-accounts/youth-banking-offers.html"
page = requests.get(link)

#Get HTML Content related to Chequing Account Name
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_='subheading-large-light')
stringo = str(ok)

start = stringo.find("CIBC")
temp = stringo[start:]

end = temp.find("<")
k = temp[:end-1]
k.replace(" ", "")
Account_Names.append(k)

if("Youth" in temp[:end]):
    Account_Type.append("youth")
else:
    Account_Type.append("student")


#Get HTML Content related to Chequing Account Info
link2="https://www.cibc.com/en/personal-banking/bank-accounts/youth-banking-offers/fees-and-details.html"
page = requests.get(link2)
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_="banner-body-copy")
stringo = str(ok)
Interest.append("0.15")

debits = str(ok)
debits = debits.split(',') #split into array for each type of account

i=0
while i < len(debits):
    temp = debits[i]
    if("transactions"in debits[i]):
        temp = debits[i]
        if("unlimited" in temp):
            Debit_Type.append("unlimited")
            Debit_Fees.append("0")
        if("e-Transfer" in temp):
            Etransfer_Fees.append("0")
            Etransfers.append("unlimited")
    if("balance" not in temp):
        Minimum_Balance.append("no") 
    if("account fee" in debits[i]):
        temp = debits[i]
        ok=temp.find("account fee")
        ok2 = temp[ok-20:ok+20]
        if("no" in ok2):
            Monthly_Fees.append("no")
        else:
            Monthly_Fees.append("yes")

    i=i+1

#debugging
#file = open("dump.txt","w+")
#file.write(stringo)
#file.close 

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

