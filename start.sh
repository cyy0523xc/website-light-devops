dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$dir"
key="website-light-devops"
if
    ps aux|grep "$key"|grep -v grep
then
    echo $(date) > status.log
else
    python3 src/main.py --key "$key" >> running.log
fi