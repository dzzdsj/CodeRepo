#!/bin/bash

#set -eu
#  set -xv

SCHEMA='DZZDSJ'

CURRENT_PATH=$(pwd)
BASE_DIR=$(dirname "$CURRENT_PATH")
SCRIPT_DIR="$BASE_DIR/script"
TMP_DIR="$BASE_DIR/tmp"
LOG_DIR="$BASE_DIR/log"
STAT_DIR="$BASE_DIR/stat"
CONFIG_DIR="$BASE_DIR/config"
TABLE_BASE_INFO_DIR="$CONFIG_DIR/table_base_info"
INDEX_BASE_INFO_DIR="$CONFIG_DIR/index_base_info"
PRIMARY_KEY_BASE_INFO_DIR="$CONFIG_DIR/primary_key_base_info"
TABLE_DDL_DIR="$CONFIG_DIR/table_ddl"
INDEX_DDL_DIR="$CONFIG_DIR/index_ddl"
PRIMARY_KEY_DDL_DIR="$CONFIG_DIR/primary_key_ddl"


TABLE_LIST_FILE="$CONFIG_DIR/table_list.txt"

get_table_list(){
    echo "$(date +"%Y-%m-%d %H:%M:%S")|Getting table list from $SCHEMA"
    sqlplus -S sys/sys as sysdba <<EOF
    set pagesize 0  feedback off heading off echo off
    spool $TABLE_LIST_FILE
    SELECT table_name FROM all_tables WHERE owner = '$SCHEMA' ORDER BY table_name;
    spool off
    quit
EOF
}

init_dir(){
    mkdir -p ${SCRIPT_DIR}
    mkdir -p ${CONFIG_DIR}
    mkdir -p ${TMP_DIR}
    mkdir -p ${LOG_DIR}
    mkdir -p ${STAT_DIR}
    mkdir -p ${TABLE_BASE_INFO_DIR}
    mkdir -p ${INDEX_BASE_INFO_DIR}
    mkdir -p ${PRIMARY_KEY_BASE_INFO_DIR}
    mkdir -p ${TABLE_DDL_DIR}
    mkdir -p ${INDEX_DDL_DIR}
    mkdir -p ${PRIMARY_KEY_DDL_DIR} 
}


get_column_base_info(){
    table_list=$(cat $TABLE_LIST_FILE)
    for table_name in $table_list
    do
    echo "$(date +"%Y-%m-%d %H:%M:%S")|Getting column base info for table: $table_name"
    sqlplus -S sys/sys as sysdba <<EOF
    set pagesize 0  
    set feedback off 
    set heading off 
    set echo off
    spool $TABLE_BASE_INFO_DIR/$table_name.txt
    SELECT  column_name||','||data_type||','||data_length||','||data_precision||','||data_scale||','||nullable||','||column_id  FROM  all_tab_columns WHERE  table_name = '$table_name' and owner = '$SCHEMA' ORDER BY column_id;
    spool off
    quit
EOF
    done
}

get_table_ddl(){
    table_list=$(cat $TABLE_LIST_FILE)
    for table_name in $table_list
    do
        echo "$(date +"%Y-%m-%d %H:%M:%S")|Getting table ddl for table: $table_name"
        local column_num=$(cat $TABLE_BASE_INFO_DIR/$table_name.txt | wc -l)
        awk -F "," -v column_num="$column_num" 'BEGIN{print "CREATE TABLE '$SCHEMA'.'$table_name'(" > "'$TABLE_DDL_DIR'/'$table_name'.sql"}{
        column_name = $1;
        data_type = $2;
        data_length = $3;
        data_precision = $4;
        data_scale = $5;
        nullable = $6;
        column_id = $7;
        body = "";
        if(data_type == "VARCHAR2"){
            body = column_name" "data_type"("data_length")";
        }
        if(data_type == "CHAR"){
            body = column_name" "data_type"("data_length")";
        }
        if(data_type == "DATE"){
            body = column_name" "data_type;
        }
        if(data_type == "NUMBER"){
            body = column_name" "data_type"("data_precision","data_scale")";
        }
        if(nullable == "N"){
            body = body" NOT NULL";
        }
        if(NR < column_num){
            body = body",";
        }
        print body >> "'$TABLE_DDL_DIR'/'$table_name'.sql";
        }END{print ");" >> "'$TABLE_DDL_DIR'/'$table_name'.sql"}' $TABLE_BASE_INFO_DIR/$table_name.txt 
    done
}
get_index_base_info(){
    table_list=$(cat $TABLE_LIST_FILE)
    for table_name in $table_list
    do
        echo "$(date +"%Y-%m-%d %H:%M:%S")|Getting index base info for table: $table_name"
        sqlplus -S sys/sys as sysdba <<EOF
    set pagesize 0  
    set feedback off 
    set heading off 
    set echo off
    spool $INDEX_BASE_INFO_DIR/$table_name.txt
    SELECT INDEX_NAME||':'||TABLE_NAME||':'||LISTAGG(COLUMN_NAME,',') WITHIN GROUP	(ORDER BY COLUMN_POSITION)  from  ALL_IND_COLUMNS WHERE INDEX_OWNER = '$SCHEMA' AND TABLE_NAME ='$table_name' GROUP BY INDEX_NAME,TABLE_NAME;
    spool off
    quit
EOF
    done 
}

