from fastapi.encoders import jsonable_encoder

class SQLOps:
    """
    This class contains SQL operations for user management.
    It is used to perform various database operations related to users.
    """
    def __init__(self, session):
        """
        Initialize the SQLOps class with a database session.

        :param session: The database session to use for operations.
        """
        self.session = session

    async def execute_query(self, query, first_result=False, json_result=False):
        """
        Execute a SQL query.

        :param query: The SQL query to execute.
        :param first_result: If True, return only the first result; otherwise, return all results.
        :param json_result: If True, return the result as JSON; otherwise, return as a list of tuples.
        :return: The result of the executed query.
        """
        if first_result:
            result = self.session.execute(query).first()
        else:
            result = self.session.execute(query).all()

        if json_result:
            result =jsonable_encoder(result.mapping().all()) if hasattr(result, 'mapping') else jsonable_encoder(result.all())
        return result

    async def insert_many(self, data: list, model):
        """
        Execute an insert SQL query.

        :param data: The data to insert into the database. It can be a dictionary or a list of dictionaries.
        :param model: The model class to which the query belongs.
        :return: The result of the executed insert query.
        """
        final_result = []
        for each in data:
            each = model(**each)
            final_result.append(each)
            self.session.add(each)
        self.session.commit()
        return final_result

    def insert_one(self, data: dict, model):
        """
        Execute an insert SQL query for a single record.

        :param data: The data to insert into the database.
        :param model: The model class to which the query belongs.
        :return: The result of the executed insert query.
        """
        each = model(**data)
        self.session.add(each)
        self.session.commit()
        return each

    def update_query(self, data: dict, model, filter_condition):
        """
        Execute an update SQL query.

        :param data: The data to update in the database.
        :param model: The model class to which the query belongs.
        :param filter_condition: The condition to filter the records to be updated.
        :return: The result of the executed update query.
        """
        query = model.__table__.update().where(filter_condition).values(data)
        result = self.session.execute(query)
        self.session.commit()
        return result

    def delete_query(self, model, filter_condition):
        """
        Execute a delete SQL query.

        :param model: The model class to which the query belongs.
        :param filter_condition: The condition to filter the records to be deleted.
        :return: The result of the executed delete query.
        """
        query = model.__table__.delete().where(filter_condition)
        result = self.session.execute(query)
        self.session.commit()
        return result



