from flask import request
from api.model.user import User, Image
from flask import jsonify
from api.serializer.serializers import UsersSerializer, ImageSerializer
from api.helper.helper import now, ValidateRequestSchema, error_handler, create_new_folder
import os
from api.model.config import app, PROJECT_HOME, UPLOAD_FOLDER
from werkzeug.utils import secure_filename
from api.model.config import db

def user(id):

    usr = User.query.filter(User.id == id).first()

    if not usr:
        return error_handler(404, 'User not found!')

    return jsonify (
        {
            'status': 'OK',
            'code': 200,
            'user': UsersSerializer(many=False).dump(usr).data,
            'user_id': usr.id,
        }
    )


def upload_image(request, user_id):
    app.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['image']:
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['image']
        img_name = secure_filename(img.filename)
        create_new_folder(app.config['UPLOAD_FOLDER'])
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        print (saved_path)
        app.logger.info("saving {}".format(saved_path))
        img.save(saved_path)
        new_image = Image()
        new_image.type = img_name.split('.')[1]
        new_image.name = img_name.split('.')[0]
        new_image.file_name = img_name
        db.session.add(new_image)
        db.session.commit()
        usr = User.query.filter(User.id == user_id).first()
        usr.image_id = new_image.id
        db.session.commit()
        image = ImageSerializer(many=False).dump(new_image).data
        return jsonify(
            {
                'status': 'OK',
                'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
                'code': 200,
                'msg': "Image is added!",
                'image': image
            }
        )
        #return send_from_directory(app.config['UPLOAD_FOLDER'],img_name, as_attachment=True)
    else:
        return "Where is the image?"