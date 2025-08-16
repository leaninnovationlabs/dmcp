# How To Prepare Test Data for DB MCP

# Postgres

## Setup Test Database

- Install Docker Desktop if you don’t have it yet.
- Install Postgres client using brew if you don’t have it yet so you get `psql` tool installed.
- Decide on the folder where you want to setup the test Postgres DB
- Goto the folder
    
    ```jsx
    $ cd postgres
    ```
    
- Create docker-compose.yml with below content. Make sure you update <username> and <password> to match your username and password.

```jsx
services:
  pgdb:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: <username>
      POSTGRES_PASSWORD: <password>
      POSTGRES_DB: dbmcptest
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

- Run `docker-compose up -d` to create the docker container with Postgres DB on it.
- Run `docker ps` command to verify container is created. It should like below.

```jsx
$ docker ps | egrep 'CONTAINER|postgre'
CONTAINER ID   IMAGE         COMMAND                  CREATED       STATUS       PORTS                                         NAMES
db1718ffab85   postgres:15   "docker-entrypoint.s…"   7 hours ago   Up 7 hours   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   postgres-pgdb-1
```

- Create pg.env file with environment variables to connect to Postgres

```jsx
$ cat pg.env
export PGHOST=localhost
export PGPORT=5432
export PGUSER=<username>
export PGDATABASE=pgbench
```

- Verify your connectivity to Postgres DB using `psql` . It should look like below.

```jsx
$ psql
psql (14.13 (Homebrew))
Type "help" for help.

pgbench=# \l
                         List of databases
   Name    | Owner | Encoding | Collate | Ctype | Access privileges 
-----------+-------+----------+---------+-------+-------------------
 dnom      | aags  | UTF8     | C       | C     | 
 dnom2     | aags  | UTF8     | C       | C     | 
 pgbench   | aags  | UTF8     | C       | C     | 
 postgres  | aags  | UTF8     | C       | C     | 
 template0 | aags  | UTF8     | C       | C     | =c/aags          +
           |       |          |         |       | aags=CTc/aags
 template1 | aags  | UTF8     | C       | C     | =c/aags          +
           |       |          |         |       | aags=CTc/aags
(6 rows)

```

## Prepare Test Data

Pagila is a sample database for PostgreSQL, designed to simulate a DVD rental store. It is a PostgreSQL port of the Sakila sample database originally created for MySQL.

- Download Pagila

```jsx
git clone https://github.com/devrimgunduz/pagila.git
```

This command creates a new directory named `pagila` in your current location, containing all the necessary files.

- Create a PostgreSQL Database.

Next, you need to create a new database in PostgreSQL for the Pagila schema and data. 

```jsx
$ psql
psql (14.13 (Homebrew))
Type "help" for help.

# create database pagila;
CREATE DATABASE
# \c pagila
You are now connected to database "pagila" as user "sreedhar".
pagila=# 
```

- Load the Schema and Data

```jsx
$ cd pagila
$ export PGDATABASE=pagila
$ psql -f pagila-schema.sql
$ psql -f pagila-data.sql
```

The first command loads the **schema**, which defines the tables, columns, and relationships. The second command populates those tables with sample data.

- Verify that the setup was successful using `psql`

```jsx
$ psql
psql (14.13 (Homebrew))
Type "help" for help.

pagila=# SELECT count(*) FROM film;
 count 
-------
  1000
(1 row)
pagila=# \dt
                    List of relations
 Schema |       Name       |       Type        |  Owner   
--------+------------------+-------------------+----------
 public | actor            | table             | sreedhar
 public | address          | table             | sreedhar
 public | category         | table             | sreedhar
 public | city             | table             | sreedhar
 public | country          | table             | sreedhar
 public | customer         | table             | sreedhar
 public | film             | table             | sreedhar
 public | film_actor       | table             | sreedhar
 public | film_category    | table             | sreedhar
 public | inventory        | table             | sreedhar
 public | language         | table             | sreedhar
 public | payment          | partitioned table | sreedhar
 public | payment_p2022_01 | table             | sreedhar
 public | payment_p2022_02 | table             | sreedhar
 public | payment_p2022_03 | table             | sreedhar
 public | payment_p2022_04 | table             | sreedhar
 public | payment_p2022_05 | table             | sreedhar
 public | payment_p2022_06 | table             | sreedhar
 public | payment_p2022_07 | table             | sreedhar
 public | rental           | table             | sreedhar
 public | staff            | table             | sreedhar
 public | store            | table             | sreedhar
(22 rows)
```

# MySQL

## Setup Test Database

- Install Docker Desktop if you don’t have it yet.
- Install MySQL client using brew if you don’t have it yet so you get `mysql` tool installed.
- Decide on the folder where you want to setup the test Postgres DB
- Goto the folder
    
    ```jsx
    $ cd mysql
    ```
    
- Create docker-compose.yml with below content. Make sure you update <username> and <password> to match your username and password.

```jsx
services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: <password>
      MYSQL_DATABASE: dbmcptest
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql

volumes:
  mysql-data:
```

- Run `docker-compose up -d` to create the docker container with Postgres DB on it.
- Run `docker ps` command to verify container is created. It should like below.

```jsx
$ docker ps | egrep 'CONTAINER|mysql'
CONTAINER ID   IMAGE         COMMAND                  CREATED       STATUS       PORTS                                         NAMES
61fb19a58dcc   mysql:8.0     "docker-entrypoint.s…"   6 hours ago   Up 6 hours   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   mysql-db-1
```

- Verify the connectivity using `mysql` client tool. It should look like below:

```jsx
$ mysql -h 127.0.0.1 -P 3306 -u root -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 10
Server version: 8.0.43 MySQL Community Server - GPL

Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| dbmcptest          |
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.01 sec)

```

## Prepare Test Data

- Download sakila test scripts and data

```jsx
$ git clone https://github.com/datacharmer/test_db
```

- Change directory to the repo folder

```jsx
$ cd test_db
```

- Load the data from `employees.sql` using `mysql` client

```jsx
$ mysql -h 127.0.0.1 -P 3306 -u root -p < employees.sql 
Enter password: 
INFO
CREATING DATABASE STRUCTURE
INFO
storage engine: InnoDB
INFO
LOADING departments
INFO
LOADING employees
INFO
LOADING dept_emp
INFO
LOADING dept_manager
INFO
LOADING titles
INFO
LOADING salaries
data_load_time_diff
00:00:18
```

- Verify the data

```jsx
$ mysql -h 127.0.0.1 -P 3306 -u root -p 
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 13
Server version: 8.0.43 MySQL Community Server - GPL

Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> connect employees;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Connection id:    16
Current database: employees

mysql> select count(*) from employees;
+----------+
| count(*) |
+----------+
|   300024 |
+----------+
1 row in set (0.03 sec)

mysql> select count(*) from departments;
+----------+
| count(*) |
+----------+
|        9 |
+----------+
1 row in set (0.01 sec)

mysql> select count(*) from dept_emp;
+----------+
| count(*) |
+----------+
|   331603 |
+----------+
1 row in set (0.05 sec)
```