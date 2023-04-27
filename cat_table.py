import datetime


class CatTable:
    def __init__(self, name=None, sex_type=None, age=None, des=None, photo=None, age_type=None,
                 close_type=None, status_type=None, personality=None, uid=None, cat_status=None, is_adapted=None,
                 adapted_date=None):
        self.name = name
        self.sex_type = sex_type
        self.age = age
        self.des = des
        self.photo = photo
        self.age_type = age_type
        self.close_type = close_type
        self.status_type = status_type
        self.personality = personality
        self.uid = uid
        self.cat_status = cat_status
        self.create_on = datetime.datetime.utcnow()
        self.is_adapted = is_adapted
        self.adapted_date = adapted_date

    def to_dict(self):
        data = {
            "_id": self.uid,
            "name": self.name,
            "age": self.age,
            "des": self.des,
            "photo": self.photo,
            "personality": self.personality,
            "cat_status": self.cat_status,
            "sex_type": self.sex_type,
            "age_type": self.age_type,
            "close_type": self.close_type,
            "status_type": self.status_type,
            "adapted_date": self.adapted_date,
            "is_adapted": self.is_adapted,
            "create_on": self.create_on
        }
        return data
