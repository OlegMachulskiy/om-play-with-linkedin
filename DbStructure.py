import logging
import sqlite3


class DbStructure:

    def __init__(self, db_name="text-cache.sqlite"):
        self.connect = sqlite3.connect(db_name)

        try:
            self.connect.execute("""
                    CREATE TABLE IF NOT EXISTS JOB_RAW_DATA (
                        job_id          number(16, 0) PRIMARY KEY,
                        job_href        TEXT,
                        job_title       VARCHAR(500),
                        full_html       TEXT, 
                        full_text       TEXT, 
                        company_name    VARCHAR(500), 
                        company_href    VARCHAR(500),
                        location        VARCHAR(500),
                        job_type        VARCHAR(500)
                    );
                """)
            logging.info("Success: CREATE TABLE IF NOT EXISTS JOB_RAW_DATA")
            self.connect.execute("CREATE UNIQUE INDEX IF NOT EXISTS JOB_RAW_DATA_IDX ON JOB_RAW_DATA (job_id)")
            logging.info("Success: CREATE UNIQUE INDEX IF NOT EXISTS JOB_RAW_DATA_IDX ON JOB_RAW_DATA")

            self.connect.execute("""
                                CREATE TABLE IF NOT EXISTS JOB_DETAILS (
                                    job_id          number(16, 0) ,
                                    insight_text    text     , 
                                    insight_href    text     
                                );
                            """)
            logging.info("Success: CREATE TABLE IF NOT EXISTS JOB_DETAILS")
            self.connect.execute("CREATE  INDEX IF NOT EXISTS JOB_DETAILS_IDX ON JOB_DETAILS (job_id)")
            logging.info("Success: CREATE  INDEX IF NOT EXISTS JOB_DETAILS_IDX ON JOB_DETAILS")

            self.connect.execute("""
                                CREATE TABLE IF NOT EXISTS JOB_ANALYSIS (
                                    job_id                      number(16, 0) REFERENCES JOB_RAW_DATA(job_id) ON DELETE CASCADE ,
                                    collocations                text,  
                                    technically_relevant        number(10, 8) ,
                                    position_relevant           number(10, 8) ,
                                    area_relevant               number(10, 8) ,
                                    relocation_relevant         number(10, 8) ,
                                    irrelevant_relevant         number(10, 8) ,
                                    hash_keywords               varchar(200),
                                    cosine_similarity           number(10, 8), 
                                    hash_corpus                 varchar(200)
                                );
                            """)
            logging.info("Success: CREATE TABLE IF NOT EXISTS JOB_ANALYSIS")
            self.connect.execute("CREATE UNIQUE INDEX IF NOT EXISTS JOB_ANALYSIS_IDX ON JOB_ANALYSIS (job_id)")
            logging.info("Success: CREATE UNIQUE INDEX IF NOT EXISTS JOB_ANALYSIS_IDX ON JOB_ANALYSIS")
        except Exception as ex:
            logging.warning("some SQL error: {}".format(ex))

    def info(self):
        data_from_sql = self.connect.execute("SELECT * FROM  sqlite_schema WHERE  type ='table'")
        fetchall = data_from_sql.fetchall()
        for i in fetchall:
            logging.debug(i)
