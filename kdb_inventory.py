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
  vgroups = ['product', 'stage', 'tier', 'type']
  hosts = {}
  inventory = {}
  inventory_vars = {}
  with libkeepass.open(filename, **credentials) as kdb:
    xmldata = ET.fromstring(kdb.pretty_print())
    for history in xmldata.xpath(".//History"):
      history.getparent().remove(history)
    for group in xmldata.findall(".//Group"):
      group_name = group.find("./Name").text.lower()
      group_uuid = group.find("./UUID").text
      group_name_uuid = group_name + "_" + group_uuid
      inventory[group_name_uuid] = {}
      subgroups = []
      for subgroup in group.findall("./Group"):
        subgroup_name = subgroup.find("./Name").text.lower()
        subgroup_uuid = subgroup.find("./UUID").text
        subgroup_name_uuid = subgroup_name + "_" + subgroup_uuid
        subgroups.append(subgroup_name_uuid)
      if subgroups:
        inventory[group_name_uuid]["children"] = subgroups
      for entry in group.findall("./Entry"):
        hostvars = {}
        hostname = None
        for string in entry.findall("./String"):
          key   = string.findtext("./Key").lower()
          value = string.findtext("./Value")
          if key == 'title' and ' ' not in value:
            hostname = value.lower()
          if value and key != "title":
            hostvars[key] = value
        if hostname and hostname != "group_vars" and ' ' not in hostname:
          try:
            inventory[group_name_uuid]["hosts"].append(hostname)
          except KeyError:
            inventory[group_name_uuid]["hosts"] = [hostname]
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
          for vgroup in vgroups:
            if vgroup in hostvars:
              vgroup = hostvars[vgroup]
              try:
                inventory[vgroup]["hosts"].append(hostname)
              except KeyError:
                inventory[vgroup] = {}
                inventory[vgroup]["hosts"] = [hostname]
          tags = entry.findtext("./Tags").split(';')
          for tag in tags:
            if tag:
              tag = tag.translate(maketrans('=','_'))
              try:
                inventory[tag]["hosts"].append(hostname)
              except KeyError:
                inventory[tag] = {}
                inventory[tag]["hosts"] = [hostname]
        if hostname and hostname != "group_vars":
          hosts[hostname] = hostvars
        if hostname == "group_vars":
          try:
            inventory[group_name_uuid]["vars"] = hostvars
          except KeyError:
            inventory[group_name_uuid] = {}
            inventory[group_name_uuid]["vars"] = hostvars
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
