import os

# nginx root path
nginx_root = '/etc/nginx/nginx-conf/'
# Nginx管理秘钥
nginx_secret = 'b5daadda4a6911ebac98c5b326b3161c'

# 项目根目录
root_path = os.path.join('/tmp')
# 部署项目与密钥
projects_conf = {
    # 项目：text.eyedmp.com
    # 项目对应根目录下的一个目录
    'text.eyedmp.com': {
        'secret': 'sdnk29isdk#%8',     # 秘钥
    }
}
