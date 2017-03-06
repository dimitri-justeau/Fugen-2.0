# coding: utf-8

from indicators.patient_indicator import PatientIndicator,\
    DuringPeriodIndicator
from indicators.followed_patients import FollowedPatients


class TbDiagnosisPatients(PatientIndicator):
    """
    Patients who had at least one tb diagnosis since they where included
    in the follow up.
    """

    @classmethod
    def get_key(cls):
        return "TB_DIAGNOSIS"

    def under_arv(self):
        return False

    def filter_patients_dataframe(self, limit_date, start_date=None,
                                  include_null_dates=False):
        followed = FollowedPatients(
            self.patients_dataframe,
            self.visits_dataframe,
            self.patient_drugs_dataframe,
            self.visit_drugs_dataframe
        ).filter_patients_dataframe(
            limit_date,
            start_date=start_date,
            include_null_dates=include_null_dates
        )[0]
        visits = self.filter_visits_by_category(
            limit_date,
            start_date=None,
            include_null_dates=include_null_dates
        )
        visits = visits[visits['tb_diagnosis']]
        visits = visits.groupby('patient_id')['visit_date'].max()
        f_index = followed.index.intersection(visits.index)
        return followed.loc[f_index], visits.loc[f_index]


class TbDiagnosisDuringPeriod(DuringPeriodIndicator):

    def __init__(self, patients_dataframe, visits_dataframe,
                 patient_drugs_dataframe, visit_drugs_dataframe):
        indicator = TbDiagnosisPatients(
            patients_dataframe,
            visits_dataframe,
            patients_dataframe,
            visits_dataframe
        )
        super(TbDiagnosisDuringPeriod, self).__init__(
            indicator,
            patients_dataframe,
            visits_dataframe,
            patient_drugs_dataframe,
            visit_drugs_dataframe
        )

    @classmethod
    def get_key(cls):
        return "TB_DIAGNOSIS_DURING_PERIOD"