init_dir
http://www.anysql.net/software/sqluldr.zip


export schema=DZZDSJ
export table=T_TEST
SET LONG 2000000
SET PAGESIZE 0
SELECT DBMS_METADATA.GET_DDL('TABLE', table_name) 
FROM all_tables
WHERE owner = '${schema}' AND table_name = '${table}';

SELECT DBMS_METADATA.GET_DDL('INDEX',u.index_name)
FROM USER_INDEXES u ;
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,'SEGMENT_ATTRIBUTES',false);

EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,'STORAGE',false);


select dbms_metadata.get_ddl('TABLE','T_TEST','DZZDSJ') from dual;

select dbms_metadata.get_ddl('$object_type ','$name','$schema') from dual;


CREATE TABLE DZZDSJ.T_DATA_TEST
(
    id     NUMBER(10,0),
    col1   CHAR(100),
    col2   VARCHAR2(100),
    col3   CHAR(100),
    col4   CHAR(100)
);
INSERT INTO DZZDSJ.T_DATA_TEST
SELECT a.rn,
       DBMS_RANDOM.STRING ('u', 5), --大写字母随机
       DBMS_RANDOM.STRING ('l', 5), --小写字母随机
       DBMS_RANDOM.STRING ('a', 5), --混合字母随机
       DBMS_RANDOM.STRING ('x', 5)  --字符串数字随机
     --DBMS_RANDOM.STRING ('p', 5) --键盘字符随机
  FROM (SELECT level,ROWNUM rn 
          FROM DUAL
       CONNECT BY ROWNUM<=500000) a;
--164 seconds       
COMMIT; 

ANALYZE TABLE DZZDSJ.T_DATA_TEST COMPUTE STATISTICS; 

SELECT A.OWNER,A.TABLE_NAME,A.TABLESPACE_NAME,A.NUM_ROWS,A.BLOCKS,A.EMPTY_BLOCKS,A.AVG_ROW_LEN
  FROM ALL_TABLES A 
 WHERE OWNER='DZZDSJ' 
   AND TABLE_NAME ='T_DATA_TEST';

SPOOL /home/dzzdsj/t_data_test_spool.txt 
SET ECHO OFF  --不显示脚本中正在执行的SQL语句
SET FEEDBACK OFF --不显示sql查询或修改行数
SET TERM OFF   --不在屏幕上显示
SET HEADING OFF  --不显示列
SET LINESIZE 1000; //设置行宽，根据需要设置，默认100
select id||','||col1|| ',' ||col2|| ',' ||col3|| ',' ||col4 FROM dzzdsj.T_DATA_TEST;  --需要导出的数据查询sql
SPOOL OFF

SPOOL /home/dzzdsj/t_data_test_spool.txt 
SET ECHO OFF  
SET FEEDBACK OFF 
SET TERM OFF   
SET HEADING OFF  
SET LINESIZE 1000
select id||','||col1|| ',' ||col2|| ',' ||col3|| ',' ||col4 FROM dzzdsj.T_DATA_TEST; 
SPOOL OFF

set time on;
@/home/dzzdsj/t_data_test_spool.sql
14M/s

