\set pswrd `echo "$POSTGRES_PASSWORD"`

CREATE USER bhtom WITH PASSWORD :'pswrd';
ALTER USER bhtom CREATEDB;

CREATE DATABASE bhtom;
GRANT ALL PRIVILEGES ON DATABASE bhtom TO bhtom;

CREATE DATABASE bhtom_test;
GRANT ALL PRIVILEGES ON DATABASE bhtom_test TO bhtom;