from flask import Flask, request, abort
from RtnMessage import RtnMessage
from cat_table import CatTable
from data_access import MongoDB
from functools import wraps
from flask_cors import CORS
import glob
import uuid
import shutil
import os

app = Flask(__name__)
CORS(app)
type_sex = ['底迪', '美眉']
type_age = ['幼貓', '成貓']
type_close = ['親人', '親貓', '']
type_status = ['可認養', '訓練中']

image_type = ['jpeg', 'bmp', 'png', 'gif', 'jpg']


def identity_check(f):
    @wraps(f)
    def func(*args, **kwargs):
        pws = 'admin'   # 密碼
        if pws != request.form['pws']:
            raise abort(403)
        return f(*args, **kwargs)

    return func


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in image_type


@app.route('/cat', methods=['GET'])
def get_cat():
    rtn = RtnMessage()
    try:
        data = {
            "age_type": request.args.get('age_type', None),
            "sex_type": request.args.get('sex_type', None),
            "close_type": request.args.get('close_type', None),
            "status_type": request.args.get('status_type', None),
            "is_adapted": request.args.get('is_adapted', None),
            "name": request.args.get('name', None),
            "_id": request.args.get('uid', None)
        }
        query_data = {}
        for key, value in data.items():
            if value:
                if key in ['status_type', 'close_type', 'age_type', 'sex_type']:
                    query_data[key] = value
                else:
                    query_data[key] = value
        dao = MongoDB()
        df = dao.get(query_data)
        for d in df:
            return_data = {}
            return_data['photo'] = './'+ os.path.relpath(d['photo'], 'C:\\Users\\郭璦菁\\OneDrive\\桌面\\cat_backend')
            return_data['photo'] = return_data['photo'].replace('\\', '/')
            return_data['photo_album_list'] = glob.glob(f'./cat_image_base/{d["_id"]}/photo_album/*')
            for i, photo in enumerate(return_data['photo_album_list']):
                return_data['photo_album_list'][i] = photo.replace('\\', '/')
            return_data['uid'] = d['_id']
            return_data['name'] = d['name']
            return_data['age'] = d['age']
            return_data['des'] = d['des']
            return_data['adapted_date'] = d['adapted_date']
            return_data['personality'] = d['personality'].split(',')
            return_data['cat_status'] = d['cat_status'].split(',')
            return_data['type'] = {
                "sex_type": d['sex_type'],
                "age_type": d['age_type'],
                "close_type": d['close_type'],
                "status_type": d['status_type']
            }
            return_data['is_adapted'] = d['is_adapted']
            rtn.result.append(return_data)
    except Exception as e:
        rtn.state = False
        rtn.msg = str(e)

    return rtn.to_dict()


@app.route('/cat', methods=['POST'])
@identity_check
def create_cat():
    rtn = RtnMessage()
    try:
        data = request.form
        uid = uuid.uuid4()
        if data.get('status_type', None) not in type_status:
            raise Exception(f'invalid status_type input, expect:{type_status}')

        if data.get('age_type', None) not in type_age:
            raise Exception(f'invalid age_type input, expect:{type_age}')

        if data.get('close_type', None) not in type_close:
            raise Exception(f'invalid close_type input, expect:{type_close}')

        if data.get('sex_type', None) not in type_sex:
            raise Exception(f'invalid sex_type input, expect:{type_sex}')

        image_path = None
        image = request.files.get('photo', None)
        if image:
            if not allowed_file(image.filename):
                raise Exception(f'invalid file type, expect:{image_type}')
            if not os.path.exists(f'./cat_image_base/{uid}'):
                os.mkdir(f'./cat_image_base/{uid}')
            image_path = f'./cat_image_base/{uid}/{uid}.{image.filename.rsplit(".", 1)[1].lower()}'
            image.save(image_path)
            image_path = image_path

        photo_album_list = request.files.getlist('photo_album[]')
        if photo_album_list:
            if not os.path.exists(f'./cat_image_base/{uid}/photo_album'):
                os.mkdir(f'./cat_image_base/{uid}/photo_album')
            for i, photo in enumerate(photo_album_list):
                if not allowed_file(photo.filename):
                    raise Exception(f'invalid file type, expect:{image_type}')
                photo_album_path = f'./cat_image_base/{uid}/photo_album/{uid}_{i}.{photo.filename.rsplit(".", 1)[1].lower()}'
                photo.save(photo_album_path)

        insert_data = CatTable(
            uid=str(uid),
            name=data['name'],
            sex_type=data['sex_type'],
            age=data['age'],
            des=data['des'],
            photo=image_path,
            age_type=data['age_type'],
            close_type=data['close_type'],
            status_type=data['status_type'],
            personality=data['personality'],
            cat_status=data['cat_status'],
            is_adapted=data.get('is_adapted', False),
            adapted_date=data.get('adapted_date', None)
        ).to_dict()

        dao = MongoDB()
        dao.insert(insert_data)

    except Exception as e:
        rtn.state = False
        rtn.msg = str(e)

    return rtn.to_dict()