CREATE OR REPLACE DIRECTORY data_dir AS '/data_dir';
grant read,write on directory data_dir to dzzdsj;

DECLARE
     vsfile   UTL_FILE.file_type; 
     v_cnt    PLS_INTEGER := 0;
BEGIN
     vsfile :=UTL_FILE.fopen ('DATA_DIR','t_data_test_utlfile.txt','w',32767);
FOR i IN (SELECT id||','||col1|| ',' ||col2|| ',' ||col3|| ',' ||col4 AS data FROM dzzdsj.T_DATA_TEST)
     LOOP
        UTL_FILE.put_line (vsfile, i.data);              
        v_cnt := v_cnt + 1;                             
     END LOOP;
    UTL_FILE.fflush (vsfile);
     UTL_FILE.fclose (vsfile);
     DBMS_OUTPUT.put_line (v_cnt || ' rows unloaded');
  END;
  /
1M/s

DECLARE
     vsfile   UTL_FILE.file_type; 
BEGIN
     vsfile :=UTL_FILE.fopen ('DATA_DIR','t_data_test_utlfile.txt','w',32767);
FOR i IN (SELECT id||','||col1|| ',' ||col2|| ',' ||col3|| ',' ||col4 AS data FROM dzzdsj.T_DATA_TEST)
     LOOP
        UTL_FILE.put_line (vsfile, i.data);                                        
     END LOOP;
    UTL_FILE.fflush (vsfile);
     UTL_FILE.fclose (vsfile);
  END;
  /


sqluldr2 dzzdsj/dzzdsj query="SELECT id||','||col1|| ',' ||col2|| ',' ||col3|| ',' ||col4  FROM dzzdsj.T_DATA_TEST" head=no file="/home/dzzdsj/t_data_test_sqluldr.txt" log="/home/dzzdsj/t_data_test_sqluldr.log"

sqluldr2 dzzdsj/dzzdsj query="SELECT *  FROM dzzdsj.T_DATA_TEST" head=no field='0x20'  file="/data_dir/t_data_test_sqluldr_0x20.txt" log="/home/dzzdsj/t_data_test_sqluldr.log" width='10:120:120:110:110'

sqluldr2 dzzdsj/dzzdsj query="SELECT *  FROM dzzdsj.T_DATA_TEST" head=no field='0x20'  file="/data_dir/t_data_test_sqluldr_0x20_%b.txt" log="/home/dzzdsj/t_data_test_sqluldr.log" width='10:120:120:110:110' batch=2
--一个batch表示50万条记录,batch=2表示单文件100万条记录

./sqluldr2 scott/tiger@192.168.163.108/orcl query=emp quote=0x22 field="," degree=8 file=- |gsql -d postgres -Umogdb -WEnmo@123 -hlocalhost -p26000 -c "\copy scott.emp from stdin DELIMITER ',' quote '\"' csv"


15M/s

SELECT id,name FROM dzzdsj.T_TEST WHERE name LIKE '%'||chr(92)||'%';

SELECT id,name FROM dzzdsj.T_TEST WHERE REGEXP_LIKE(name,'\\');

UPDATE dzzdsj.T_TEST SET NAME ='1'||chr(0)||'2' WHERE id=1;

-----------------------------------
sqluldr2 dzzdsj/dzzdsj query="SELECT *  FROM dzzdsj.T_TEST" head=no field='|'  file="/tmp/t_test.txt" log="/home/dzzdsj/tmp/t_test_sqluldr.log" charset="AL32UTF8"

sqluldr2 dzzdsj/dzzdsj query="SELECT *  FROM dzzdsj.T_TEST" head=no field='0x20'  file="/tmp/t_test_fixed.txt" log="/home/dzzdsj/tmp/t_test_fixed_sqluldr.log" charset="AL32UTF8"  width='10:30:10:20:20'

copy dzzdsj.t_test from '/tmp/t_test.txt' LOG ERRORS DATA REJECT LIMIT 'unlimited' delimiter '|';

copy dzzdsj.t_test from '/tmp/t_test_fixed.txt' LOG ERRORS DATA REJECT LIMIT 'unlimited' FIXED FORMATTER(id(0,10),name(10,30),cust_id(40,10),create_time(50,20),update_time(70,20)) timestamp_format 'YYYY-MM-DD HH24:MI:SS';
