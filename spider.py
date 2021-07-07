#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, requests, sys, getopt, re, urllib3
#from bs4 import BeautifulSoup

# disable warning for SSL verification
urllib3.disable_warnings()

# The following is the basic information need for perform spider task
URL_REGULAR_EXPRESSION = "<a.*href=\"(https?://.*?)[\"|\'].*"
url = ''
deep = 0
logfile = "spider.log"
loglevel = 1
concurrency = 1
key = ''
f = open("spider.txt", 'w')

'''
Purpose: use to remove duplicates and the ones that are too deep
format: <url(str), depth(int)>
'''
dict_of_dept = {}


''' 
Purpose: get the information needed from the command line arguments
effect: edit the basic infomation
requirement: argv must have length of even number
Contract: (list of str) -> 
'''
def get_args(argv):
    global url, deep, logfile, loglevel, concurrency, key, dict_of_dept

    try:
        opts, args = getopt.getopt(argv, "u:d:f:l:", ["concurrency=", "key="])
    except getopt.GetoptError:
        print("There is a error with the arguments")
        sys.exit(2)
    

    if not (opts[0].__contains__('-u') and opts[1].__contains__('-d') and opts[2].__contains__('-f')) :
        print("The required argument is not given")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-u':
            url = arg
            #the url itself is consider as depth 1(parent)
            dict_of_dept[url] = 1
        if opt == '-d':
            deep = int(arg)
        if opt == '-f':
            logfile = arg
        if opt == '-l':
            loglevel = int(arg)
        if opt == '--concurrency':
            concurrency = int(arg)
        if opt == '--key':
            key = arg

    

''' 
Purpose: get the information needed from the command line arguments
effect: edit the basic infomation
requirement: argv must have length of even number
Contract: (list of str) -> 
'''
def get_html(url):
    res = requests.get(url, verify = False)
    html = res.text
    return html

def get_all_url_from_html(html):
    list_of_url = re.findall(URL_REGULAR_EXPRESSION, html)
    return list_of_url


def get_url_to_deep(url,depth):
    global f, dict_of_dept

    # if it is too deep, just no nothing and return
    if(depth > deep):
        return
    
    try:
        #Get all url from 
        html = get_html(url)
        list_of_url = get_all_url_from_html(html)
        for u in list_of_url:
            #if it is already in dict, remove it
            if u not in dict_of_dept:
                dict_of_dept[u]= dict_of_dept[url]+1
                f.write(u)
                get_url_to_deep(u, depth + 1)

    except Exception as e:
        print("%s" % e)
 


if __name__ == "__main__":
    get_args(sys.argv[1:])
    get_url_to_deep(url, 1)
    f.close()