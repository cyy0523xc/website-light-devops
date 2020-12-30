"""
接口：
1. 部署新版本
2. 回滚就版本
"""
import os
import shutil
import tarfile
from fastapi import FastAPI, File, UploadFile, Form
from fastapi import status, HTTPException
from settings import root_path, projects_conf
from main_settings import BaseResp

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
):
    secret_check(project, module, secret)
    project_path = os.path.join(root_path, project, module)
    upload_path = os.path.join(root_path, project, 'upload', module)
    tar_filename = tar_file.filename
    if not tar_filename.isascii() or '/' in tar_filename or '\\' in tar_filename or not tar_filename.endswith('.tar'):
        error('非法文件或者文件名')
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
    project_bak = os.path.join(root_path, project, module+'_bak')
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
    return succ_return()


@app.post('/version/rollback', summary='版本回滚接口', tags=['版本管理'],
          response_model=BaseResp)
async def api_version_release(
    project: str = Form(..., example='项目名称',
                        title='项目名称',
                        description='项目名称'),
    secret: str = Form(..., example='项目发布密钥',
                       title='项目发布密钥',
                       description='项目发布密钥'),
    module: str = Form(..., title='模块名称',
                       description='模块名称'),
):
    secret_check(project, module, secret)
    project_path = os.path.join(root_path, project, module)
    project_bak = os.path.join(root_path, project, module+'_bak')
    if not os.path.isdir(project_bak):
        return err_return('备份版本不存在，无法回滚')

    project_bak_bak = os.path.join(root_path, project, module+'_bak_bak')
    if os.path.isdir(project_bak_bak):
        shutil.rmtree(project_bak_bak, ignore_errors=True)
    shutil.move(project_path, project_bak_bak)
    try:
        shutil.move(project_bak, project_path)
    except Exception as e:
        print('rollbak error: ', e)
        shutil.move(project_bak_bak, project_path)
        return err_return('回滚版本失败')

    shutil.rmtree(project_bak_bak)
    return succ_return()


def err_return(msg):
    return {
        'status': False,
        'msg': msg,
    }


def succ_return():
    return {
        'status': True,
    }


def secret_check(project, module, secret):
    """安全检测"""
    if project not in projects_conf or secret != projects_conf[project]['secret']:
        print(project, secret)
        error('错误的项目名称或者发布密钥')
    if not module.islower() or not module.isalpha():
        error('非法模块名')
    project_path = os.path.join(root_path, project, module)
    upload_path = os.path.join(root_path, project, 'upload', module)
    if not os.path.isdir(project_path) or not os.path.isdir(upload_path):
        print(project_path, os.path.isdir(project_path))
        print(upload_path, os.path.isdir(upload_path))
        error('模块名不存在或者配置不正确')

    return True


def error(msg, code=status.HTTP_422_UNPROCESSABLE_ENTITY):
    raise HTTPException(status_code=code, detail=msg)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=18000, reload=True)
