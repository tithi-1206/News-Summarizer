import requests
from bs4 import BeautifulSoup
import csv
import os
import json
import logging
import time
import schedule


################################################################################################################
# function to write (append) the title and content of a news in its respective file
def writeToCSVFile(categoryName, title, content):
    path = "D:\\News\\"
    file = path + categoryName + ".csv"

    try:
        with open(file, 'a', encoding='utf-8', newline='') as fp:
            csvWriter = csv.writer(fp)
            csvWriter.writerow([title, content])
        fp.close()
    except Exception as e:
        logger.error(f'An error occurred while opening/writing to CSV file for category: {categoryName} : {e}')
        print(f'An error occurred: {e}')
################################################################################################################


################################################################################################################
# function to make a csv file for a category
def makeCSVFile(categoryName):
    path = "D:\\News\\"
    file = path + categoryName + ".csv"
    try:

        with open(file, 'w', encoding='utf-8', newline='') as fp:
            pass
        fp.close()
        logger.info(f'CSV file created for category: {categoryName}')
    except Exception as e:
        logger.error(f'An error occurred while making a CSV file for category: {categoryName} : {e}')
        print(f'An error occurred: {e}')
################################################################################################################


################################################################################################################
# function to write scraped content of particular news into its csv file
def scrapeNews(categoryName, url):

    if categoryName == "Entertainment":     # scrape Times of India
        newsResponse = requests.get(url)
        if newsResponse.status_code == 200:
            htmlContentOfNews = newsResponse.text
            newsSoup = BeautifulSoup(htmlContentOfNews, 'html.parser')

            title = newsSoup.find('h1')
            title = title.text

            content = newsSoup.find('p')
            content = content.text

            # print(title)
            # print(content)
            writeToCSVFile(categoryName, title, content)
        else:
            print(f'Failed to retrieve content. Status code: {newsResponse.status_code}')

    elif categoryName == "India":       # scrape NDTV
        newsResponse = requests.get(url)
        if newsResponse.status_code == 200:
            htmlContentOfNews = newsResponse.text
            newsSoup = BeautifulSoup(htmlContentOfNews, 'html.parser')

            # print(newsSoup.prettify())

            title = newsSoup.find('h1')
            title = title.text
            # NDTV headlines have extra space character at start, remove that
            title = title[1:]

            contentList = newsSoup.find_all('p')
            if contentList:
                content = ""
                for i in range(0, len(contentList) - 4):      # since last 4 paragraphs of NDTV website is noise
                    content += contentList[i].text
                    content += " "

                # print(title)
                # print(content)
                writeToCSVFile(categoryName, title, content)
        else:
            print(f'Failed to retrieve content. Status code: {newsResponse.status_code}')

    elif categoryName == "Business":        # scrape Money Control
        newsResponse = requests.get(url)
        if newsResponse.status_code == 200:
            htmlContentOfNews = newsResponse.text
            newsSoup = BeautifulSoup(htmlContentOfNews, 'html.parser')

            title = newsSoup.find('h1')
            title = title.text

            contentList = newsSoup.find_all('p')
            content = ""
            # content starts from para 51st and skip last 4 paras (noise) for Money Control
            for i in range(51, len(contentList) - 4):
                content += contentList[i].text
                content += " "
            # some articles require PRO subscription of Moneycontrol. Filtering those articles (Discarding)
            if content.find("Limited Period offer on Moneycontrol PRO. Subscribe to PRO and get up to  Ad free experience Experience a non-intrusive navigation and faster response in the ad free mode Sharpest Opinions Access to 230+ exclusive stories per month from our editorial and Experts") == -1:
                # print(title)
                # print(content)
                writeToCSVFile(categoryName, title, content)

        else:
            print(f'Failed to retrieve content. Status code: {newsResponse.status_code}')

    elif categoryName == "Technology":      # scrape GSMArena
        newsResponse = requests.get(url)
        if newsResponse.status_code == 200:
            htmlContentOfNews = newsResponse.text
            newsSoup = BeautifulSoup(htmlContentOfNews, 'html.parser')

            title = newsSoup.find('h1')
            title = title.text

            raw_content = ""
            # finding the div with id 'review-body', as it contains all the 'p' tags of the content
            divContainingContent = newsSoup.find('div', {'id': 'review-body'})
            if divContainingContent:
                paragraphs = divContainingContent.find_all('p')
                for p in paragraphs:
                    # to remove noise
                    if p.text.find("Source", 0, 6) == -1 and p.text.find("Via", 0, 3) == -1:
                        raw_content += p.text
                        raw_content += " "

                # to remove any newlines
                content = ' '.join(raw_content.splitlines())
                # print(title)
                # print(content)
                writeToCSVFile(categoryName, title, content)
        else:
            logger.error(f'Failed to retrieve content of a news article of category: {categoryName}')
            print(f'Failed to retrieve content. Status code: {newsResponse.status_code}')
    else:
        pass
