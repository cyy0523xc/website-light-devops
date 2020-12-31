"""
接口：
1. 部署新版本
2. 回滚就版本
"""
import os
import time
import shutil
import tarfile
from fastapi import FastAPI, File, UploadFile, Form
from settings import root_path, projects_conf
from settings import nginx_root, nginx_secret
from main_settings import BaseResp
from utils import err_return, succ_return, error
from utils import run_cmds, check_version, cmp_version

with open('description.md') as f:
    description = f.read()

app = FastAPI(
    title='轻量级项目版本发布管理工具',
    description=description,
    version="0.6",
)


@app.post('/version/release', summary='新版本发布接口', tags=['版本管理'], 
          response_model=BaseResp)
async def api_version_release(
    tar_file: UploadFile = File(..., description='待发布的打包文件，现支持tar格式'),
    project: str = Form(..., title='项目名称',
                        description='项目名称'),
    secret: str = Form(..., title='项目发布密钥',
                       description='项目发布密钥'),
    module: str = Form(..., title='模块名称',
                       description='模块名称'),
    version: str = Form(..., title='版本号',
                        description='版本应该有自己的版本号，以便后续查询。版本号规范：1.0, 0.5.2'),
    remark: str = Form('', title='版本更新备注',
                       description='新版本发布的时候，应该写上相应的更新说明，这些信息会记录在版本更新记录里，通过历史接口可以查询'),
):
    """新版本发布：新版本发布之前，应该先查看版本更新历史信息，确认更新的版本是否正确"""
    if not check_version(version):
        return err_return('版本号不规范，请参照接口的参数说明')

    secret_check(project, module, secret)
    project_path = os.path.join(root_path, project, module)
    upload_path = os.path.join(root_path, project, 'upload', module)
    tar_filename = tar_file.filename
    if not tar_filename.isascii() or '/' in tar_filename or '\\' in tar_filename or not tar_filename.endswith('.tar'):
        error('非法文件或者文件名')
    # 获取旧的版本号信息
    version_path = os.path.join(project_path, 'version.txt')
    if os.path.isfile(version_path):
        with open(version_path) as f:
            old_version = f.read().strip()
            if cmp_version(version, old_version) <= 0:
                return err_return('版本号不是最新的。比较规则举例：1.2 > 1.1.10, 1.2 < 1.10')

    # 保存到上传目录
    tar_file = tar_file.file
    upload_filename = os.path.join(upload_path, tar_filename)
    with open(upload_filename, 'wb') as f:
        f.write(tar_file.read())

    # 解压到项目模块目录
    if not tarfile.is_tarfile(upload_filename):
        os.remove(upload_filename)
        return err_return('非法tar文件')
    # 删除备份项目
    project_bak = os.path.join(root_path, project, 'backup', module)
    if os.path.isdir(project_bak):
        shutil.rmtree(project_bak, ignore_errors=True)
    # 备份旧项目（回滚时可以直接回滚该目录）
    shutil.move(project_path, project_bak)
    # 部署新项目
    with tarfile.open(upload_filename) as tfile:
        names = tfile.getnames()
        if names[0] != 'dist':
            return err_return('打包文件结构错误')
        for name in names:
            if not name.startswith('dist'):
                return err_return('打包文件结构错误')

        tfile.extractall(project_path)
    
    # delete upload file
    os.remove(upload_filename)
    # 写入版本号数据
    with open(version_path, 'w+') as f:
        f.write(version)

    # 记录部署信息
    deploy_log = get_deploy_logfile(project, module)
    with open(deploy_log, 'a+') as f:
        time_str = time.strftime("%Y-%m-%d %H:%M")
        msg = "\n%s: %s, Version: %s, Remark: %s" % (time_str, tar_filename, version, remark)
        f.write(msg)
    return succ_return()


@app.post('/version/rollback', summary='版本回滚接口', tags=['版本管理'],
          response_model=BaseResp)
