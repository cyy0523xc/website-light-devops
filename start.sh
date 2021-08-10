# sudo crontab -e:
# * * * * * nohup bash /product_demo_devops/apps/website-light-devops/website-light-devops/start.sh &
# 注意需要在sudo下运行，否则初始化项目可能会不成功
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$dir"
key="website-light-devops"
if
    ps aux|grep "$key"|grep python|grep -v start.sh|grep -v grep
then
    echo $(date) > status.log
    echo $(ps aux|grep "$key"|grep python|grep -v start.sh|grep -v grep) >> status.log
else
    python3 src/main.py --key "$key" >> running.log
fi