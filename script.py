#!/usr/bin/env python3

import requests
import sys
import queue
from bs4 import BeautifulSoup

BASE_URL = "https://codeforces.com/api/user.status"

def get_input():
  if len(sys.argv) < 3:
    print("handle and/or path to save file not provided!")
    print("info: ./app.py <handle> <path-to-directory>")
    sys.exit()
  global PARAMS
  PARAMS = {
    "handle": sys.argv[1],
    "from": 1,
    "count": 10000
  }
  global BASE_PATH
  BASE_PATH = sys.argv[2]
  if BASE_PATH[-1:] != '/':
    BASE_PATH += '/'

def download_data():
  res = requests.get(url = BASE_URL, params = PARAMS)
  global data
  data = res.json()

def prepare_queue():
  global q
  q = queue.LifoQueue(maxsize = PARAMS["count"])
  for sub in data["result"]:
    if sub["verdict"] == "OK":
      q.put({
        "id": sub["id"],
        "contest": sub["contestId"],
        "index": sub["problem"]["index"],
        "lang": sub["programmingLanguage"]
      })

def download_submissions():
  while not q.empty():
    i = q.get()
    download_code(i)
    print("downloaded:", i)

def download_code(sub):
  URL = "https://codeforces.com/contest/{}/submission/{}".format(sub["contest"], sub["id"])
  code = requests.get(url = URL)
  code = get_code(code.content)
  save_code(code, sub)
  
def get_code(html):
  soup = BeautifulSoup(html, "html5lib")
  code = soup.find("pre", attrs = {"id":"program-source-text"})
  return code.text

def save_code(code, meta):
  path = BASE_PATH + str(meta["contest"]) + meta["index"]
  path = path + get_extension(meta["lang"])
  f = open(path, "w")
  f.write(code)
  print("written file:", path)
  f.close()

def get_extension(lang):
  lang = lang.lower()
  if "java" in lang:
    return ".java"
  elif "c++" in lang:
    return ".cpp"
  elif "go" in lang:
    return ".go"
  elif "kotlin" in lang:
    return ".kt"
  elif "python" in lang:
    return ".py"
  elif "rust" in lang:
    return ".rs"
  elif "c#" in lang:
    return ".cs"
  else:
    return ""

get_input()
download_data()
prepare_queue()
download_submissions()