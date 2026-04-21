-- The MariaDB image only grants the app user access to MYSQL_DATABASE.
-- pytest-django needs to CREATE/DROP a separate test_catalog database,
-- which requires an explicit grant here. No Docker env var covers this.
GRANT ALL ON `test_catalog`.* TO 'catalog'@'%';
FLUSH PRIVILEGES;
