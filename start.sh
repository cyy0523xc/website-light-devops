key="website-light-devops"
if
    ps aux|grep "$key"|grep -v grep
then
   echo $(date) > run.log
else
    nohup python3 src/main.py --key "$key" &
fi