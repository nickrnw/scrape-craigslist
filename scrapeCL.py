# -*- coding: utf-8 -*-
import re

import mysql.connector
import requests
from bs4 import BeautifulSoup

# Connect to our DB
db_connection = mysql.connector.connect(
    host="localhost",
    user="testing",
    passwd="",
    database="job_postings"
)

# Get a handle on our db connection
db_cursor = db_connection.cursor(prepared=True)


def removeselecttext(needle, haystack):
    return haystack.replace(needle, '')


# Write each word to a table for analysis
def writeWordstoDB(id, body):
    # tokenize into words
    words = body.split(' ')

    # loop the words and insert
    for word in words:
        data = (word, row_id)
        state = """ INSERT INTO words
                       (word, post_id) VALUES (%s,%s)"""
                       
        db_cursor.execute(statement, data)
        db_connection.commit()


# Write URL & Title to our DB
def writetodatabase(title, url, body):
    # remove un-wanted text
    body = body.replace('qr code link to this post', '')

    data = (title, url, body)
    statement = """ INSERT INTO postings
                       (title, url, body) VALUES (%s,%s, %s)"""
    db_cursor.execute(statement, data)

    # get the row id
    row_id = db_cursor.lastrowid

    db_connection.commit()

    # write each word to the words table
    writeWordstoDB(row_id, body)


# scrub text
def standardize_text(content):
    content = re.sub('[^a-zA-Z\d\s:]', '', content)
    return content.encode('utf8', 'ignore').lower()


def request_post_body(title, url):
    # Request the post url
    response = requests.get(url)

    data = response.text

    soup = BeautifulSoup(data, 'lxml')

    post_body = soup.findAll('section', {'id': 'postingbody'})

    for post in post_body:
        body = standardize_text(post.text)
        body = body.replace(' ', '')
        writetodatabase(title, url, body)


# Main
def crawl_craigslist():
    url = 'https://' + 'portland' + '.craigslist.org/search/sof'

    # Make a request & get a response object
    response = requests.get(url)

    # Create a variable to hold our response body
    data = response.text

    # Init Beautifulsoup to parse our response body
    soup = BeautifulSoup(data, 'lxml')

    # Locate all <a> with defined class
    titles = soup.findAll('a', {'class': 'result-title'})

    for title in titles:
        title_text = standardize_text(title.text)
        href_text = title['href']
        request_post_body(title_text, href_text)


# main
crawl_craigslist()
