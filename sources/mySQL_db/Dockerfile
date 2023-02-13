FROM mysql:latest
COPY ./card_transdata.csv ./var/lib/mysql-files
COPY ./DatabaseCreation.sql /docker-entrypoint-initdb.d/
