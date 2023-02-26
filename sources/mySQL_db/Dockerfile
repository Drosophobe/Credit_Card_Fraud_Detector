FROM mysql:latest
EXPOSE 3307
EXPOSE 33060
COPY ./card_transdata.csv ./var/lib/mysql-files
COPY ./DatabaseCreation_docker.sql /docker-entrypoint-initdb.d/
