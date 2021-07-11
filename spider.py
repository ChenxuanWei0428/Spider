#!/usr/bin/env python3
# -*- coding: utf-8 -*-

" This is the spider program that allow command line input "

__author__ = "Austin Wei"

import json, requests, sys, getopt, re, urllib3, logging, asyncio
#from bs4 import BeautifulSoup

# disable warning for certificate
urllib3.disable_warnings()

# The following is the basic information need for perform spider task
URL_REGULAR_EXPRESSION = "<a.*href=\"(https?://.*?)[\"|\'].*"
url = ''
deep = 0
logfile = "spider.log"
loglevel = 1
concurrency = 1
key = ""
f = open("spider.txt", 'w')
total_visited = 0
total_saved = 0


'''
Purpose: use to remove duplicates and the ones that are too deep
format: <url(str), depth(int)>
'''
dict_of_dept = {}

# the list will store all of the coroutine that is required
coroutine = []

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
            if (arg != ""):
                logfile = arg
        if opt == '-l':
            loglevel = 10 * int(arg)
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


async def get_url_to_deep(url,depth):
    global f, dict_of_dept, total_saved, total_visited

    # if it is too deep, just no nothing and return
    if(depth > deep):
        return
    
    try:
        #Get all url from 
        html = get_html(url)
        list_of_url = get_all_url_from_html(html)
        for u in list_of_url:
            total_visited += 1
            #if it is already in dict, remove it
            if u not in dict_of_dept:
                print(u)
                logging.info(u)
                dict_of_dept[u]= dict_of_dept[url]+1
                if key in u:
                    total_saved += 1
                    #write the website with key work in the file
                    f.write(u)
                get_url_to_deep(u, depth + 1)

    except Exception as e:
        print("%s" % e)
    
    return True


'''
Purpose: print_info() print the total number of URL viseted and saved every 10 second
effect produce outpost to concole
'''
async def print_info():
    global total_saved, total_visited
    while True:
        print("total number saved: %d, total number visited: %d" % (total_saved, total_visited))
        await asyncio.sleep(10)
        try:
            all_done = True
            for task in coroutine:
                if (task.result() != True):
                    all_done = False
            break
        except asyncio.InvalidStateError:
            pass


if __name__ == "__main__":
    
    get_args(sys.argv[1:])
    #init the log file
    logging.basicConfig(filename= logfile,format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level = loglevel,filemode='w',datefmt='%Y-%m-%d%I:%M:%S %p')
    
    #init cores
    core_info = print_info()
    core_spider = get_url_to_deep(url, deep)
    
    #init the tasks
    loop = asyncio.get_event_loop()
    task_info = loop.create_task(core_info)

    coroutine = [loop.create_task(core_spider) for i in range(concurrency)]
    wait_coroutine = asyncio.wait(coroutine)
    loop.run_until_complete(task_info)
    loop.run_until_complete(wait_coroutine)



    f.close()