@app.route('/cat', methods=['DELETE'])
@identity_check
def delete_cat():
    rtn = RtnMessage()
    try:
        uid = request.form['uid']
        query_data = {
            "_id": uid
        }
        dao = MongoDB()
        dao.delete(query_data)

        shutil.rmtree(f'./cat_image_base/{uid}', ignore_errors=True)
    except Exception as e:
        rtn.state = False
        rtn.msg = str(e)
    return rtn.to_dict()


@app.route('/cat', methods=['PUT'])
@identity_check
def update_cat():
    rtn = RtnMessage()
    try:
        data = request.form
        uid = data['uid']
        if data.get('status_type', None) not in type_status:
            raise Exception(f'invalid status_type input, expect:{type_status}')

        if data.get('age_type', None) not in type_age:
            raise Exception(f'invalid age_type input, expect:{type_age}')

        if data.get('close_type', None) not in type_close:
            raise Exception(f'invalid close_type input, expect:{type_close}')

        if data.get('sex_type', None) not in type_sex:
            raise Exception(f'invalid sex_type input, expect:{type_sex}')

        image_path = None
        image = request.files.get('photo', None)
        if image:
            if not allowed_file(image.filename):
                raise Exception(f'invalid file type, expect:{image_type}')
            if not os.path.exists(f'./cat_image_base/{uid}'):
                os.mkdir(f'./cat_image_base/{uid}')
            image_path = f'./cat_image_base/{uid}/{uid}.{image.filename.rsplit(".", 1)[1].lower()}'
            image.save(image_path)

        photo_album_list = request.files.getlist('photo_album[]')
        if photo_album_list:
            if not os.path.exists(f'./cat_image_base/{uid}/photo_album'):
                os.mkdir(f'./cat_image_base/{uid}/photo_album')
            for i, photo in enumerate(photo_album_list):
                if not allowed_file(photo.filename):
                    raise Exception(f'invalid file type, expect:{image_type}')
                photo_album_path = f'./cat_image_base/{uid}/photo_album/{uid}_{i}.{photo.filename.rsplit(".", 1)[1].lower()}'
                photo.save(photo_album_path)

        insert_data = CatTable(
            uid=str(uid),
            name=data['name'],
            sex_type=data['sex_type'],
            age=data['age'],
            des=data['des'],
            photo=image_path,
            age_type=data['age_type'],
            close_type=data['close_type'],
            status_type=data['status_type'],
            personality=data['personality'],
            cat_status=data['cat_status'],
            is_adapted=data.get('is_adapted', False),
            adapted_date=data.get('adapted_date', None)
        ).to_dict()
        query_data = {
            "_id", uid
        }
        dao = MongoDB()
        dao.update(query_data, insert_data)

    except Exception as e:
        rtn.state = False
        rtn.msg = str(e)

    return rtn.to_dict()


if __name__ == '__main__':
    app.run(
        debug=True,
        use_reloader=False
    )
