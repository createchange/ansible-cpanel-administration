#! /usr/bin/env python2

import os, errno, subprocess, urllib

'''
Verify specific logs (/var/log/rkhunter/rkhunter.log and /var/log/yum.log) as the authoritative logs. Do they get cycled out in a manner which would break this?
Consider returning ALL entries of binary in the log file, in order to not get old entries that don't align with rkhunter date of alert.
'''

def get_changed_files():
        '''
        Searches through rkhunter.log to find changed files. Separates these files into two lists.
        returns: cpanel_files_changed, system_files_changed
        '''
        cpanel_files_changed = []
        system_files_changed = []
        with open('/var/log/rkhunter/rkhunter.log','r') as f:
                data = f.read().split("\n")
                for line in data:
                        if "File:" in line:
                                if "/usr/local/cpanel/" in line:
                                        cpanel_files_changed.append(line.split(": ")[1])
                                if "/usr/bin/" in line or "/usr/sbin/" in line:
                                        system_files_changed.append(line.split(": ")[1])
        return cpanel_files_changed, system_files_changed

def system_file_check(system_files_changed):
        '''
        Accepts list of binary paths which have changed. Crossreferences these binaries against the most recent yum.log to see if it spots
        that binary as having been updated.

        If updated, prints the binary name + the line in the yum.log that references it.
        If not found in yum log, prints binary name + error message.
        '''
        parent_binaries = []
        FNULL = open(os.devnull, 'w')
        for entry in system_files_changed:
                binary = str("'" + entry + "'")
                search_command = "repoquery --quiet --disablerepo=cpanel-plugins.repo --whatprovides " + binary + " --qf '%{NAME}'"
                x = subprocess.Popen(search_command, shell=True, stderr=FNULL, stdout=subprocess.PIPE)
                output = x.stdout.read().split('\n')
                for package in output:
                        if "Skipping" in package or package == "":
                                pass
                        else:
                                if package not in parent_binaries:
                                        parent_binaries.append(package)
        if parent_binaries:
                print("\nThe following SYSTEM binaries have changed:\n")
                with open('/var/log/yum.log', 'r') as f:
                        yum_log = f.read().split('\n')
                for binary in parent_binaries:
                        print("Binary: " + str(binary) + "\nyum.log entry: " +  str(yum_log_crossreference_result(binary, yum_log)) + "\n")


def yum_log_crossreference_result(binary, yum_log):
        '''
        Takes binary and yum_log (each line of log as entry in list) as input.
        Checks for occurrence of binary name in yum.log list.
        Returns to the affirmative or negative if the binary is found in the log.
        '''
        for line in yum_log:
                if binary in line:
                        return line

        return "ERROR: Not found in yum.log!"

def cpanel_file_check(cpanel_files_changed):
        with open('/usr/local/cpanel/version', 'r') as f:
                cp_version = f.read().strip('\n')
        print("Current WHM Version: %s" % cp_version)

        for cp_file in cpanel_files_changed:
                urllib.urlretrieve("http://httpupdate.cpanel.net/cpanelsync/%s/binaries/linux-c7-x86_64/bin/%s.xz" % (cp_version, cp_file), "/home/jonathanweaver/scripts/tmp/%s.xz" % cp_file)
                subprocess.call("xz -d /home/jonathanweaver/scripts/tmp/%s.xz" % cp_file, shell=True)

                existing = (str(subprocess.check_output("md5sum /usr/local/cpanel/bin/%s" % cp_file, shell=True)).split(" "))[0]
                source = (str(subprocess.check_output("md5sum /home/jonathanweaver/scripts/tmp/%s" % cp_file, shell=True)).split(" "))[0]
                print("Binary name: %s" % cp_file)
                print("Existing hash: %s" % existing)
                print("Source hash: %s" % source)
                if existing == source:
                        print("Result: OK\n")
                else:
                        print("Result: WARNING - hashes did not match.\n")

                try:
                        os.remove('/home/jonathanweaver/scripts/tmp/%s' % cp_file)
                except OSError:
                        pass


# Start of program
cpanel_files_changed, system_files_changed = get_changed_files()
if system_files_changed:
        system_file_check(system_files_changed)
if cpanel_files_changed:
        cpanel_file_check(cpanel_files_changed)
if not system_files_changed and not cpanel_files_changed:
        print("\nNo files changed.\n")
