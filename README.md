# Ansible KeePass inventory script
Quick & dirty (just a sysadmin ;) ) Ansible inventory script to read KeePass 2.x (v4) files.

Reads environment variables "KDB_PATH" and "KDB_PASS" to open KeePass file and export JSON inventory for Ansible.

## Details
- Entries are mapped to hosts. "Title" -> hostname.
- "Titles" with spaces and empty values are ignored.
- Entries named "group_vars" can contain values that are mapped to Ansible "host_vars" in the same branch. So group_names don't have to be unique in the whole tree.
- tags are mapped to groups (tag_tagname). '=' is replaced by '_'.

