# python-elastic-index-cleaner

##### This script allows you to clean up elastic search indexes older than a specified number of days. Install it on the desired machine and hang up the task in cron to run it daily. Then it will automatically work and you can forget about outdated indexes.
##### Replace the following variable values with yours in the dockerfile and try to assemble the container. You can always get the log that the docker container gives and find out if something went wrong.
#### ENV ELASTIC_HOST='https://your_elastic_host:9200'
#### ENV ELASTIC_USERNAME='your_elastic_username'
#### ENV ELASTIC_PASSWORD='your_elastic_password'
#### ENV AMOUNT_OF_DAYS_PROD='number of days e.g. 30 (only number)'
#### ENV AMOUNT_OF_DAYS_MORE='number of days e.g. 15 (only number)'
