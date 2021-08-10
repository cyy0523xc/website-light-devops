# -*- coding: utf-8 -*-
# 项目相关
#
# Author: caiyingyao
# Email: cyy0523xc@gmail.com
# Created Time: 2021-08-10
from os.path import join, isdir
from settings import root_path, projects_conf
from utils import error


class ProjectPath:
    def __init__(self, project: str) -> None:
        self.project = project
        # 项目根目录
        self.project_path = join(root_path, project)
        # 上传目录
        self.upload_path = join(root_path, project, 'upload')
        # 版本更新备份目录
        self.project_bak = join(root_path, project, 'backup')
        # 版本更新临时目录
        self.project_tmp = join(root_path, project, 'tmp')
        # 版本更新日志
        self.deploy_log = join(root_path, project, 'deploy.log')
        # 版本号记录文件
        self.version_path = join(root_path, project, 'version.txt')

    def secret_check(self, secret: str):
        """安全检测"""
        if self.project not in projects_conf or secret != projects_conf[self.project]['secret']:
            print(self.project, secret)
            error('错误的项目名称或者发布密钥')
        if self.project in set(['upload', 'backup', 'tmp', 'deploy.log', 'version.txt']):
            print(self.project)
            error('非法项目名称')

        if not isdir(self.project_path) or not isdir(self.upload_path):
            print(self.project_path, isdir(self.project_path))
            print(self.upload_path, isdir(self.upload_path))
            error('模块名不存在或者配置不正确')

        return True
