#!/bin/sh
echo Defaults:root \!requiretty >> /etc/sudoers
cd /usr/local/elasticsearch/elasticsearch-1.7.2
sudo ./bin/elasticsearch -d