#################################################################################################################


#################################################################################################################
# function that scrapes a category and stores all the news headlines and their contents in a separate text file
def scrapeCategory(categoryName, url):

    homepage = "https://news.google.com/"

    # all links of required news sites for a category are stored in this list
    allLinksOfCategory = []

    categoryResponse = requests.get(url)
    if categoryResponse.status_code == 200:
        htmlContentOfCategory = categoryResponse.text
        categorySoup = BeautifulSoup(htmlContentOfCategory, 'html.parser')

        # this is a list of all the divs containing 'a' tag having attribute 'href' targeting the site of news
        # all these divs are of class "XlKvRb"
        articles = categorySoup.find_all('div', class_='XlKvRb')

        if categoryName == "Entertainment":

            # making the csv file for "Entertainment" category
            makeCSVFile(categoryName)

            # "3RpbWVzb2ZpbmRpYS5pbmRpYXRpbWVzLmNvbS92aWRlb3MvZXRpbWVzL2JvbGx5d29v" is the url sub-string found in MANY Times of India links.
            # This is the case for (i.e. works for) 'Entertainment' category ONLY
            for article in articles:
                link = article.find('a')
                if link:
                    hreff = link.get('href')
                    if "3RpbWVzb2ZpbmRpYS5pbmRpYXRpbWVzLmNvbS92aWRlb3MvZXRpbWVzL2JvbGx5d29v" in hreff:
                        fullLink = homepage + hreff
                        allLinksOfCategory.append(fullLink)

            # printing all links of the category
            for linkk in allLinksOfCategory:
                scrapeNews(categoryName, linkk)

        elif categoryName == "India":

            # making the csv file for "India" category
            makeCSVFile(categoryName)

            # "3d3Lm5kdHYuY29tL2luZGlhLW5ld" is the url sub-string found in MANY NDTV links.
            # This is the case for (i.e. works for) 'India' category ONLY
            for article in articles:
                link = article.find('a')
                if link:
                    hreff = link.get('href')
                    if "3d3Lm5kdHYuY29tL2luZGlhLW5ld" in hreff:
                        fullLink = homepage + hreff
                        allLinksOfCategory.append(fullLink)

            # printing all links of the category
            for linkk in allLinksOfCategory:
                scrapeNews(categoryName, linkk)

        elif categoryName == "Business":

            # making the csv file for "Business" category
            makeCSVFile(categoryName)

            # "3d3dy5tb25leWNvbnRyb2wuY29tL25ld3MvYnVzaW5" is the url sub-string found in MANY Money Control links.
            # This is the case for (i.e. works for) 'India' category ONLY
            for article in articles:
                link = article.find('a')
                if link:
                    hreff = link.get('href')
                    if "3d3dy5tb25leWNvbnRyb2wuY29tL25ld3MvYnVzaW5" in hreff:
                        fullLink = homepage + hreff
                        allLinksOfCategory.append(fullLink)

            # printing all links of the category
            for linkk in allLinksOfCategory:
                scrapeNews(categoryName, linkk)

        elif categoryName == "Technology":

            # making the csv file for "Technology" category
            makeCSVFile(categoryName)

            # "3d3LmdzbWFyZW5hLmNvb" is the url sub-string found in MANY GSMArena links.
            # This is the case for (i.e. works for) 'India' category ONLY
            for article in articles:
                link = article.find('a')
                if link:
                    hreff = link.get('href')
                    if "3d3LmdzbWFyZW5hLmNvb" in hreff:
                        fullLink = homepage + hreff
                        allLinksOfCategory.append(fullLink)

            # printing all links of the category
            for linkk in allLinksOfCategory:
                scrapeNews(categoryName, linkk)

        else:
            pass

    else:
        logger.error(f'Failed to retrieve content of category: {categoryName}')
        print(f'Failed to retrieve content. Status code: {categoryResponse.status_code}')
    logger.info(f'All news links of category: {categoryName} retrieved successfully')
