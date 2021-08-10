import os

# nginx root path
nginx_root = '/product_demo_devops/apps/nginx-conf/nginx-conf-v2/'
# Nginx管理秘钥
nginx_secret = 'b5daadda4a6911ebac98c5b326b3161c'
# nginx网站配置所在目录
nginx_site_path = '/etc/nginx/sites-enabled/'

# 项目根目录
root_path = '/product_demo_devops/apps/website-light-devops/projects/'
# 代码文件所在目录
base_path = os.getcwd()
base_path = os.path.join(base_path, os.path.dirname(__file__))

# 端口的范围
# 定义范围主要是为了避免端口冲突
port_min = 31000
port_max = 31999
