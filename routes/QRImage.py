from flask import Response
from libs.QrImagesConvert import createQrImageWithData
from hashlib import md5

import time


def QR_Image(request):
    start_time = time.time()
    data = request.args.get('data', '')
    if len(data) == 0:
        return Response("{'error':'输入错误'}", status=201, mimetype='application/json')
    else:
        data_md5 = md5(data.encode("utf-8"))
        image_name = data_md5.hexdigest()
        image_name = image_name + '.png'
        img = createQrImageWithData(data, image_name)
        end_time = time.time()
        time_time = end_time - start_time
        print("%d分%.2f秒" % ((time_time / 60), (time_time % 60.0)))
        return Response(img, mimetype='image/jpeg')
