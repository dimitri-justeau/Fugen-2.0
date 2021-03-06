# coding: utf-8

from data.indicators.patient_indicator import PatientIndicator,\
    DuringPeriodIndicator

from data.indicators.followed_patients import FollowedPatients


class TbResearchPatients(PatientIndicator):
    """
    Patients who had at least one tb research since they where included
    in the follow up.
    """

    @classmethod
    def get_key(cls):
        return "TB_RESEARCH_ALL"

    @classmethod
    def get_display_label(cls):
        return "Recherche TB (tous jusqu'à la fin de la période)"

    def under_arv(self):
        return False

    def filter_patients_dataframe(self, limit_date, start_date=None,
                                  include_null_dates=False):
        followed = FollowedPatients(
            self.fuchia_database
        ).get_filtered_patients_dataframe(
            limit_date,
            start_date=start_date,
            include_null_dates=include_null_dates
        )
        visits = self.filter_visits_by_category(
            limit_date,
            start_date=None,
            include_null_dates=include_null_dates
        )
        visits = visits[visits['tb_research']]
        visits = visits.groupby('patient_id')['visit_date'].max()
        f_index = followed.index.intersection(visits.index)
        return followed.loc[f_index], visits.loc[f_index]


class TbResearchDuringPeriod(DuringPeriodIndicator):

    def __init__(self, fuchia_database):
        indicator = TbResearchPatients(fuchia_database)
        super(TbResearchDuringPeriod, self).__init__(
            indicator,
            fuchia_database
        )

    @classmethod
    def get_key(cls):
        return "TB_RESEARCH"

    @classmethod
    def get_display_label(cls):
        return "Recherche TB"
