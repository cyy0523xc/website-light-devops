"""
接口：
1. 部署新版本
2. 回滚就版本
"""
import os
from os.path import join, isfile, isdir
import time
import json
import shutil
import tarfile
from fastapi import FastAPI, File, UploadFile, Form
from settings import nginx_secret, nginx_site_path
from settings import base_path, root_path
from settings import port_min, port_max
from settings import params_pattern
from settings import deploy_port, deploy_host
from main_settings import BaseResp
from utils import err_return, succ_return, error
from utils import run_cmds, cmp_version
from project import ProjectPath, get_projects, update_confs

# print(base_path)
with open(join(base_path, 'description.md'), encoding='utf8') as f:
    description = f.read()

_idx = description.index('\n')
title = description[:_idx].strip().strip('# ')
description = description[_idx+1:].strip()
description = description.replace('{host}', deploy_host).replace('{port}', str(deploy_port))
app = FastAPI(
    title=title,
    description=description,
    version="0.7.1",
)


@app.post('/version/release', summary='新版本发布接口', tags=['版本管理'],
          response_model=BaseResp)
async def api_version_release(
    tar_file: UploadFile = File(..., description='待发布的打包文件，现支持tar格式'),
    project: str = Form(..., regex=params_pattern['project'], title='项目名称',
                        description='项目名称'),
    secret: str = Form(..., min_length=16, max_length=32, title='项目发布密钥',
                       description='项目发布密钥'),
    version: str = Form(..., regex=params_pattern['version'], title='版本号',
                        description='版本应该有自己的版本号，以便后续查询。版本号规范：1.0, 0.5.2，最多允许三级版本号'),
    remark: str = Form(..., min_length=10, max_length=100, title='版本更新备注',
                       description='新版本发布的时候，应该写上相应的更新说明，这些信息会记录在版本更新记录里，通过历史接口可以查询'),
):
    """新版本发布\n
    注意事项：\n
    1. 新版本发布之前，应该先查看版本更新历史信息，确认更新的版本是否正确 \n
    2. 注意打包文件必须满足要求，打包的目录必须要有一个`dist`目录
    """
    ppath = ProjectPath(project)
    ppath.secret_check(secret)
    tar_filename = tar_file.filename
    if any([not tar_filename.isascii(),
            '/' in tar_filename,
            '\\' in tar_filename,
            not tar_filename.endswith('.tar')]):
        error('非法文件或者文件名：%s' % tar_filename)

    # 获取旧的版本号信息
    if isfile(ppath.version_path):
        with open(ppath.version_path, encoding='utf8') as f:
            old_version = f.read().strip()
            if cmp_version(version, old_version) <= 0:
                return err_return('版本号不是最新的。比较规则举例：1.2 > 1.1.10, 1.2 < 1.10')

    # 保存到上传目录
    tar_file = tar_file.file
    upload_filename = join(ppath.upload_path, tar_filename)
    with open(upload_filename, 'wb', encoding='utf8') as f:
        f.write(tar_file.read())

    # 解压到项目模块目录
    if not tarfile.is_tarfile(upload_filename):
        os.remove(upload_filename)
        return err_return('非法tar文件')

    # 删除备份项目
    if isdir(ppath.project_bak):
        shutil.rmtree(ppath.project_bak, ignore_errors=True)

    # 备份旧项目（回滚时可以直接回滚该目录）
    shutil.move(ppath.project_path, ppath.project_bak)

    # 部署新项目
    with tarfile.open(upload_filename, encoding='utf8') as tfile:
        names = tfile.getnames()
        if names[0] != 'dist':
            return err_return('打包文件结构错误')
        for name in names:
            if not name.startswith('dist'):
                return err_return('打包文件结构错误')

        tfile.extractall(ppath.project_path)

    # delete upload file
    os.remove(upload_filename)
    # 写入版本号数据
    with open(ppath.version_path, 'w+', encoding='utf8') as f:
        f.write(version)

    # 记录部署信息
    with open(ppath.deploy_log, 'a+', encoding='utf8') as f:
        data = {
            'time': time.strftime("%Y-%m-%d %H:%M:%S"),
            'action': 'release',
            'filename': tar_filename,
            'version': version,
            'remark': remark,
        }
        f.write(json.dumps(data) + '\n')
    return succ_return()


@app.post('/version/rollback', summary='版本回滚接口', tags=['版本管理'],
          response_model=BaseResp)
async def api_version_rollback(
    project: str = Form(..., regex=params_pattern['project'], title='项目名称',
                        description='项目名称'),
    secret: str = Form(..., title='项目发布密钥',
                       description='项目发布密钥'),
):
    """版本回滚到上一个版本"""
    ppath = ProjectPath(project)
    ppath.secret_check(secret)
    if not isdir(ppath.project_bak):
        return err_return('备份版本不存在，无法回滚')

    # 备份当前模块
    if isdir(ppath.project_tmp):
        shutil.rmtree(ppath.project_tmp, ignore_errors=True)
    shutil.move(ppath.project_path, ppath.project_tmp)
    try:
        # 回滚备份
        shutil.move(ppath.project_bak, ppath.project_path)
    except Exception as e:
        # 回滚不成功则还原
        print('rollbak error: ', e)
        shutil.move(ppath.project_tmp, ppath.project_path)
        return err_return('回滚版本失败')

    # 删除多余的备份
    shutil.rmtree(ppath.project_tmp)
    # 记录部署信息
    with open(ppath.deploy_log, 'a+', encoding='utf8') as f:
        data = {
            'time': time.strftime("%Y-%m-%d %H:%M:%S"),
            'action': 'rollback',
        }
        f.write(json.dumps(data) + '\n')
    return succ_return()


