create tablespace flyway_tbs datafile '/oracle/app/oracle/oradata/DZZDSJDB/datafile/flyway01.dbf' size 50m autoextend on next 50m maxsize 30G;
create profile unlimited_profile limit
failed_login_attempts unlimited
password_life_time unlimited
password_reuse_time unlimited
password_reuse_max unlimited;
create user flyway identified by flyway default tablespace flyway_tbs  profile unlimited_profile;
grant connect to flyway;
grant resource to flyway;
grant unlimited tablespace to flyway;
