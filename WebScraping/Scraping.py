from bs4 import BeautifulSoup
import requests

page = requests.get("https://www.rbcroyalbank.com/accounts/chequing-accounts.html")

soup = BeautifulSoup(page.content, 'html.parser')
interest = soup.find_all(class_='text-center text-script')
#fees = list(interest.children)

fee = "$"
s_string = str(interest)

most_recent_index=s_string.find(fee) #find initial occurence of $ in the string

while most_recent_index != -1:
    print(s_string.find(fee))
    print(s_string[most_recent_index:most_recent_index+6])
    most_recent_index=s_string.find(fee) #find the next occurence to see if there are any more

file = open("dump.txt","w+")
file.write(s_string)
file.close 

