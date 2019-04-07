from flask import Flask
from flask import request
from api.model.user import db
from flask_cors import CORS
from api.serializer.serializers import UsersSerializer, RoleSerializer
from api.views.register_and_login import register, login, activate_user, logout
from api.views.user import user, upload_image
from api.model.config import app
from flask import send_from_directory

#db.create_all()


cors = CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/register', methods=['POST'])
def register_endpoint():

    return register(request)

@app.route('/login', methods=['POST'])
def login_endpoint():

    if "code" in request.json:
        activate_user(request)

    return login(request)

@app.route('/user/<int:id>', methods=['GET'])
def get_user_endpoint(id):

    return user(id)

@app.route('/upload/user/<int:user_id>', methods=['POST'])
def upload_endpoint(user_id):

    return upload_image(request, user_id)

@app.route('/dir/<path:path>', methods=['GET'])
def serve_file_in_dir_endpoint(path):

    var = '/home/oem/Desktop/Projects/E-wallet/e-wallet-server/api/model/uploads/'
    return send_from_directory(var, path)

@app.route('/logout', methods=['POST'])
def logout_endpoint():

    return logout(request)


"""@app.route('/role', methods=['GET'])
def create_role():

    role = Role()
    role.role_name = 'user'
    role.deleted = False
    db.session.add(role)
    db.session.commit()
    return "True"""


if __name__ == '__main__':
    app.run()