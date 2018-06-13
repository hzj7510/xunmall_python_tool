from flask import Flask
from libs.copyfiles import copy_files
from routes.QRImage import QR_Image
from routes.CopyGoods import copy_goods
from flask import request, render_template, session
from flask.ext.cache import Cache
from flask_socketio import SocketIO, emit

app = Flask(__name__, template_folder='./static/html')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/qrimage')
def route_qrimage():
    print('get request')
    return QR_Image(request)


@app.route('/changedb')
def route_copy_goods():
    return copy_goods(request, cache)


@app.route('/copyfiles')
def route_copy_files():
    session['path'] = request.args.get('p', '')
    session['dis_path'] = request.args.get('dp', '')
    return render_template('copyfiles.html')


@socketio.on('connect_event')
def file_info_msg(msg):
    path = session.get('path')
    dis_path = session.get('dis_path')
    for info in copy_files(path, dis_path):
        emit('server_response', {'data': info})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8800)
