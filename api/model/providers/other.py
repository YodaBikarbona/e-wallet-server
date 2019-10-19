from api.model.country import Country, Currency, City
from api.model.config import db


class OtherProvider:

    @classmethod
    def get_countries(cls):
        countries = Country.query.filter(Country.activated == True).all()
        #db.session.close()
        return countries

    @classmethod
    def get_cities(cls, country_id):
        cities = City.query.filter(City.country_id == country_id).all()
        #db.session.close()
        return cities

