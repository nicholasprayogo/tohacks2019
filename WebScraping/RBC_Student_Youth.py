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


#RBC Chequing Account webpage for Youth & Student
page = requests.get("https://www.rbcroyalbank.com/accounts/youth-student-banking.html")
link = "https://www.rbcroyalbank.com/accounts/youth-student-banking.html"
#Get HTML Content related to Chequing Account Names
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_='h4 text-center text-blue')
stringo = str(ok)

#Get HTML content related to account info
debs = soup.find_all(class_='disc-list')
debits = str(debs)
debits = debits.split(',') #split into array for each type of account
debs = debits

start = stringo.find('RBC') 
counter = 0

while (start > -1):
    
    end = stringo.find('</a>') #find first occurence of the closing charachters
    temp = stringo[start:end].replace("’","'")
    #print(temp)
    Account_Names.append(temp)

    stringo=stringo[end+1:] #start new substring from the end of the previous
   
    start = stringo.find('RBC')


#Assume there are no monthly fees so set all values to 0, then check after
#Also check if they are student or youth accounts
i=0
while ( i < len(Account_Names)):
    #Find information relevant to debits each month
    temp = debits[i].find("debit") 
    if(temp > -1):
        t2 = debits[i][temp-10:temp+10]
        if("Unlimited" in t2):
            Debit_Type.append("unlimited")
            Debit_Fees.append("0")
        else:
            result= [int(''.join(i)) for is_digit, i in groupby(t2, str.isdigit) if is_digit]
            Debit_Type.append(str(result[0]))
            Debit_Fees.append("$1.25")

    #Standard fees are added if not found in html tags
    if("interest" not in debs):
        Interest.append("0")
    
    if("etransfer" not in debs):
        Etransfer_Fees.append("0")
        Etransfers.append("unlimited")

    #Find information related to minimum balance
    temp = debits[i].find("minimum balance") 
    if(temp > -1):
        t2 = debits[i][temp-20:temp+10]
        if("No" in t2):
            Minimum_Balance.append("no")
        else:
            Minimum_Balance.append("yes")
    

    #Find relevant account type information
    if("Student" in Account_Names[i]):
        Account_Type.append("student")
    else:
        Account_Type.append("youth")

    

    Monthly_Fees.append(0)
    i=i+1

Monthly_Fees[0]="$10.95"


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



