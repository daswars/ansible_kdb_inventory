#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import libkeepass
import os
import json
import lxml.etree as ET
from string import maketrans

def kdb_inventory():
  filename = os.environ["KDB_PATH"]
  credentials = { 'password' : os.environ["KDB_PASS"] }
  hosts = {}
  inventory = {}
  inventory_vars = {}
  with libkeepass.open(filename, **credentials) as kdb:
    xmldata = ET.fromstring(kdb.pretty_print())
    for history in xmldata.xpath(".//History"):
      history.getparent().remove(history)      
    for entry in xmldata.findall(".//Entry"):
      hostvars = {}
      hostname = None
      for string in entry.findall("./String"):
        key   = string.findtext("./Key").lower()
        value = string.findtext("./Value")
        if key == 'title' and ' ' not in value and value != 'group_vars':
          hostname = value.lower()
        if value and key != "title":
          hostvars[key] = value
      if hostname and hostname != "group_vars" and ' ' not in hostname:
        for ancestor in entry.iterancestors("Group"):
          try:
            for aentry in ancestor.find("./Entry/String[Key='Title'][Value='group_vars']"):              
              aentry = aentry.getparent().getparent()
              for astring in aentry.findall("./String"):
                avalue = astring.findtext("./Value")
                if not avalue:
                  continue
                akey = astring.findtext("./Key").lower()
                if not hostvars.has_key(akey) and akey != "title":
                  hostvars[akey] = avalue
          except TypeError:
            continue
        groups = {
          group.find('Name')
          for group in entry.xpath('ancestor::Group')
        }
        for group in groups:
          group = group.text.lower()
          try:
            inventory[group]["hosts"].append(hostname)
          except KeyError:
            inventory[group] = {}
            inventory[group]["hosts"] = [hostname]
        tags = entry.findtext("./Tags").split(';')
        for tag in tags:
          if tag:
            tag = tag.translate(maketrans('=','_'))
            tag = "tag_" + tag
            try:
              inventory[tag]["hosts"].append(hostname)
            except KeyError:
              inventory[tag] = {}
              inventory[tag]["hosts"] = [hostname]
      if hostname:
        hosts[hostname] = hostvars
      inventory_vars["hostvars"] = hosts
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
