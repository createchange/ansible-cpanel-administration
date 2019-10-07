#!/usr/bin/env python3

'''
If requested, grabs domains from 3 cpanel servers. Allows for searching of domain
to see which server that account resides on.
'''

import subprocess
import glob, os

home = str(os.environ['HOME'])
os.chdir(home + "/cpanel-ansible/")
update_cache = input("Would you like to update the cache? (y/n)\n> ")
if update_cache == "y":
    subprocess.call("ansible-playbook playbooks/fetch-userdomains.yml --ask-become-pass", shell=True)

search_param = input("\nPlease enter your search parameters:\n> ")
print("")

os.chdir(home + "/cpanel-ansible/output/userdomains/")
for file in glob.glob("*"):
    with open(file, "r") as f:
        file_name = file[12:20]
        file_contents = f.read()
        file_contents = file_contents.split("\n")
        for line in file_contents:
            if search_param in line:
                print("%s: %s" % (file_name, line.split(":")[0]))

