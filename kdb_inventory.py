#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import libkeepass
import os
import json
#import xml.etree.cElementTree as ET
import lxml.etree as ET
    
def kdb_inventory():
  filename = os.environ["KDB_PATH"]
  credentials = { 'password' : os.environ["KDB_PASS"] }
  hosts_info = {}
  inventory = {}
  inventory_vars = {}
  with libkeepass.open(filename, **credentials) as kdb:
    xmldata = ET.fromstring(kdb.pretty_print())
    for group in xmldata.findall(".//Group"):
      group_name = str(group.find("./Name").text)
      group_name = group_name.lower()
      for parent in group:
        parents = {
          dept.find('Name').text
          for dept in parent.xpath('ancestor::Group')        
        }
      group_vars = []
      hosts = []
      for entry in group.findall("./Entry"):
        vars = {}
        hostname = ""
        for string in entry.findall("./String"):
          host_entry = string.find("[Key='Title']")
          if host_entry is not None:
            host = string.find("./Value")
            hostname = str(host.text).lower()
            if hostname in hosts:
              break
            if hostname != "group_vars":
              hosts.append(hostname)
          key = string.find("./Key")
          key = str(key.text).lower()
          value = string.findtext("./Value")
          if value and value != hostname and key != "title":
            vars[key] = str(value)
        if hostname == "group_vars":
          group_vars = vars
          try:
            inventory[group_name]["vars"] = group_vars
          except KeyError:
            inventory[group_name] = {}
            inventory[group_name]["vars"] = group_vars
        elif hostname and ' ' not in hostname:
          hosts_info[hostname] = vars
        if hostname and hostname != "group_vars" and ' ' not in hostname:
          for actual_group in parents:
            actual_group = actual_group.lower()
            try:
              if hostname not in inventory[actual_group]["hosts"]:
                inventory[actual_group]["hosts"].append(hostname)
            except KeyError:
              try:
                inventory[actual_group]["hosts"] = [hostname]
              except KeyError:              
                inventory[actual_group] = {}
                inventory[actual_group]["hosts"] = [hostname]
            inventory[actual_group]["hosts"].sort()
  inventory_vars["hostvars"] = hosts_info
  inventory["_meta"] = inventory_vars
  print json.dumps(inventory, indent=2, sort_keys=True)

if __name__ == '__main__':
  try:
    os.environ["KDB_PATH"]
  except KeyError:
    print "{}"
    sys.exit(0)
  if len(sys.argv) == 2 and (sys.argv[1] == '--list'):
    kdb_inventory()
  elif len(sys.argv) == 3 and (sys.argv[1] == '--host'):
    kdb_inventory()
  else:
    print "Usage: %s --list or --host <hostname>" % sys.argv[0]
    sys.exit(1)
