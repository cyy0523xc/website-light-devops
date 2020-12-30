# 轻量级站点部署管理工具

## 启动

```sh
cd src

# 复制配置文件
cp settings-example.py settings.py

# 配置项目及安全秘钥
vim settings.py

# 创建上传目录和模块目录
# 可以使用脚本创建(待开发)
# 创建模块目录
/root_path/project_name/module_name
# 创建模块的上传目录
/root_path/project_name/upload/module_name

# 启动
python3 main.py
```
