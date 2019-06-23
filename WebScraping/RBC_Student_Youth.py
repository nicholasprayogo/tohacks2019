from bs4 import BeautifulSoup
import requests
import re
from itertools import groupby
from objdict import ObjDict
import json



Account_Names = []  #Account Names
Minimum_Balance = [] #Is there a minimum balance, yes or no
Monthly_Fees = [] #What are the monthly fees
Account_Type = [] #Is it student or youth account
Debit_Type = [] #unlimited or how many free per month
Etransfers = [] #how many 


#RBC Chequing Account webpage for Youth & Student
page = requests.get("https://www.rbcroyalbank.com/accounts/youth-student-banking.html")

#Get HTML Content related to Chequing Account Names
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_='h4 text-center text-blue')
stringo = str(ok)

#Get HTML content related to debits per month
debs = soup.find_all(class_='disc-list')
debits = str(debs)
debits = debits.split(',') #split into array for each type of account

#debugging
st = str(debs)
file = open("dump.txt","w+")
file.write(st)
file.close 


start = stringo.find('RBC') 
counter = 0

while (start > -1):
    #print(start)
    end = stringo.find('</a>') #find first occurence of the closing charachters
    #print("What I found: " + stringo[start:end])
    temp = stringo[start:end].replace("’","'")
    print(temp)
    Account_Names.append(temp)

    stringo=stringo[end+1:] #start new substring from the end of the previous
    #print(stringo)
    start = stringo.find('RBC')

#print(Account_Names)

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
        else:
            result= [int(''.join(i)) for is_digit, i in groupby(t2, str.isdigit) if is_digit]
            Debit_Type.append(str(result[0]))

    #Find information related to minimum balance
    temp = debits[i].find("minimum balance") 
    if(temp > -1):
        t2 = debits[i][temp-20:temp+10]
        if("No" in t2):
            Minimum_Balance.append("no")
        else:
            Minimum_Balance.append("yes")

    #Enter E Transfer Information
    Etransfers.append("unlimited")

    #Find relevant account type information
    if("Student" in Account_Names[i]):
        Account_Type.append("student")
    else:
        Account_Type.append("youth")

    #Almost always no monthly fee
    Monthly_Fees.append(0)
    i=i+1

Monthly_Fees[0]=10.95


#Parse everything into a JSON object
data = ObjDict()

j=0
while ( j < len(Account_Names)):
    data['name']=Account_Names[j]
    data['type']=Account_Type[j]
    data['fees']=Monthly_Fees[j]
    data['transactions']=Debit_Type[j]
    data['etransfers']=Etransfers[j]
    data['balance']=Minimum_Balance[j]
    json_data = data.dumps()
    print(json_data)
    j=j+1




