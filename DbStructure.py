import sqlite3
import logging


class DbStructure:

    def __init__(self, db_name = "text-cache.sqlite"):
        self.connect = sqlite3.connect(db_name)

        try:
            self.connect.execute("""
                    CREATE TABLE IF NOT EXISTS JOB_RAW_DATA (
                        job_id          number(16, 0) ,
                        job_href        TEXT,  
                        full_html       TEXT, 
                        company         VARCHAR(250), 
                        company_href    VARCHAR(250),
                        company_desc    VARCHAR(500),
                        location        VARCHAR(250),
                        job_type        VARCHAR(250)
                    );
                """)
            logging.info("Success: CREATE TABLE IF NOT EXISTS JOB_RAW_DATA")
            self.connect.execute("CREATE UNIQUE INDEX IF NOT EXISTS JOB_RAW_DATA_IDX ON JOB_RAW_DATA (job_id)")
            logging.info("Success: CREATE UNIQUE INDEX IF NOT EXISTS JOB_RAW_DATA_IDX ON JOB_RAW_DATA")
        except Exception as ex:
            logging.warning("some SQL error: {}".format(ex))

    def info(self):
        data_from_sql = self.connect.execute("SELECT * FROM  sqlite_schema WHERE  type ='table'")
        fetchall = data_from_sql.fetchall()
        for i in fetchall:
            logging.debug(i)
