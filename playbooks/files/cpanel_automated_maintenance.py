#! /usr/bin/env python2

# Must be run as root to work
# Can be run with ansible "become" command?

import subprocess

def check_disk_space():
    diskspace = subprocess.Popen("df -h", shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
    diskspace = diskspace.split('\n')
    warnings = False
    for line in diskspace:
        if '%' in line:
            if '\'' in line:
                pass
            else:
                if True:
                    items = line.split()
                    try:
                        if int(items[4].strip('%')) > 70:
                            print(line + " ----- DISK SPACE ALERT!")
                            warnings = True
                        else:
                            pass
                    except:
                        pass
    if warnings == False:
        print("No warnings")

def check_backups():
    backups = subprocess.Popen('grep "Final state" /usr/local/cpanel/logs/cpbackup/*', shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
    backups = str(backups).split('\n')
    warnings = False
    for line in backups:
        if "Backup" in line:
            if "Failure" in line:
                warnings = True
    if warnings == True:
        for line in backups:
            if "Backup" in line:
                print(line)
    else:
        print("All backups successful")

def check_mail_delivery():
    # Pre-emptively prune messages
    subprocess.Popen("/usr/sbin/exim -bpr | grep '<>' | awk {'print $3'} | xargs /usr/sbin/exim -Mrm", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    mailcheck = subprocess.Popen("exim -bpc", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip()
    print("There are %s messages in the queue\n") % mailcheck

print("\nDisk Space Alerts:")
check_disk_space()

print("\nBackup History:")
check_backups()

print("\nMail Queue Count:")
check_mail_delivery()
