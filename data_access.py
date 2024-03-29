import pymongo


class MongoDB:
    def __init__(self):
        self.db_handler = pymongo.MongoClient('mongodb+srv://royee13028:a301047718451@cluster0.uggn4gr.mongodb.net/?retryWrites=true&w=majority')['cat_db']['cat']

    def insert(self, data):
        result = self.db_handler.insert_one(data)
        return result

    def update(self, query, data):
        result = self.db_handler.update_one(query, data)
        return result

    def get(self, query):
        result = self.db_handler.find(query)
        data = []
        for r in result:
            data.append(r)

        return data

    def delete(self, query):
        self.db_handler.delete_one(query)
