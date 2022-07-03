#python3

"""

1. create target.txt
2. create wordlist.txt for common backup names.
3. run script. e.g. "python3 backupfinder.py"
 __                __                 ___ __           __             
|  |--.---.-.----.|  |--.--.--.-----.'  _|__|.-----.--|  |.-----.----.
|  _  |  _  |  __||    <|  |  |  _  |   _|  ||     |  _  ||  -__|   _|
|_____|___._|____||__|__|_____|   __|__| |__||__|__|_____||_____|__|  
                              |__|                                    

19.07.2019
@musana

"""


import threading
import requests
from sys import stdout
from urllib.parse import urlparse
from datetime import datetime

# until 17 line for debugging. After this section can be remove.
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

proxies = {
  'http': 'http://127.0.0.1:8080',
  'https': 'http://127.0.0.1:8080',
}

class backupFind(threading.Thread):
    possible_headers = ['application/gzip', 'application/vnd.rar', 'application/zip', 'application/octet-stream']
    extension        = ['.bz', '.bz2', '.gz', '.rar', '.sh', '.tar', '.zip', '.7z', '.bak', '.tar.gz', '.sql', '.tmp'
                        '.db', '.old', '.dmp', '.dump', '.bak', '.bk', '.sql_data', '.sql_dump']
    headers          = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "close",
                        "Upgrade-Insecure-Requests": "1", "Pragma": "no-cache", "Cache-Control": "no-cache"}

    def __init__(self, url, ext):
        threading.Thread.__init__(self)
        self.url = url if url[-1] == '/' else url+'/'
        self.ext = ext

    @classmethod
    def readWordlist(cls):
        with open('wordlist.txt', 'r') as bu:
            backup_wordlist = bu.read().splitlines()
            return backup_wordlist

    @classmethod
    def readUrlFromFile(cls):
        with open('targets.txt', 'r') as bu:
            url_list = bu.read().splitlines()
            return url_list

    @classmethod
    def createSubList(cls, subListCount):
        urlWithSubList = [backupFind.readUrlFromFile()[i:i + subListCount] \
                          for i in range(0, len(backupFind.readUrlFromFile()), subListCount)]
        return urlWithSubList

    def run(self):
        for word in backupFind.readWordlist():
            try:
                req = requests.head(self.url + word + self.ext, headers=backupFind.headers, verify=False)
                stdout.write("\r %s" % req.url)
                stdout.flush()
                resp_headers = req.headers['Content-Type'].lower()

                for header in backupFind.possible_headers:
                    if header == resp_headers or resp_headers.startswith('application/x'): # return only key
                        if 'plain' not in resp_headers:
                            stdout.write("\r")
                            result = "[+][TM] Backup Found! [URL:{}] [Content-Type: {}]".format(req.url, resp_headers)
                            print(result)
                            with open('backup_results.txt', 'a+') as br:
                                br.writelines(result+'\n')
                            stdout.flush()
                            break
            except Exception as e:
                pass

class heuristic(threading.Thread):
    def __init__(self, url, ext):
        threading.Thread.__init__(self)
        self.url = url if url[-1] == '/' else url+'/'
        self.ext = ext

    def heuristicMethod(self):
        heuristic    = list()
        domain       = urlparse(self.url).netloc
        withdash     = domain.replace('.', '-')
        withuscore   = domain.replace('.', '_')
        heuristic.extend((domain, withuscore, withdash))
        concat       = ""
        concatletter = ""

        # for each sub domain
        for part in domain.split('.'):
            concat += part
            heuristic.append(concat)

        # for each letter at whole domain
        for letter in domain:
            concatletter += letter
            heuristic.append(concatletter)

        return heuristic

    def run(self):
        for word in self.heuristicMethod():
            try:
                req = requests.head(self.url + word + self.ext, headers=backupFind.headers, verify=False)
                stdout.write("\r %s" % req.url)
                stdout.flush()
                resp_headers = req.headers['Content-Type']

                for header in backupFind.possible_headers:
                    if header == resp_headers.lower() or resp_headers.startswith('application/x'):  # return only key
                        stdout.write("\r")
                        result = "[+][HM] Backup Found! [URL:{}] [Content-Type: {}]".format(req.url, resp_headers)
                        print(result)
                        with open('backup_results.txt', 'a+') as br:
                            br.writelines(result + '\n')
                        stdout.flush()
                        break
            except Exception as e:
                pass

if __name__ == '__main__':
    for url in backupFind.readUrlFromFile():
        for ext in backupFind.extension:
            heuristicmethod = heuristic(url, ext)
            traditionalmtd  = backupFind(url, ext)
            traditionalmtd.start()
            heuristicmethod.start()
