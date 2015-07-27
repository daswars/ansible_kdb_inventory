# Ansible KeePass inventory script
Quick & dirty (just a sysadmin ;) ) Ansible inventory script to read KeePass 2.x (v4) files.

Reads environment variables "KDB_PATH" and "KDB_PASS" to open KeePass file and export JSON inventory for Ansible.

## Details
- Entries are mapped to hosts. "Title" -> hostname
- "Titles" with spaces and empty values are ignored
- Entries named "group_vars" can contain values that are mapped to Ansible "host_vars". So group_names don't have to be unique 
- tags are mapped to virtual groups

