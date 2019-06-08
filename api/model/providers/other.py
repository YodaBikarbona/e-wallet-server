from api.model.country import Country, Currency, City


class OtherProvider:

    @classmethod
    def get_countries(cls):
        return Country.query.filter(Country.activated == True).all()

    @classmethod
    def get_cities(cls, country_id):
        return City.query.filter(City.country_id == country_id).all()

