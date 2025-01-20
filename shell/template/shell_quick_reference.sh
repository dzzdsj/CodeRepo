#日期时间格式化
echo "$(date +"%Y-%m-%d %H:%M:%S")|Getting table"

#awk注意事项
#1.awk 重定向要用双引号包裹起来
#2.awk 引用外部变量可以用双引号内加单引号包裹的形式
awk -F ","  'BEGIN{print "CREATE TABLE "'$SCHEMA_NAME'"."'$table_name'"(" > "'$TABLE_BASE_INFO_DIR'/'$table_name'.sql"}{
body = "";
}' $TABLE_BASE_INFO_DIR/$table_name.txt 

