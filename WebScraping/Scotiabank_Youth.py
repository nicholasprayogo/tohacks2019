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
page = requests.get("http://www.scotiabank.com/ca/en/personal/bank-accounts/students/getting-there-savings-program-youth.html")
link = "http://www.scotiabank.com/ca/en/personal/bank-accounts/students/getting-there-savings-program-youth.html"
#Get HTML Content related to Chequing Account Names
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_="bns--title title--h1")
stringo = str(ok)

debits = stringo.split(',') #split into array for each type of account
i=0
while(i < len(debits)):
    temp = debits[i]
    i=i+1

    if("transactions"in stringo):
        ok=stringo.find("monthly fees")
        temp = stringo[ok-10:ok+30]
        #print(temp)
        if len(Monthly_Fees) < 1:
            if("free" in temp):
                Monthly_Fees.append("no")
            else:
                Monthly_Fees.append("yes")

            ok=stringo.find("first")
            temp = stringo[ok+10:ok+15]

            Debit_Type.append(temp)

            ok=stringo.find("additional transactions")
            temp = stringo[ok+3:ok+15]
            temp = str(temp)
       
            Debit_Fees.append(temp)
    
            ok=stringo.find("transfer fee")
            temp = stringo[ok-20:ok+20]
           
            if("No" in temp):    
                Etransfer_Fees.append("0")
                Etransfers.append("unlimited")

            if("fee" in stringo):
                temp = stringo
                ok=temp.find("monthly fees")
                ok2 = temp[ok-20:ok+20]
        

temp = debits[0]

if('class="bns--title title--h1"' in temp ):
    start = stringo.find('bns--section ')
    temp = stringo[start+15:]
    start = temp.find('Savings')
    temp = temp[start:]
    end = temp.find("unt")
    Account_Names.append(temp[:end+3])

if("Student" in temp[:end+3]):
    Account_Type.append("youth")
else:
    Account_Type.append("student")

Interest.append("0.05")

ok = soup.find_all(class_="bns--mega-menu ")
stringo = str(ok)



#Parse everything into a JSON object
data = ObjDict()

j=0
while ( j < len(Account_Names)):
    data['name']=str("Getting There Savings Account")
    data['type']=str("youth")
    data['monthly_fee']=str("0")
    data['etrans_num']=str("unlimited")
    data['etrans_fee']= str("0")
    data['trans_num']= str("2")
    data['trans_fee']=str("1.25")
    data['interest']=str("0.05")
    data['link']=link
    #json_data = data.dumps()
    j=j+1
    #After creating the json, upload the object to the database
    client.CreateItem(collection_link,data) #upload the data to the database