async def api_version_rollback(
    project: str = Form(..., title='项目名称',
                        description='项目名称'),
    secret: str = Form(..., title='项目发布密钥',
                       description='项目发布密钥'),
    module: str = Form(..., title='模块名称',
                       description='模块名称'),
):
    """版本回滚到上一个版本"""
    secret_check(project, module, secret)
    project_path = os.path.join(root_path, project, module)
    project_bak = os.path.join(root_path, project, 'backup', module)
    if not os.path.isdir(project_bak):
        return err_return('备份版本不存在，无法回滚')

    # 备份当前模块
    project_bak_bak = os.path.join(root_path, project, module+'_bak_bak')
    if os.path.isdir(project_bak_bak):
        shutil.rmtree(project_bak_bak, ignore_errors=True)
    shutil.move(project_path, project_bak_bak)
    try:
        # 回滚备份
        shutil.move(project_bak, project_path)
    except Exception as e:
        # 回滚不成功则还原
        print('rollbak error: ', e)
        shutil.move(project_bak_bak, project_path)
        return err_return('回滚版本失败')

    # 删除多余的备份
    shutil.rmtree(project_bak_bak)
    # 记录部署信息
    deploy_log = get_deploy_logfile(project, module)
    with open(deploy_log, 'a+') as f:
        time_str = time.strftime("%Y-%m-%d %H:%M")
        msg = "Time: %s  Rollback\n" % time_str
        f.write(msg)
    return succ_return()


@app.post('/version/history', summary='版本更新历史', tags=['版本管理'])
async def api_version_history(
    project: str = Form(..., title='项目名称',
                        description='项目名称'),
    module: str = Form(..., title='模块名称',
                       description='模块名称'),
):
    """获取版本更新的历史信息"""
    project_path = os.path.join(root_path, project, module)
    if not os.path.isdir(project_path):
        error('参数错误')
    deploy_log = get_deploy_logfile(project, module)
    if not os.path.isfile(deploy_log):
        return []
    with open(deploy_log) as f:
        history = f.readlines()
     
    history = [m.strip() for m in history]
    history = [m for m in history if len(m) > 0]
    return history


@app.post('/nginx/pull', summary='Nginx配置更新', tags=['Nginx'])
async def api_nginx_pull(
    secret: str = Form(..., title='管理密钥',
                       description='管理密钥'),
):
    """相当于在Nginx配置目录执行git pull"""
    if secret != nginx_secret:
        error('秘钥错误')
    cmds = ['cd %s' % nginx_root, 'git pull']
    msg = run_cmds(cmds)
    return succ_return(msg=msg)


@app.post('/nginx/reload', summary='Nginx配置重新加载', tags=['Nginx'],
          response_model=BaseResp)
async def api_nginx_reload(
    secret: str = Form(..., title='管理密钥',
                       description='管理密钥'),
):
    """相当于执行命令: nginx -s reload"""
    if secret != nginx_secret:
        error('秘钥错误')
    cmds = ['nginx -s reload']
    msg = run_cmds(cmds)
    return succ_return(msg=msg)


def get_deploy_logfile(project, module):
    """获取部署日志文件名"""
    return os.path.join(root_path, project, 'logs', '%s-deploy.log' % module)


def secret_check(project, module, secret):
    """安全检测"""
    if project not in projects_conf or secret != projects_conf[project]['secret']:
        print(project, secret)
        error('错误的项目名称或者发布密钥')
    if project in set(('backup', 'logs')) or project.startswith('.'):
        print(project)
        error('非法项目名称')
    if not module.islower() or not module.isalpha():
        error('非法模块名')
    project_path = os.path.join(root_path, project, module)
    upload_path = os.path.join(root_path, project, 'upload', module)
    if not os.path.isdir(project_path) or not os.path.isdir(upload_path):
        print(project_path, os.path.isdir(project_path))
        print(upload_path, os.path.isdir(upload_path))
        error('模块名不存在或者配置不正确')

    return True


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=18000, reload=True)
