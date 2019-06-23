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
link = "https://www.cibc.com/en/student/bank-accounts.html"
page = requests.get(link)

#Get HTML Content related to Chequing Account Name
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_=" ")
stringo = str(ok)

#debugging
file = open("dump.txt","w+")
file.write(stringo)
file.close 

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




