#!/usr/bin/env python3

import shutil
import subprocess
import os
import time
from urllib.parse import urlparse

HomeDir = os.path.expanduser('~')

if not os.path.exists(os.path.expanduser('~/Documents')):
    raise Exception("Documents not exist.")

PrivateNucleiDir = os.path.expanduser('~/Documents/PrivateNuclei/')

if not os.path.exists(PrivateNucleiDir):
    raise Exception("Private Nuclei not exist")

Params = ['return_to','redirect','checkout_url','continue','dest',
          'destination','go','image_url','redir','redirect_uri','redirect_url',
          'return_path','return','returnTo','rurl','url','view']
Pattern = "|".join(Params)

RedirectNuclei = PrivateNucleiDir + "OpenRedirect" 

if not os.path.exists(RedirectNuclei):
    raise Exception("Redirect Nuclei not exist")

files = [
    'redirect_recon.txt',
    'subs.txt',
    'alive.txt',
    'waybackurls.txt',
    'params.txt',
    'JSCrawl.txt'
]

class Recon:
    def __init__(self, url: str):
        if not url.strip():
            raise Exception(
                "Missing url, please set your url you want to recon.")

        self.url = url

        if os.path.exists('redirect_recon.txt') or os.path.exists('subs.txt') or os.path.exists('alive.txt') or os.path.exists('waybackurls.txt') or os.path.exists('params.txt') or os.path.exists('JSCrawl.txt'):
            choose = input("Do you want delete old files? [Y/N]: ")
            if choose.lower() == "y":
                for f in files:
                    if os.path.exists(f):
                        os.remove(f)
                        print(f"Deleted {f}")
            else:
                print("Ok")
                
                
    def isInstalled(self, name: str):
        return shutil.which(name)

    def subdomains(self, url: str):
        if not self.isInstalled("subfinder"):
            raise Exception("Missing subfinder, please install subfinder.")

        if not self.isInstalled("httpx"):
            raise Exception("Missing httpx, please install httpx")

        domain = urlparse(url).netloc
        fix = None

        if not domain:
            fix = domain
        else:
            remove_subs = domain.split('.')[-2:]
            fix = ".".join(remove_subs)

        if os.path.exists("subs.txt"):
            os.remove("subs.txt")
        elif os.path.exists('alive.txt'):
            os.remove('alive.txt')

        print("Started subfinder for search domain that are alive")

        subs = subprocess.run(
            ['subfinder', '-d' , f'{fix}', '-o' ,'subs.txt'], capture_output=True, text=True)
        
        if subs.returncode != 0:
            print("Skipping. Failed getting any subs that found.")
            print("Err : " + subs.stderr)
            return

        if os.path.exists('subs.txt') and os.path.getsize('subs.txt') == 0:
            print("Didn't found any subs.")
            os.remove('subs.txt')
            return

        print("Subs saved, checking any alive.")

        alive = subprocess.run(['httpx', '-l', 'subs.txt', '-o', 'alive.txt'], capture_output=True,
                               text=True)
        if alive.returncode != 0:
            print("Skipping. Failed getting subs alive.")
            print("Err : " + alive.stderr)
            return

        if len(alive.stdout) == 0:
            print("Not found any alive domain.")
            os.remove('alive.txt')
            return

        print("subs that alive saved.")

    def waybackurls(self, url: str):
        if not self.isInstalled("waybackurls"):
            raise Exception("Missing waybackurls, please install waybackurls")

        print("Started waybackurls")

        result = subprocess.run(['waybackurls', url], capture_output=True, text=True)
        if result.returncode != 0:
            print("Skipping. Failed getting waybackurls")
            print("Err : " + result.stderr)
            return

        if len(result.stdout) != 0 and url in result.stdout:
            with open("waybackurls.txt", "w") as f:
                f.write(result.stdout)

            print("Waybackurls file saved.")
        else:
            print("Not found any results from waybackurls, could've API failed?")
            return

        result2 = subprocess.run(['grep', '-E' , Pattern, 'waybackurls.txt'], capture_output=True, text=True)
        if result2.returncode == 2:
            print("Skipping. Failed getting waybackurls patterns")
            print("Err : " + result2.stderr)
            return

        if len(result2.stdout) != 0:
            print("Params file saved.")
            
            with open("params.txt", "w") as f:
                f.write(result.stdout)
        else:
            print("Not found Any Params that exist.")

    def redirect_recon(self, url: str):
        if not self.isInstalled("nuclei"):
            raise Exception("Missing Nuclei, please installl nuclei")
        
        if os.path.exists("redirect_recon.txt"):
            os.remove("redirect_recon.txt")

        print("Started redirect_recon on website checking if there any open redirect.")

        result = subprocess.run(['nuclei', '--target', url, '-t', RedirectNuclei, '-o', 'redirect_recon.txt'], text=True, capture_output=True)
        if result.returncode != 0:
            print("Skipping. Failed to scan on website about open redirect.")
            print("Err : " + result.stderr)
            return

        if os.path.exists('redirect_recon.txt') and os.path.getsize('redirect_recon.txt') == 0:
            print("Didn't found redirect open.")
            os.remove('redirect_recon.txt')
        else:
            print("Found redirect open, check on file redirect_recon")

    def JSFinder(self, url: str):
        if not self.isInstalled("katana"):
            raise Exception("Missing katana, please install katana")

        print("Started JSFinder crawl.")

        found = 0
        result = subprocess.Popen(['katana', '-u', url , '-jc', '-retry' , '5', '-d', '5' ,'-o', 'JSCrawl.txt'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        output, err = result.communicate()
        
        if result.returncode != 0:
            print("Skipping. Failed to crawl to website.")
            print("Err : " + err)
            return

        while result.poll() is None:
            if os.path.exists("JSCrawl.txt"):
                with open("JSCrawl.txt", "r") as f:
                    found = len(f.readlines())

            if found != 0:
                print(f"Found ({found}), Still crawling.")
            else:
                print("Still crawling.")

            time.sleep(3)
        
        result.wait()

        
        if os.path.exists("JSCrawl.txt") and os.path.getsize("JSCrawl.txt") == 0:
            print('JSCrawl finished. JS files found.')
        else:
            print("JSCrawl finished. JS files not found.")
        

    def Start(self):
        self.subdomains(self.url)
        self.waybackurls(self.url)
        self.redirect_recon(self.url)
        self.JSFinder(self.url)

if __name__ == "__main__":
    url = input("Enter Url for use the tool: ")
    Init = Recon(url).Start()

