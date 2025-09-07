from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import insert


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

    async def execute_query(self, query, first_result: bool = False, json_result: bool = False):
        """
        Execute a SQL query.

        :param query: The SQL query to execute.
        :param first_result: If True, return only the first result; otherwise, return all results.
        :param json_result: If True, return the result as JSON; otherwise, return as a list of tuples.
        :return: The result of the executed query.
        """
        if first_result:
            if json_result:
                return jsonable_encoder(self.session.execute(query).mappings().first())
            result = self.session.execute(query).first()
            return result[0] if result else []
        else:
            if json_result:
                return jsonable_encoder(self.session.execute(query).mappings().all())
            return self.session.execute(query).all()

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

    async def upsert_query(self, data: dict, model, conflict_columns: list):
        """
        Execute an upsert SQL query.

        :param data: The data to upsert in the database.
        :param model: The model class to which the query belongs.
        :param conflict_columns: The columns to check for conflicts during the upsert operation.
        :return: The result of the executed upsert query.
        """
        insert_stmt = insert(model).values(data)
        if "updated_at" not in data and hasattr(model, 'updated_at'):
            data['updated_at'] = model.updated_at
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=conflict_columns,
            set_=data
        ).returning(model.id)
        result = self.session.execute(upsert_stmt)
        self.session.commit()
        return str(result.scalar()) if result else None

    async def bulk_upsert_fund_schemes(self, data_list: list[dict], model, conflict_columns: list):
        if not data_list:
            return {}

        stmt = insert(model).values(data_list)

        update_dict = {
            col.name: stmt.excluded[col.name]
            for col in model.__table__.columns
            if col.name not in conflict_columns and col.name != "id"
        }

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns,
            set_=update_dict
        ).returning(model.scheme_code, model.id)

        result = await self.session.execute(upsert_stmt)
        await self.session.commit()

        # Build mapping {scheme_code: scheme_id}
        return {row[0]: row[1] for row in result.fetchall()}

    async def bulk_upsert_nav_history(self, data_list: list[dict], model, conflict_columns: list):
        if not data_list:
            return {}

        stmt = insert(model).values(data_list)

        update_dict = {
            col.name: stmt.excluded[col.name]
            for col in model.__table__.columns
            if col.name not in conflict_columns and col.name != "id"
        }

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns,
            set_=update_dict
        )

        await self.session.execute(upsert_stmt)
        await self.session.commit()

        return None
