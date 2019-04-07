from flask import Flask
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)


class RoleSerializer(ma.Schema):

    class Meta:
        fields = ('id', 'created', 'deleted', 'role_name')


class ImageSerializer(ma.Schema):

     class Meta:
         fields = ('id', 'name', 'type', 'file_name')


class UsersSerializer(ma.Schema):
    role = ma.Nested(RoleSerializer, only=['role_name'])
    image = ma.Nested(ImageSerializer, only=['file_name'])

    class Meta:
        fields = ('id', 'created', 'deleted', 'first_name', 'last_name', 'email', 'activated',
                  'first_login', 'last_login', 'birth_date', 'gender', 'address', 'phone', 'city', 'role_id', 'created',
                  'address', 'phone', 'city', 'state', 'role', 'image')


# class SchoolYearSerializer(ma.Schema):
#
#     class Meta:
#         fields = ('id', 'start', 'end')
#
#
# class SchoolClassSerializer(ma.Schema):
#
#     class Meta:
#         fields = ('id', 'name', 'school_year_id')
#
#
# class SchoolClassStudentSerializer(ma.Schema):
#     school_class = ma.Nested(SchoolClassSerializer, only=['name'])
#     user = ma.Nested(UsersSerializer, only=['first_name', 'last_name'])
#
#     class Meta:
#         fields = ('id', 'student_id', 'classes_id', 'school_class', 'user')
#
#
# class SchoolClassProfessorSerializer(ma.Schema):
#     school_class = ma.Nested(SchoolClassSerializer, only=['name'])
#     user = ma.Nested(UsersSerializer, only=['first_name', 'last_name'])
#
#     class Meta:
#         fields = ('id', 'classes_id', 'professor_id', 'multiple_professors', 'school_class', 'user')
#
#
# class SchoolSubjectSerializer(ma.Schema):
#     user = ma.Nested(UsersSerializer, only=['first_name', 'last_name'])
#
#     class Meta:
#         fields = ('id', 'name', 'professor_id', 'user')
#
#
# class AbsenceSerializer(ma.Schema):
#
#     class Meta:
#         fields = ('id', 'class_id', 'school_subject_id', 'professor_id', 'student_id',
#                   'date', 'comment', 'approved')
#
#
# class GradeSerializer(ma.Schema):
#
#     class Meta:
#         fields = ('id', 'class_id', 'school_subject_id', 'professor_id', 'student_id',
#                   'date', 'comment', 'grade')
#
#
# class StudentGradeSerializer(ma.Schema):
#
#     class Meta:
#         fields = ('id', 'class_id', 'school_subject_id', 'professor_id', 'student_id',
#                   'closed', 'grade')