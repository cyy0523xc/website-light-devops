'''
工具函数库

Author: alex
Created Time: 2020年12月31日 星期四 09时42分48秒
'''
import os
import re
from uuid import uuid1
from fastapi import status, HTTPException


def err_return(msg):
    """错误信息"""
    return {
        'status': False,
        'msg': msg,
    }


def succ_return(msg=''):
    """成功信息返回"""
    return {
        'status': True,
        'msg': msg
    }


def error(msg, code=status.HTTP_422_UNPROCESSABLE_ENTITY):
    """错误异常"""
    raise HTTPException(status_code=code, detail=msg)


def run_cmds(cmds):
    """执行多个shell命令"""
    log_file = '/tmp/%s.log' % uuid1()
    cmds = ';'.join(cmds)
    os.system('%s > %s' % (cmds, log_file))
    if not os.path.isfile(log_file):
        error('操作失败')
    with open(log_file) as f:
        msg = f.read()
    os.remove(log_file)
    return msg


def check_version(version):
    """判断版本号字符串是否合法"""
    return len(re.findall('^(\d+\.){1,2}\d+$', version)) > 0


def cmp_version(new_ver, old_ver):
    """比较新旧版本号的大小"""
    new_ver = [int(v) for v in new_ver.split('.')]
    old_ver = [int(v) for v in old_ver.split('.')]
    for i in range(min(len(new_ver), len(old_ver))):
        if new_ver[i] == old_ver[i]:
            continue
        return new_ver[i] - old_ver[i]
    if len(new_ver) > len(old_ver):
        return 1
    if len(new_ver) < len(old_ver):
        return -1
    return 0
