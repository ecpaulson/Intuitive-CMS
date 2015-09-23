echo Defaults:root \!requiretty >> /etc/sudoers

container_commands:
 01-run-ES:
  command: "sudo /usr/local/elasticsearch/elasticsearch-1.7.2/bin/elasticsearch"
