
import requests
import random
import sys
import argparse
import time
import numpy as np
import json

def get_ip_address():
    return str(random.randint(1,255)) + "." + str(random.randint(1,255)) + "." + str(random.randint(1,255)) + "." + str(random.randint(1,255))

def http_get_logs(url):
    r = requests.get(url)

parser = argparse.ArgumentParser()
parser.add_argument("target",help="<http...> the http(s) location to send the GET request")
args = parser.parse_args()
i = 0
random.seed(1)
pages = ['/','/test.css','/contactus.html','/img_top.png','/services.html','/services/product1.html','/catalog.html','/services/product2.html','/img_bottom.gif']
pages_size = {'/':17692,'/test.css':1439,'/contactus.html':9926,'/img_top.png':256,'/services.html':5293,'/services/product1.html':7529,'/catalog.html':10237,'/services/product2.html':2735,'/img_bottom.gif':52}
pages_prob = [0.7,0.01,0.04,0.1,0.05,0.02,0.035,0.035,0.01]

for i in range(250000):
    ip_add = get_ip_address()
    tot_time = time.strftime("%d/%b/%Y:%d:%H:%M:%S")
    get_page = np.random.choice(pages,p = pages_prob)
    response = [200,301,404,500]
    get_response = str(np.random.choice(response, p = [0.93,0.04,0.008,0.022]))
    num_size = str(pages_size[get_page])
    #get_browsers = str(np.random.choice(browsers, p = [0.20,0.20,0.20,0.20,0.20]))
    http_get_logs(args.target + '?browseraction=' +ip_add + " - - [" + tot_time + " -0800] \\\"GET " + get_page + " HTTP/1.1\\\" " + get_response + " "+ num_size)
    print("sending no " + str(i))
    #http_get_logs(args.target + '?browseraction=('+ip_add + " - - [" + tot_time + " -0800] \"GET " + get_page + " HTTP/1.1\" " + get_response + " "+ num_size + " \"" + get_browsers + "\")")
    #http_get_logs((args.target + "?browseraction=" + ip_add + " - - [" + tot_time + " -0800] \\\"GET " + get_page + " HTTP/1.1\\\" ")) + get_response + " " + num_size))
    if get_page == '/':
        #print(ip_add + " - - [" + tot_time + " -0800] \"GET /img3.pn HTTP/1.1\" 404 87 \"" + get_browsers + "\"")
        http_get_logs(args.target + '?browseraction=' + ip_add + " - - [" + tot_time + " -0800] \\\"GET /img3.pn HTTP/1.1\\\" 404 87")
    sys.stdout.flush()
    time.sleep(random.random())
    i += 1








