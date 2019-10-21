from api.model.country import Country, Currency, City
from config import session as Session

class OtherProvider:

    @classmethod
    def get_countries(cls):
        countries = Session.query(Country)\
            .filter(Country.activated == True)
        return countries.all()

    @classmethod
    def get_cities(cls, country_id):
        cities = Session.query(City)\
            .filter(City.country_id == country_id)
        return cities.all()

