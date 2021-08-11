# crontab -e:
# * * * * * nohup bash /product_demo_devops/apps/website-light-devops/website-light-devops/start.sh &
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$dir"
# 尽量避免和目录名一致
key="website-light-devops-run"
if
    ps aux|grep "$key"|grep python|grep -v start.sh|grep -v grep
then
    echo $(date) > status.log
    echo $(ps aux|grep "$key"|grep python|grep -v start.sh|grep -v grep) >> status.log
else
    python3 src/main.py --key "$key" 1> running.log 2>&1  # >> running.log
    echo $(date) >> running.log
fi