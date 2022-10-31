import argparse
import logging

import altair as alt
import pandas

from DbStructure import DbStructure

sql = """
select 
	jrd.job_href , jrd.job_title , jrd.location , jrd.company_name ,
	technically_relevant , position_relevant, area_relevant , relocation_relevant, irrelevant_relevant, 
	cosine_similarity, 	ja.collocations , log(1 + cosine_similarity / cosine_irrelevant)  as cosine_irrelevant
from JOB_ANALYSIS ja
join JOB_RAW_DATA jrd on ja.job_id = jrd.job_id   
where ja.cosine_irrelevant<>0  
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
            x='cosine_similarity',
            y='cosine_irrelevant',
            color='technically_relevant',
            href='job_href',
            tooltip=['job_title', 'location', 'company_name', 'job_href'],
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
