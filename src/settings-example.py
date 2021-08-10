import os

# nginx root path
nginx_root = '/etc/nginx/nginx-conf/'
# Nginx管理秘钥
nginx_secret = 'b5daadda4a6911ebac98c5b326b3161c'
# nginx网站配置所在目录
nginx_site_path = '/'

# 项目根目录
root_path = '/tmp/'
# 代码文件所在目录
base_path = os.getcwd()
base_path = os.path.join(base_path, os.path.dirname(__file__))

# 端口的范围
# 定义范围主要是为了避免端口冲突
port_min = 31000
port_max = 31999