#################################################################################################################


#################################################################################################################
# using API to summarize content
def sum_news(content):
    url = "https://api.ai21.com/studio/v1/summarize"
    payload = {
        "sourceType": "TEXT",
        "source": content
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer ZMbqqDC60MDfIyBR1be0aZcGLC2MeqXe"
    }

    # Retry summarization up to 3 times if the initial summary is 'None'
    for _ in range(3):
        response = requests.post(url, json=payload, headers=headers)
        response_data = json.loads(response.text)
        summary = response_data.get('summary', '')

        if summary is not None and summary.strip() != '':
            return summary  # Return the summary if it's not 'None'

    return ''  # Return an empty string if all retries result in 'None' summaries
#################################################################################################################


#################################################################################################################
# function to summarize a category using api
def summarizeCategory(categoryName):
    path = "D:\\News\\"
    ipfile = path + categoryName + ".csv"
    opfile = path + categoryName + "_Summarized" + ".csv"

    try:
        with open(ipfile, 'r', encoding='utf-8', newline='') as input_file, open(opfile, 'w', encoding='utf-8', newline='') as output_file:
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file)

            for row in csv_reader:
                original_content = row[1]

                # count number of words
                words = original_content.split()
                numWords = len(words)
                if numWords == 140:  # dont summarize
                    # copy as it is
                    csv_writer.writerow([row[0], row[1]])

                else:  # summarize
                    summarized_content = sum_news(original_content)  # Apply your summarization function

                    # Only write the row if summarized_content is not an empty string
                    if summarized_content != '':
                        # Remove all occurrences of the word 'None'
                        summarized_content = summarized_content.replace("None", "")

                        # Write the summarized content to the new CSV file
                        csv_writer.writerow([row[0], summarized_content])
    except Exception as e:
        logger.error(f'An Error occurred while opening CSV files for summarizing for category: {categoryName}: {e}')
        print(f'An Error occurred while opening CSV files for summarizing for category: {categoryName}: {e}')
    logger.info(f'News of category: {categoryName} summarized successfully')
    input_file.close()
    output_file.close()
#################################################################################################################


################################################ DRIVER CODE ####################################################
def DRIVERCODE():

    # making a folder "News" in D drive
    if not os.path.exists("D:\\News"):
        os.makedirs("D:\\News")
        logger.info("Folder 'News' created in path: 'D:\\News'")

    # SCRAPING THE HOMEPAGE (for links of categories)
    homepage = "https://news.google.com/"
    homepageResponse = requests.get(homepage)

    # all categories and their links are stored in this dictionary
    homepageCategoryNameAndLinks = {}

    if homepageResponse.status_code == 200:
        html_content = homepageResponse.text
        homepageSoup = BeautifulSoup(html_content, 'html.parser')

        # Find all anchor elements (<a>) and extract their href attributes and adding them to dictionary
        # The dictionary has keys as the name of categories and values as href links
        for anchor in homepageSoup.find_all('a', attrs={'aria-label': True, 'href': True}):
            label = anchor['aria-label']
            href = homepage+anchor['href']
            homepageCategoryNameAndLinks[label] = href
        logger.info("Homepage categories retrieved")
    else:
        logger.error("Failed to retrieve content of homepage")
        print(f'Failed to retrieve content. Status code: {homepageResponse.status_code}')

    scrapeCategory("Entertainment", homepageCategoryNameAndLinks["Entertainment"])
    scrapeCategory("India", homepageCategoryNameAndLinks["India"])
    scrapeCategory("Business", homepageCategoryNameAndLinks["Business"])
    scrapeCategory("Technology", homepageCategoryNameAndLinks["Technology"])
    logger.info("ALL CSV FILES CREATED")
    print("ALL CSV FILES CREATED")

    summarizeCategory("Entertainment")
    summarizeCategory("India")
    summarizeCategory("Business")
    summarizeCategory("Technology")
    logger.info("ALL SUMMARIZED CSV FILES CREATED")
    print("ALL SUMMARIZED CSV FILES CREATED")
###############################################################################################################








# setting up a logger for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename="D:\\News\\logFile.log", filemode="w")
logger = logging.getLogger("newsApp")


# immediate initial run
DRIVERCODE()

# scheduling the program every one hour
schedule.every(15).minutes.do(DRIVERCODE)

while True:
    schedule.run_pending()
    # checking pending tasks every 15 minutes
    time.sleep(900)