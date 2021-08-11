import os

# 默认端口
default_port = 18000

# Nginx管理密钥及管理密钥
nginx_secret = 'b5daadda4a6911ebac98c5b326b3161c'
# nginx网站配置所在目录
nginx_site_path = '/product_demo_devops/apps/website-light-devops/nginx-conf/'

# 项目根目录
root_path = '/product_demo_devops/apps/website-light-devops/projects/'
# 代码文件所在目录
base_path = os.getcwd()
base_path = os.path.join(base_path, os.path.dirname(__file__))

# 端口的范围
# 定义范围主要是为了避免端口冲突
port_min = 31000
port_max = 31999

# 参数正则
params_pattern = {
    'project': '^[a-zA-Z\d][a-zA-Z\d\.\-]{3,99}$',
    'version': '^(\d+\.){1,2}\d+$',
    'host': '^[a-zA-Z\d][a-zA-Z\d\.\-]{3,63}$',
}

# 校验变量
assert os.path.isdir(nginx_site_path)
assert os.path.isdir(root_path)
