from bs4 import BeautifulSoup
import requests

#Stores Account Names
Account_Names = []
#Stores Monthly Fees
Monthly_Fees = [] 

#RBC Normal Chequing Account webpage
page = requests.get("https://www.rbcroyalbank.com/accounts/youth-student-banking.html")

#Get HTML Content related to Chequing Account Names
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_='h4 text-center text-blue')
stringo = str(ok)
#debugging
file = open("dump.txt","w+")
file.write(stringo)
file.close 
start = stringo.find('RBC') 
counter = 0


while (start > -1):
    #print(start)
    end = stringo.find('</a>') #find first occurence of the closing charachters
    #print("What I found: " + stringo[start:end])
    temp = stringo[start:end]
    Account_Names.append(temp)

    stringo=stringo[end+1:] #start new substring from the end of the previous
    #print(stringo)
    start = stringo.find('RBC')

print(Account_Names)

