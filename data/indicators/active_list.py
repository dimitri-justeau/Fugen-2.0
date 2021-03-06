# coding: utf-8

from dateutil.relativedelta import relativedelta
from data.indicators.arv_started_patients import ArvStartedPatients
from data.indicators.arv_stopped import ArvStopped
from data.indicators.dead_patients import DeadPatients
from data.indicators.lost_patients import LostPatients
from data.indicators.patient_indicator import PatientIndicator

from data.indicators.transferred_patients import TransferredPatients
from utils import getFirstDayOfPeriod, getLastDayOfPeriod


class ActiveList(PatientIndicator):

    def under_arv(self):
        return False

    @classmethod
    def get_key(cls):
        return "ACTIVE_LIST"

    @classmethod
    def get_display_label(cls):
        return "File active"

    def filter_patients_dataframe(self, limit_date, start_date=None,
                                  include_null_dates=False):
        arv_started = ArvStartedPatients(self.fuchia_database)
        dead = DeadPatients(self.fuchia_database)
        transferred = TransferredPatients(self.fuchia_database)
        lost = LostPatients(self.fuchia_database)
        arv_stopped = ArvStopped(self.fuchia_database)
        al = (arv_started & ~dead & ~transferred & ~lost & ~arv_stopped)
        return al.get_filtered_patients_dataframe(
            limit_date,
            start_date=start_date,
            include_null_dates=include_null_dates
        ), None


class PreviousActiveList(ActiveList):

    @classmethod
    def get_key(cls):
        return "PREVIOUS_ACTIVE_LIST"

    @classmethod
    def get_display_label(cls):
        return "File active précédente"

    def filter_patients_dataframe(self, limit_date, start_date=None,
                                  include_null_dates=False):
        n_limit = limit_date - relativedelta(months=1)
        n_start = start_date - relativedelta(months=1)
        return super(PreviousActiveList, self).filter_patients_dataframe(
            getLastDayOfPeriod(n_limit.month, n_limit.year),
            start_date=getFirstDayOfPeriod(n_start.month, n_start.year),
            include_null_dates=include_null_dates
        )
