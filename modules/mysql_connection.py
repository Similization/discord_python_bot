import json

from mysql.connector import connect, Error

try:
    with open("../configuration.json") as json_data_file:
        data = json.load(json_data_file)
    db = data["database"]
    with connect(
            host=db["host"],
            user=db["login"],
            password=db["password"],
    ) as connection:
        create_db_query = "SELECT * FROM discord_bot.users"
        with connection.cursor() as cursor:
            result = cursor.execute(create_db_query, multi=True)
            if result.with_rows:
                print("Rows produced by statement '{}':".format(
                    result.statement))
                print(result.fetchall())
            else:
                print("Number of rows affected by statement '{}': {}".format(
                    result.statement, result.rowcount))
except Error as e:
    print(e)

# class MYSQLContextManager(object):
#     """oracle db connection"""
#     def __init__(self, connection_string: str):
#         self.connection_string = connection_string
#         self.connector = None
#
#     def __enter__(self):
#         self.connector = mysql.connector.connect(self.connection_string)
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if exc_tb is None:
#             self.connector.commit()
#         else:
#             self.connector.rollback()
#         self.connector.close()
