#!/usr/bin/python
# pastebin scraper v3
# written by unix-ninja

import argparse
import BeautifulSoup
import datetime
import json
import os
import Queue
import random
import requests
import sys
import threading
import time

############################################################
# Configs

max_seen = 500
num_workers = 1
pastesseen = set()
pastes = Queue.Queue()

############################################################
# Functions

def downloader():
    global app_running
    # download delay is small. we can increase it for errors
    delay = 1.2
    while app_running:
        today = datetime.datetime.today().strftime("%Y/%m/%d");
        if not os.path.exists("pastes/"+today):
            if not args.debug:
                os.makedirs("pastes/"+today)
        paste = pastes.get()
        fn = "pastes/%s/%s.txt" % (today, paste['key'])
        if os.path.exists(fn):
            if args.verbose:
                sys.stdout.write("[*] Skipping %s, already archived\n" % paste['key'])
            continue
        try:
            #html = requests.get("http://pastebin.com/raw.php?i=" + paste, timeout=1)
            html = requests.get("https://scrape.pastebin.com/api_scrape_item.php?i=" + paste['key'], timeout=1)
        except requests.Timeout as err:
            html.status_code = 408
        except:
            html.status_code = 999
        if html.status_code is not 200:
            sys.stdout.write("[!] Download error\n")
            sys.stdout.write("[!] HTTP: " + str(html.status_code) + "\n")
            # don't download permenant errors
            if html.status_code not in [404,999]:
                # replace the paste if we haven't downloaded it
                print "[*] Requeuing %s..." % paste['key']
                pastes.put(paste)
                # make sure the error delay is reasonable
                time.sleep(delay * 12)
            continue
        if "requesting a little bit too much" in html.text:
            print "[*] Requeuing %s..." % paste['key']
            pastes.put(paste)
            print "[*] Throttling..."
            time.sleep(0.1)
        else:
            if not args.debug:
                f = open(fn, "wt")
                f.write(html.text.encode(html.encoding))
                f.close()
        sys.stdout.write("Downloaded %s" % paste['key'])
        if args.verbose:
            sys.stdout.write(", waiting %f sec" % delay)
        sys.stdout.write("\n")
        time.sleep(delay)
        pastes.task_done()

def scraper():
    global app_running
    # we should wait a bit between fetches so pastebin doesn't block us
    delay = 35
    html = None
    while app_running:
        if args.verbose:
            print ("[*] Fetching...")
        try:
            #html = requests.get("http://www.pastebin.com", timeout=1)
            html = requests.get("https://scrape.pastebin.com/api_scraping.php", timeout=2)
        except requests.Timeout as err:
            if not html:
                html = requests.Response
            if args.verbose:
                print ("[*] Bad response. Forcing 408...")
            html.status_code = 408
        except:
            html.status_code = 999
        if html.status_code is not 200:
            sys.stdout.write("[!] Fetch error\n")
            sys.stdout.write("[!] HTTP: " + str(html.status_code) + "\n")
            time.sleep(delay)
            continue
        if html:
            try:
                for paste in html.json():
                    if paste['key'] in pastesseen:
                        if args.verbose:
                            sys.stdout.write("%s already seen\n" % paste['key'])
                    else:
                        pastes.put(paste)
                        pastesseen.add(paste['key'])
                        if max_seen > 0 and len(pastesseen) > max_seen:
                            pastesseen.pop()
                        if args.verbose:
                            sys.stdout.write("%s queued for download\n" % paste['key'])
            except:
                sys.stdout.write("[!] Unable to fetch %s\n" % paste['key'])
        time.sleep(delay)

############################################################
# Parse options

parser = argparse.ArgumentParser(description='Scrape pastes from pastebin.com using the pastebin API')
parser.add_argument('-d', dest='debug', action='store_true', help='enable debug mode')
parser.add_argument('-v', dest='verbose', action='store_true', help='enable verbose output')
args = parser.parse_args()

############################################################
# Main App

print "[*] Starting Pastebin Scraper..."
print "[*] PID: " + str(os.getpid())
if args.debug:
    print "[*] DEBUG MODE"

global app_running
app_running = True

for i in range(num_workers):
    t = threading.Thread(target=downloader)
    t.setDaemon(True)
    t.start()

if not os.path.exists("pastes"):
    if not args.debug:
        os.mkdir("pastes")

s = threading.Thread(target=scraper)
s.start()

while True:
    try:
        s.join(1)
    except KeyboardInterrupt:
        print "Terminating..."
        app_running = False
        sys.exit(1)
    time.sleep(1)

