from PIL import Image
from MyQR import myqr

import qrcode
import os
import io

current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_path)
static_image_path = os.path.join(root_path, 'static', 'image')
dynamic_image_path = os.path.join(root_path, 'static', 'runtime', 'qrimage')


def createQrImageWithData(data, image_name):
    image_dir = set(os.listdir(dynamic_image_path))
    if image_name not in image_dir:
        # myqr.run(
        #     data,
        #     version=8,
        #     level='H',
        #     picture=None,
        #     colorized=False,
        #     contrast=1.0,
        #     brightness=1.0,
        #     save_name=image_name,
        #     save_dir=dynamic_image_path
        # )
        print('create qr image')
        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=1)
        qr.add_data(data)
        img = qr.make_image()
        img.save(os.path.join(dynamic_image_path, os.path.basename(image_name)))
        convertImageWithPath(image_name)
        print('end create qr image')
        return return_qr_io(image_name)
    else:
        # 直接返回图片
        return return_qr_io(image_name)


def convertImageWithPath(img_name):
    print('convert qr image with logo')
    qrImage = Image.open(os.path.join(dynamic_image_path, img_name)).convert('RGBA')
    # 这里换成你想要的尺寸
    qrImage = qrImage.resize((200, 200), Image.ANTIALIAS)
    addImage = Image.open(os.path.join(static_image_path, 'qr.png')).convert('RGBA')
    # 这里换成你想要的尺寸
    addImage = addImage.resize((40, 40), Image.ANTIALIAS)
    hqr, wqr = qrImage.size
    hadd, wadd = addImage.size
    # 获取图片大小，同时计算左上角的位置
    loc = (int(hqr / 2 - hadd / 2), int(wqr / 2 - wadd / 2))
    qrImage.paste(addImage, loc)
    qrImage.save(os.path.join(dynamic_image_path, os.path.basename(img_name)))
    print('end convert')


def return_qr_io(img_name):
    print('start return qr image io')
    qrImage = Image.open(os.path.join(dynamic_image_path, img_name)).convert('RGBA')
    output = io.BytesIO()
    qrImage.save(output, format='png')
    print('end return qr image io')
    return output.getvalue()


if __name__ == '__main__':
    createQrImageWithData('http://jianshu.com')
