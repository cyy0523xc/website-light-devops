key="website-light-devops"
if
    ps aux|grep "$key"
then
   echo date > run.log
else
    python3 src/main.py --key "$key"
fi