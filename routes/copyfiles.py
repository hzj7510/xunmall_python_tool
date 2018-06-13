from flask import Response
from libs.copyfiles import copy_files


def route_copy_files(request):
    path = request.args.get('p', '')
    dis_path = request.args.get('dp', '')
    if len(dis_path) == 0 or len(path) == 0:
        return Response("{'error':'输入错误'}", status=201, mimetype='application/json')
    else:
        if copy_files(path, dis_path):
            return Response("{'success':'更新完成'}", status=200, mimetype='application/json')
        else:
            return Response("{'error':'更新错误'}", status=201, mimetype='application/json')