@app.post('/nginx/reload', summary='Nginx配置重新加载', tags=['Nginx'],
          response_model=BaseResp)
async def api_nginx_reload(
    secret: str = Form(..., title='管理密钥',
                       description='管理密钥'),
):
    """相当于执行命令: nginx -s reload"""
    if secret != nginx_secret:
        error('管理密钥错误')
    cmds = ['nginx -s reload']
    msg = run_cmds(cmds)
    return succ_return(msg=msg)


@app.get('/project', summary='获取项目列表', tags=['Project'])
async def api_config_projects():
    """获取项目列表接口\n
    可以查看已经配置的项目名称，端口，备注，当前版本及最后的更新信息等信息。"""
    data = []
    projects_conf = get_projects()
    for key, val in projects_conf.items():
        ppath = ProjectPath(key)
        # 获取版本信息
        version = None
        if isfile(ppath.version_path):
            with open(ppath.version_path, encoding='utf8') as f:
                version = f.read().strip()
        # 获取最后更新数据
        last_updated = None
        if isfile(ppath.deploy_log):
            with open(ppath.deploy_log, encoding='utf8') as f:
                history = f.readlines()
            history = [m.strip() for m in history]
            history = [m for m in history if len(m) > 0]
            last_updated = [json.loads(m) for m in history[-2:]]

        data.append({
            'project_name': key,
            'port': val['port'],
            'desc': val['desc'],
            'version': version,
            'last_updated': last_updated,
        })
    return data


@app.post('/project/init', summary='项目初始化', tags=['Project'])
async def api_project_init(
    secret: str = Form(..., title='管理密钥',
                       description='管理密钥'),
    project: str = Form(..., regex=params_pattern['project'], title='项目名称',
                        description='项目名称'),
    host: str = Form(None, regex=params_pattern['host'], title='项目访问域名',
                     description='项目访问域名，如果该值为空，则使用IP+端口进行访问'),
    port: int = Form(..., ge=port_min, le=port_max, title='项目端口号',
                     description='项目端口号'),
    prj_secret: str = Form(..., title='项目发布密钥，每个项目可以定义不同的发布密钥',
                           description='项目发布密钥，每个项目可以定义不同的发布密钥'),
    desc: str = Form(..., title='项目说明',
                     description='项目说明'),
):
    """项目初始化\n
    在初始化之前，项目必须已经存在配置文件中。
    """
    if secret != nginx_secret:
        error('管理密钥错误')

    ppath = ProjectPath(project)
    ppath.init(port, prj_secret, desc)
    site_conf_temp = join(base_path, 'nginx-site.conf')
    with open(site_conf_temp, encoding='utf8') as f:
        site_conf = f.read()
    # 配置参数
    site_conf = site_conf.replace('__desc__', desc.replace('\r\n', '').replace('\n', ''))
    site_conf = site_conf.replace('__port__', str(port))
    site_conf = site_conf.replace('__root__', join(ppath.project_path, 'dist'))
    site_conf = site_conf.replace('__error_log__', join(ppath.project_path, 'error.log'))
    site_conf = site_conf.replace('__access_log__', join(ppath.project_path, 'access.log'))
    if host is not None:
        site_conf = site_conf.replace('__host__', 'server_name  %s' % host)

    # 写入配置
    site_file = join(nginx_site_path, '%s.conf' % project)
    with open(site_file, 'w', encoding='utf8') as f:
        f.write(site_conf)

    return succ_return('操作成功')


@app.delete('/project', summary='项目删除', tags=['Project'])
async def api_project_delete(
    secret: str = Form(..., title='管理密钥',
                       description='管理密钥'),
    project: str = Form(..., regex=params_pattern['project'], title='项目名称',
                        description='项目名称'),
):
    """项目删除\n
    删除一个存在的项目。
    """
    if secret != nginx_secret:
        error('管理密钥错误')

    ppath = ProjectPath(project)
    # 删除项目目录(备份)
    if isdir(ppath.project_path):
        targe_path = join(root_path, "backup_%s" % project)
        if isdir(targe_path):
            error('删除备份目录已经存在: %s' % targe_path)
        shutil.move(ppath.project_path, targe_path)

    # 删除nginx配置
    site_file = join(nginx_site_path, '%s.conf' % project)
    if isfile(site_file):
        os.remove(site_file)

    # 修改配置
    confs = get_projects()
    if project in confs:
        confs.pop(project)
    update_confs(confs)
    return succ_return('操作成功')



@app.post('/project/history', summary='项目更新历史', tags=['Project'])
async def api_version_history(
    project: str = Form(..., regex=params_pattern['project'], title='项目名称',
                        description='项目名称'),
):
    """获取版本更新的历史信息"""
    ppath = ProjectPath(project)
    if not isdir(ppath.project_path):
        error('参数错误')
    if not isfile(ppath.deploy_log):
        return []
    with open(ppath.deploy_log, encoding='utf8') as f:
        history = f.readlines()

    history = [m.strip() for m in history]
    history = [json.loads(m) for m in history if len(m) > 0]
    return history


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=deploy_port, reload=True)
