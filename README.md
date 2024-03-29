# 轻量级站点部署管理工具

## 使用场景

### 前端版本更新

前端开发人员只需要按要求打包文件，然后使用接口就能自己完成版本的部署，并且记录版本更新日志，整个过程而不需要运维工程师的参与。

## 启动

```sh
# 安装依赖
pip install -r requirements.txt

cd src

# 复制配置文件
cp settings-example.py settings.py

# 配置项目及安全密钥
# 具体看配置文件
# 对应的目录得先建立，不然会报错
vim settings.py

# 测试启动
python3 main.py
```

线上部署则可以添加到crontab中，实现自动启动：

```sh
* * * * * nohup bash /path/to/website-light-devops/start.sh &
```

相关日志文件：

- `status.log`: 进程最近状态日志
- `running.log`: 进程运行日志

## 运维

查找进程id

```sh
bash status.sh

# 如果这两个命令是比较准确的，查找端口被占用的情况
netstat -anp |grep 18000
lsof -i:18000
```

知道进程id之后，停止：`kill -9 {pid}`
