import argparse
import logging

import altair as alt
import pandas

from persistence.DbStructure import DbStructure




class JobsPlot:
    def __init__(self):
        self.db = DbStructure()
        pass

    def run(self):
        my_df = pandas.read_sql_query("""
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

    """, con=self.db.connect)

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

    def build_axis_chart(self):
        my_df = pandas.read_sql_query("""
   
select 
	jrd.job_href , jrd.job_title , jrd.location , jrd.company_name ,
	jas.cosine_relevant as cv_relevant , 
	jaxs1.cosine_relevant as architects, 
	jaxs2.cosine_relevant as developers, 
	jaxs3.cosine_relevant as managers, 
	jaxs4.cosine_relevant as fintech 
from JOB_RAW_DATA jrd 
join JOB_ANL_SIMILARITY jas on jas.job_id = jrd.job_id
join JOB_AXIS_SIMILARITY jaxs1 on jaxs1.job_id  = jrd.job_id and jaxs1.axis='architects.txt'
join JOB_AXIS_SIMILARITY jaxs2 on jaxs2.job_id  = jrd.job_id and jaxs2.axis='developers.txt'
join JOB_AXIS_SIMILARITY jaxs3 on jaxs3.job_id  = jrd.job_id and jaxs3.axis='managers.txt'
join JOB_AXIS_SIMILARITY jaxs4 on jaxs4.job_id  = jrd.job_id and jaxs4.axis='fintech.txt'


            """, con=self.db.connect)

        chart = alt.Chart(my_df).mark_point().encode(
            x='developers',
            y='managers',
            color='cv_relevant',
            size='fintech',
            href='job_href',
            tooltip=['job_title', 'location', 'company_name', 'job_href'],
        ).properties(
            width=800,
            height=600
        ).interactive()

        chart.save('three-axis.html')

if __name__ == '__main__':
    logging.basicConfig(filename='categorize-jobs.py.log', level=logging.DEBUG, filemode="w", encoding="UTF-8")
    argparser = argparse.ArgumentParser(prog='scrap-profiles',
                                        description='omachulski scripts to count update jobs statistics',
                                        epilog='src: https://github.com/OlegMachulskiy/om-play-with-linkedin')
    args = argparser.parse_args()

    jp = JobsPlot()
    jp.run()
    jp.build_axis_chart()
