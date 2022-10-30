import sqlite3
import logging


class DbStructure:

    def __init__(self, db_name = "text-cache.sqlite"):
        self.connect = sqlite3.connect(db_name)

        try:
            self.connect.execute("""
                    CREATE TABLE IF NOT EXISTS GEODATA (
                        lat number(3, 8) ,
                        lon number(3, 8) ,
                        geodata_json TEXT
                    );
                """)
            logging.info("Success: CREATE TABLE IF NOT EXISTS GEODATA")
            self.connect.execute("CREATE UNIQUE INDEX IF NOT EXISTS GEODATA_IDX ON GEODATA (lat, lon)")
            logging.info("Success: CREATE UNIQUE INDEX IF NOT EXISTS GEODATA_IDX ON GEODATA")
        except Exception as ex:
            logging.warning("some SQL error: {}".format(ex))
            dataFromSql = self.connect.execute("SELECT count(*) FROM GEODATA");
            for row in dataFromSql.fetchall():
                logging.debug(str(row))
                pass

    def info(self):
        data_from_sql = self.connect.execute("SELECT     name FROM  sqlite_schema WHERE  type ='table'")
        fetchall = data_from_sql.fetchall()
        for i in fetchall:
            logging.debug(i)
