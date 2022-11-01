import argparse
import logging

import altair as alt
import pandas

from persistence.DbStructure import DbStructure

sql = """
select 
	jrd.job_href , jrd.job_title , jrd.location , jrd.company_name ,
	jak.technically_relevant , jak.position_relevant, jak.area_relevant , jak.relocation_relevant, jak.irrelevant_relevant, 
	jas.cosine_relevant , jas.spacy_relevant , jas.cosine_irrelevant , jas.spacy_irrelevant , 
	jas.spacy_relevant / jas.spacy_irrelevant  as coloring, 
	jas.spacy_relevant / jas.spacy_irrelevant as X, 
	jas.cosine_relevant / jas.cosine_irrelevant as Y
from JOB_RAW_DATA jrd 
join JOB_ANL_KW jak on jak.job_id = jrd.job_id   
join JOB_ANL_SIMILARITY jas on jas.job_id = jrd.job_id

    """


class JobsPlot:
    def __init__(self):
        self.db = DbStructure()
        pass

    def run(self):
        my_df = pandas.read_sql_query(sql, con=self.db.connect)

        # my_df.plot.scatter(x="technically_relevant", y="position_relevant", s=my_df["area_relevant"] * 2000,
        #                    c="relocation_relevant");
        # plt.show()

        chart = alt.Chart(my_df).mark_point().encode(
            x='cosine_relevant',
            y='cosine_irrelevant',
            color='coloring',
            href='job_href',
            tooltip=['job_title', 'location', 'company_name', 'job_href', 'spacy_relevant', 'spacy_irrelevant'],
        ).properties(
            width=800,
            height=600
        ).interactive()

        chart.save('chart.html')


if __name__ == '__main__':
    logging.basicConfig(filename='categorize-jobs.py.log', level=logging.DEBUG, filemode="w", encoding="UTF-8")
    argparser = argparse.ArgumentParser(prog='scrap-profiles',
                                        description='omachulski scripts to count update jobs statistics',
                                        epilog='src: https://github.com/OlegMachulskiy/om-play-with-linkedin')
    args = argparser.parse_args()

    jp = JobsPlot()
    jp.run()
