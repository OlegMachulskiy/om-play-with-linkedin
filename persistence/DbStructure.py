import logging
import sqlite3
import traceback


class DbStructure:

    def __init__(self, db_name="text-cache.sqlite"):
        self.connect = sqlite3.connect(db_name)

        try:
            self.connect.execute("""
                    CREATE TABLE IF NOT EXISTS JOB_RAW_DATA (
                        job_id          INTEGER     PRIMARY KEY,
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
                                    job_id          INTEGER ,
                                    insight_text    text     , 
                                    insight_href    text     
                                );
                            """)
            logging.info("Success: CREATE TABLE IF NOT EXISTS JOB_DETAILS")
            self.connect.execute("CREATE  INDEX IF NOT EXISTS JOB_DETAILS_IDX ON JOB_DETAILS (job_id)")
            logging.info("Success: CREATE  INDEX IF NOT EXISTS JOB_DETAILS_IDX ON JOB_DETAILS")

            self.connect.execute("""
                                CREATE TABLE IF NOT EXISTS JOB_ANL_KW (
                                    job_id                      INTEGER 
                                                    REFERENCES JOB_RAW_DATA(job_id) ON DELETE CASCADE ,
                                    technically_relevant        number(10, 8) ,
                                    position_relevant           number(10, 8) ,
                                    area_relevant               number(10, 8) ,
                                    relocation_relevant         number(10, 8) ,
                                    irrelevant_relevant         number(10, 8) ,
                                    hash_keywords               varchar(200),
                                    updated_at                  datetime 
                                );
                            """)
            logging.info("Success: CREATE TABLE IF NOT EXISTS JOB_ANL_KW")
            self.connect.execute("CREATE UNIQUE INDEX IF NOT EXISTS JOB_ANL_KW_IDX ON JOB_ANL_KW (job_id)")
            logging.info("Success: CREATE UNIQUE INDEX IF NOT EXISTS JOB_ANL_KW_IDX ON JOB_ANL_KW")

            self.connect.execute("""
                                CREATE TABLE IF NOT EXISTS JOB_ANL_SIMILARITY (
                                    job_id                          INTEGER 
                                                    REFERENCES JOB_RAW_DATA(job_id) ON DELETE CASCADE ,
                                    hash_relevant                   varchar(200), 
                                    hash_irrelevant                 varchar(200), 
                                    cosine_relevant                 number(10, 8), 
                                    cosine_irrelevant               number(10, 8), 
                                    spacy_relevant                  number(10, 8), 
                                    spacy_irrelevant                number(10, 8), 
                                    updated_at                      datetime 
                                );
                            """)
            logging.info("Success: CREATE TABLE IF NOT EXISTS JOB_ANL_SIMILARITY")
            self.connect.execute("CREATE UNIQUE INDEX IF NOT EXISTS JOB_ANL_SIMILARITY_IDX ON JOB_ANL_SIMILARITY (job_id)")
            logging.info("Success: CREATE UNIQUE INDEX IF NOT EXISTS JOB_ANL_SIMILARITY_IDX ON JOB_ANL_SIMILARITY")

            # self.connect.execute("""
            #                     CREATE TABLE IF NOT EXISTS JOB_COLLOCATIONS (
            #                         job_id                          INTEGER
            #                                         REFERENCES JOB_RAW_DATA(job_id) ON DELETE CASCADE ,
            #                         hash_relevant                   varchar(200),
            #                         hash_irrelevant                 varchar(200),
            #                         cosine_relevant                 number(10, 8),
            #                         cosine_irrelevant               number(10, 8),
            #                         updated_at                      datetime
            #                     );
            #                 """)
            # logging.info("Success: CREATE TABLE IF NOT EXISTS JOB_ANL_SIMILARITY")
            # self.connect.execute("CREATE UNIQUE INDEX IF NOT EXISTS JOB_ANL_SIMILARITY_IDX ON JOB_ANALYSIS (job_id)")
            # logging.info("Success: CREATE UNIQUE INDEX IF NOT EXISTS JOB_ANL_SIMILARITY_IDX ON JOB_ANL_SIMILARITY")
        except Exception as ex:
            traceback.print_exception(ex)
            logging.error(traceback.format_exception(ex))
            raise ex

    def info(self):
        data_from_sql = self.connect.execute("SELECT * FROM  sqlite_schema WHERE  type ='table'")
        fetchall = data_from_sql.fetchall()
        for i in fetchall:
            logging.debug(i)
