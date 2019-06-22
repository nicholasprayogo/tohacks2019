from bs4 import BeautifulSoup
import requests

#Chequing Accounts Page
page = requests.get("https://www.rbcroyalbank.com/accounts/chequing-accounts.html")

#Get HTML content related to Chequing account monthly fees
soup = BeautifulSoup(page.content, 'html.parser')
interest = soup.find_all(class_='text-center text-script')

#Get HTML content related to Account Names



#Parse
s_string = str(interest)

most_recent_index=s_string.find("$") #find initial occurence of $ in the string
starting_position = 0

Account_Names = []
Monthly_Fees = []  



while (starting_position > -1):
    print(most_recent_index)
    print(s_string[most_recent_index:most_recent_index+6])
    temp = s_string[most_recent_index:most_recent_index+6].replace('<', '')
    print(temp)
    Monthly_Fees.append(temp)
    s_string=s_string[most_recent_index+6:]
    print(s_string)
    most_recent_index = s_string.find("$")
    starting_position = most_recent_index

print(Monthly_Fees)


file = open("dump.txt","w+")
file.write(s_string)
file.close 

