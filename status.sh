# 可以直接kill掉进程
# stop：kill -9 {pid}
ps aux|grep "website-light-devops-run"|grep python|grep -v start.sh|grep -v grep