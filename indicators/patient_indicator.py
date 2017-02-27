# coding: utf-8

import pandas as pd

from indicators.base_indicator import BaseIndicator


class PatientIndicator(BaseIndicator):
    """
    Indicator on patients. The indicator is a number of patients that match
    some criterion defined by the indicator.
    Patients indicators can be combined to create intersection indicators.
    """

    @classmethod
    def get_key(cls):
        raise NotImplementedError()

    def get_filtered_patients_dataframe(self, limit_date, start_date=None,
                                        gender=None, age_min=None,
                                        age_max=None, include_null_dates=False,
                                        **kwargs):
        return NotImplementedError()

    def get_value(self, limit_date, start_date=None, gender=None,
                  age_min=None, age_max=None, age_is_null=False,
                  include_null_dates=False):
        patients = self.get_filtered_patients_dataframe(
            limit_date,
            start_date=start_date,
            gender=gender,
            age_min=age_min,
            age_max=age_max,
            age_is_null=age_is_null,
            include_null_dates=include_null_dates
        )
        return len(patients)

    def __or__(self, other):
        return UnionPatientIndicator(self, other)

    def __and__(self, other):
        return IntersectionPatientIndicator(self, other)


class UnionPatientIndicator(PatientIndicator):
    """
    Result of the union of two patient indicators, using the | (pipe)
    operator.
    """

    def __init__(self, indicator_a, indicator_b):
        self.indicator_a = indicator_a
        self.indicator_b = indicator_b

    @classmethod
    def get_key(cls):
        raise NotImplementedError()

    def get_filtered_patients_dataframe(self, limit_date, start_date=None,
                                        gender=None, age_min=None,
                                        age_max=None, include_null_dates=False,
                                        **kwargs):
        df_a = self.indicator_a.get_filtered_patients_dataframe(
            limit_date,
            start_date=start_date,
            gender=gender,
            age_min=age_min,
            age_max=age_max,
            include_null_dates=include_null_dates,
            **kwargs
        )
        df_b = self.indicator_b.get_filtered_patients_dataframe(
            limit_date,
            start_date=start_date,
            gender=gender,
            age_min=age_min,
            age_max=age_max,
            include_null_dates=include_null_dates,
            **kwargs
        )
        df_c = pd.merge(
            df_a, df_b,
            left_index=True, right_index=True,
            suffixes=('', '_y'),
            how='outer'
        )
        return df_c[df_a.columns]


class IntersectionPatientIndicator(PatientIndicator):
    """
    Result of the intersection of two patient indicators, using the &
    operator.
    """

    def __init__(self, indicator_a, indicator_b):
        self.indicator_a = indicator_a
        self.indicator_b = indicator_b

    @classmethod
    def get_key(cls):
        raise NotImplementedError()

    def get_filtered_patients_dataframe(self, limit_date, start_date=None,
                                        gender=None, age_min=None,
                                        age_max=None, age_is_null=False,
                                        include_null_dates=False):
        df_a = self.indicator_a.get_filtered_patients_dataframe(
            limit_date,
            start_date=start_date,
            gender=gender,
            age_min=age_min,
            age_max=age_max,
            age_is_null=age_is_null,
            include_null_dates=include_null_dates
        )
        df_b = self.indicator_b.get_filtered_patients_dataframe(
            limit_date,
            start_date=start_date,
            gender=gender,
            age_min=age_min,
            age_max=age_max,
            age_is_null=age_is_null,
            include_null_dates=include_null_dates
        )
        df_c = pd.merge(
            df_a, df_b,
            left_index=True, right_index=True,
            suffixes=('', '_y'),
            how='inner'
        )
        return df_c[df_a.columns]
