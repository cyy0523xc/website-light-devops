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

# 部署密钥
projects_conf = {
    # 项目：text.eyedmp.com
    # 项目对应根目录下的一个目录
    'text.eyedmp.com': {
        'secret': 'sdnk29isdk#%8',     # 秘钥
        'port': 31000,                 # 端口号
        'desc': '项目描述',
    }
}
