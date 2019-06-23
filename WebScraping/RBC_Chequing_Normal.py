from bs4 import BeautifulSoup
import requests

#Stores Account Names
Account_Names = []
#Stores Monthly Fees
Monthly_Fees = [] 

#RBC Normal Chequing Account webpage
page = requests.get("https://www.rbcroyalbank.com/accounts/chequing-accounts.html")

#Get HTML Content related to Chequing Account Names
soup = BeautifulSoup(page.content, 'html.parser')
ok = soup.find_all(class_='h4 text-center')
stringo = str(ok)
#debugging
file = open("dump.txt","w+")
file.write(stringo)
file.close 
start = stringo.find('RBC') 
counter = 0
#ter">RBC No Limit Banking</h3>
#center">RBC Signature No Limit Banking</h3>
while (start > -1):
    #print(start)
    if(counter == 0):
        end = stringo.find('<br')
    else:
        end = stringo.find('</h3>') #find first occurence of the closing charachters
    
    print("What I found: " + stringo[start:end])
    temp = stringo[start:end]
    if not temp.strip():
        print(temp)
        Account_Names.append(temp)

    stringo=stringo[end+1:] #start new substring from the end of the previous
    #print(stringo)
    start = stringo.find('RBC')
    counter=1

#Get HTML Content related to Monthly Fees
interest = soup.find_all(class_='text-center text-script')



#Change list into string of Monthly Fee Information
s_string = str(interest)
#Finds initial occurence of the $ charachter in HTML 
most_recent_index=s_string.find("$") #find initial occurence of $ in the string
starting_position = 0


#Loops through to find all Instances of $ to then get monthly fee value
#Values are placed into Monthly_Fees array
while (starting_position > -1):
    #print(most_recent_index)
    #print(s_string[most_recent_index:most_recent_index+6])
    temp = s_string[most_recent_index:most_recent_index+6].replace('<', '')
    #print(temp)
    Monthly_Fees.append(temp)
    s_string=s_string[most_recent_index+6:]
    #print(s_string)
    most_recent_index = s_string.find("$")
    starting_position = most_recent_index
