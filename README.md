# Ansible KeePass inventory script
Quick & dirty (just a sysadmin ;) ) Ansible inventory script to read KeePass 2.x (v4) files.

Reads environment variables "KDB_PATH" and "KDB_PASS" to open KeePass file and export JSON inventory for Ansible.

## Limitations
group_vars for non unique group names are not treated

