""" Import the libraries or API needed to accomplish the project """
# Web Scraping
import requests
import pandas as pd
import json
import numpy as np
import requests
import html5lib
from bs4 import BeautifulSoup
import re
# For printing
import time
# Threading
import queue
import threading
# Concurrency
import concurrent.futures
NUM_THREADS = 10

# start the timer to get the time
start = time.time()
current_time = time.strftime("%H:%M:%S")
print ("Started at:", current_time)
print ("\n")

""" Declare and define some of the global variables
    main_url: As per the requirements, DLSU website will be used
        'https://www.dlsu.edu.ph'
    response: get the server response for the main url
        the content property, which is the body of the page, will be used
    soup:  instace of Beautiful soup
        has methods that will allow us to perform selections
    sub_links: contains all other sub urls in the main dlsu website
    data: raw data of all found websites on the main one
"""

main_url = 'https://www.dlsu.edu.ph'
response = requests.get(main_url)
soup = BeautifulSoup(response.content, 'lxml')

# Defined a dataset for the data and links
sub_links = []
data = []
url_limit = 10

""" Function: remove_duplicates
    This function searches all urls and removes the duplicatess record in the website
"""
def remove_duplicates(l): 
    for item in l:
        # searches all urls in the main website
        match = re.search("(?P<url>https?://[^\s]+)", item)
        if match is not None:
            # will append on the sub_links dataset
            sub_links.append((match.group("url")))

""" Main Body - Execution Process """

def get_urls(soup):
    # 1. Get all the links associated to the main URL -> 'https://www.dlsu.edu.ph'
    for link in soup.find_all('a', href=True):
        # append to the data all website links found on the main one
        data.append(str(link.get('href')))

    # 2. Remove the dublicates from the 'data'; Note: final list will be on sub_links
    remove_duplicates(data)

    # 3. while flag is true, gets the link address, remove duplicates, checking limits for the number of urls
    flag = True
    while flag:
        try:
            for link in sub_links:
                for j in soup.find_all('a', href=True):
                    # store in a temporary one
                    temp = []
                    source_code = requests.get(link)
                    soup = BeautifulSoup(source_code.content, 'lxml')
                    temp.append(str(j.get('href')))
                    remove_duplicates(temp)

                    if len(sub_links) > url_limit: # set limitation to number of URLs
                        break
                if len(sub_links) > url_limit:
                    break
            if len(sub_links) > url_limit:
                break
        except Exception as e:
            print(e)
            if len(sub_links) > url_limit:
                break

            
with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    executor.map(get_urls, soup)

# Display ALL links generated, no duplicates must be found.         
print ("The DLSU Website has the following sub URLS:")
for url in sub_links:
    print(url)

# Printing the time   
current_time = time.strftime("%H:%M:%S")
print ("\n\nEnded at:", current_time)
print ("Elapsed Time: %.2f seconds\n\n" % (time.time() - start))

""" Function deCFemail 
    For protected emails
"""
def deCFEmail(fp):
    try:
        r = int(fp[:2],16)
        email = ''.join([chr(int(fp[i:i+2], 16) ^ r) for i in range(2, len(fp), 2)])
        return email
    except (ValueError):
        pass


""" Temporary website urls to be scraped now """
workable_urls = ['https://www.dlsu.edu.ph/colleges/gcoe/office-of-the-dean/',
                'https://www.dlsu.edu.ph/colleges/ccs/office-of-the-dean/']

position = []
names = []
emails = []
department = []
urlsList = []
testList = []

temp = ""
temp_dept = ""
dept = "Department"
titles = ["Mr","Dr","Mrs","Ms"]

""" While Flag is equal to true, which signifies that table is equal to none,
    repeat this process;
    Else, proceed to the remaining of the code
    NOTE: This was done since there are times that soup cannot find instance of table.
    This process will be repeated unless, table has retrieved data already.
"""
print("Web Scraping has started... This will take a while... ")

def get_emails(url_index):
    global temp_dept
    global position
    global testList

    a = workable_urls[url_index]
    print("Url :", a)
    testpage = requests.get(a)
    soup2 = BeautifulSoup(testpage.content, 'lxml')

    try:
        # flag = True
        # while(flag):
        # Accessing the table itself for the current website
        table = soup2.find('div',{'class':'wpb_wrapper'})
        table

        # if (table!=None):
        #     print("Data extracted!\n")
        #     flag = False
        # else:
        #     print("Data is still being extracted...")
        #     flag = True

        """ Declaring the arrays where the data will be saved
            For future use.
            NOTE: Need to get the ff:
                (1) email
                (2) associated name
                (3) office
                (4) department/ unit
                (5) urls scraped
        """

        # getting the length of all tables on the website
        table_length = len(table.find_all('td'))

        # filling in the arrays with the data from the table
        for x in range(0,table_length):
            temp = table.find_all('td')[x]      
            # print("Temp:", temp)
            if dept in temp.text:
                temp_dept = temp.text
                # print("Dept:", temp_dept)
            elif any(word in temp.text for word in titles):
                names.append(temp.text)
                department.append(temp_dept)
            elif temp.text == None:
                pass
            else:
                position.append(temp.text)
                
            try:
                # email
                temp2 = table.find_all('td')[x].a['href']
                if "email-protect" in temp2:
                    emails.append(deCFEmail(temp2.split("#")[1]))
            except:
                pass
       
        """ Displays the length of names, urls, departments, positions, and emails"""
        print("Current number of information extracted on the given website")
        print("Number of names: ", len(names))
        print("Number of urls: ", len(urlsList))
        print("Number of departments: ", len(department))
        print("Number of positions: ", len(position))
        print("Number of emails: ", len(emails))
        print("\n")

        """ Filter and group together the extracted data """
        emails
        position = list(filter(None, position))

        testList = list(zip(names,position,emails,department))
        testList

        """ Next steps will be the output generation """

    except Exception as e:
        print('Data Failed to extract!')
        print(e)

# This is where threading begins, using the map() function to assign threads to run get_emails() and the index number'range(len(workable_urls))'
#  to be placed as parameters for get_emails
with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor2:
    executor2.map(get_emails, range(len(workable_urls))) 

# Declaration of Dataframe that will serve as the output NO. 1
df = pd.DataFrame (testList, columns = ['Name','Position', 'Email', 'Department'])
text = "Congratulations! You have extracted the following information: " 

# Saving the content to the text file named "Extracted_Information.txt"
np.savetxt('Extracted_Information.txt',  df.values, fmt='%s, %s, %s, %s', delimiter=" , ", newline="\n", header=text)

# Declaring and defining the variables to be input in the text file 2
text2 = "Statistics of the Website"
df2 = [('URL: '+str(main_url)), ('Number of pages scraped: '+ str(len(sub_links))), ('Total No. of Emails Extracted: ' + str(len(emails)))]
# Saving the content to the text file named "Statistics.txt"
np.savetxt('Statistics.txt',  df2, fmt='%s', delimiter=" \n ",  header=text2)

print("Web Scraping succesfully completed. Check your files for the extracted information and statistics.")
print("Open Extracted_Information.txt and Statistics.txt")



