from flask import Flask
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)


class RoleSerializer(ma.Schema):

    class Meta:
        fields = ('id', 'created', 'role_name')


class ImageSerializer(ma.Schema):
     class Meta:
         fields = ('id', 'name', 'type', 'file_name')


class CountrySerializer(ma.Schema):
    class Meta:
        fields = ('id', 'created', 'name', 'phone_code', 'alpha3code', 'activated')


class CitySerializer(ma.Schema):
    country = ma.Nested(CountrySerializer, only=['name'])

    class Meta:
        fields = ('id', 'created', 'name', 'country_id', 'country')


class CurrencySerializer(ma.Schema):
    class Meta:
        fields = ('id', 'created', 'name', 'symbol', 'symbol_native', 'code', 'name_plural', 'activated')


class UsersSerializer(ma.Schema):
    role = ma.Nested(RoleSerializer, only=['role_name'])
    image = ma.Nested(ImageSerializer, only=['file_name'])
    country = ma.Nested(CountrySerializer, only=['name'])
    city = ma.Nested(CitySerializer, only=['name'])
    currency = ma.Nested(CurrencySerializer, only=['name', 'code'])

    class Meta:
        fields = ('id', 'created', 'first_name', 'last_name', 'email', 'activated',
                  'first_login', 'last_login', 'birth_date', 'gender', 'address', 'phone', 'role_id', 'created',
                  'address', 'phone', 'city_id', 'country_id', 'currency_id', 'application_rating', 'city',
                  'country', 'role', 'image', 'currency')


class CategoryTranslationSerializer(ma.Schema):

    class Meta:
        fields = ('id', 'translation_category_name', 'lang_code')


class SubCategoryTranslationSerializer(ma.Schema):

    class Meta:
        fields = ('id', 'translation_subcategory_name', 'lang_code')


class CategorySerializer(ma.Schema):

    class Meta:
        fields = ('id', 'created', 'name', 'translations')


class SubCategorySerializer(ma.Schema):
    bill_category = ma.Nested(CategorySerializer, only=['name', 'translations'])

    class Meta:
        fields = ('id', 'created', 'name', 'bill_category_id', 'bill_category', 'translations')


class BillSerializer(ma.Schema):
    bill_category = ma.Nested(CategorySerializer, only=['name', 'translations'])
    bill_sub_category = ma.Nested(SubCategorySerializer, only=['name', 'translations'])
    image = ma.Nested(ImageSerializer, only=['file_name'])
    user = ma.Nested(UsersSerializer, only=['first_name', 'last_name'])
    currency = ma.Nested(CurrencySerializer, only=['name', 'code'])

    class Meta:
        fields = ('id', 'created', 'title', 'comment', 'price', 'bill_type', 'currency_id', 'image_id',
                  'bill_category_id', 'bill_sub_category_id', 'user_id', 'quantity', 'not_my_city', 'currency', 'image',
                  'bill_category', 'bill_sub_category', 'user')


class UserCirrenciesSerializer(ma.Schema):
    currency = ma.Nested(CurrencySerializer, only=['name', 'code'])
    user = ma.Nested(UsersSerializer, only=['first_name', 'last_name'])

    class Meta:
        fields = ('id', 'user_id', 'currency_id', 'monthly_cost_limit', 'user', 'currency')


class NewsSerializer(ma.Schema):
    user = ma.Nested(UsersSerializer, only=['first_name', 'last_name', 'role'])

    class Meta:
        fields = ('id', 'created', 'title', 'content', 'type', 'user_id', 'user')


class BugsSerializer(ma.Schema):
    user = ma.Nested(UsersSerializer, only=['first_name', 'last_name'])

    class Meta:
        fields = ('id', 'created', 'comment', 'is_fixed', 'user_id', 'user')
