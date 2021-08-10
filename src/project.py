# -*- coding: utf-8 -*-
# 项目相关
#
# Author: caiyingyao
# Email: cyy0523xc@gmail.com
# Created Time: 2021-08-10
import os
import json
from typing import Dict
from os.path import join, isdir, isfile
from settings import root_path, base_path
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

    def secret_check(self, secret: str, project_conf: dict) -> bool:
        """安全检测"""
        if secret != project_conf['secret']:
            print(self.project, secret)
            error('项目发布密钥错误')
        if self.project in set(['upload', 'backup', 'tmp', 'deploy.log', 'version.txt']):
            print(self.project)
            error('非法项目名称')

        if not isdir(self.project_path) or not isdir(self.upload_path):
            print(self.project_path, isdir(self.project_path))
            print(self.upload_path, isdir(self.upload_path))
            error('模块名不存在或者配置不正确')

        return True

    def init(self, port: int, secret: str, desc: str) -> bool:
        """项目目录初始化:
        1. 创建项目目录
        2. 创建上传目录
        3. 更新项目配置
        """
        if isdir(self.project_path):
            error('项目目录已经存在：%s' % self.project_path)
        #
        if self.project in set(['upload', 'backup', 'tmp', 'deploy.log', 'version.txt']):
            print(self.project)
            error('非法项目名称')
        # 判断端口是否冲突
        confs = get_projects()
        for prj, conf in confs.items():
            if prj == self.project:
                error('项目名称冲突: %s' % self.project)
            if conf['port'] == port:
                error('端口号冲突: %d' % port)

        # 创建项目目录
        os.makedirs(self.project_path)
        # 更新项目列表
        confs[self.project] = {
            'secret': secret,     # 秘钥
            'port': port,                 # 端口号
            'desc': desc,
        }
        update_confs(confs)
        return True


def get_projects() -> Dict:
    """获取所有项目配置"""
    conf_file = join(base_path, 'projects.json')
    if not isfile(conf_file):
        return {}
    return json.load(conf_file)


def update_confs(confs) -> None:
    """更新项目配置"""
    conf_file = join(base_path, 'projects.json')
    with open(conf_file, 'w', encoding='utf8') as f:
        f.write(json.dump(confs))
