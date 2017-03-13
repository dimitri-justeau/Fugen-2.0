# coding: utf-8

import pandas as pd

import constants
import utils


# The driver for accessing the Microsoft Access database #
ACCESS_DRIVER = constants.ACCESS_DRIVER

# The password of the Fuchia database #
FUCHIADB_PASSWORD = constants.FUCHIADB_PASSWORD


PATIENTS_SQL = \
    """
    SELECT TbPatient.FdxReference AS id,
        TbPatient.FdsId AS patient_code,
        TbPatient.FdnHIV AS hiv,
        TbPatient.FdnGender AS gender,
        TbPatient.FdnAge AS age,
        TbPatient.FdnAgeUnit AS age_unit,
        TbPatient.FddAgeDate AS age_date,
        TbPatient.FddBirth AS birth_date,
        TbPatient.FddTransfered AS transfered,
        TbPatient.FddDecentralized AS decentralized,
        TbPatient.FddDead AS dead,
        TbReference.FdnValue AS entry_mode,
        TbReference.FdsLookup as entry_mode_lookup
    FROM TbPatient
    LEFT JOIN TbReference
        ON TbPatient.FdxReferenceModeEntry = TbReference.FdxReference
    """


VISITS_SQL = \
    """
    SELECT TbFollowUp.FdxReference AS id,
        TbFollowUp.FdxReferencePatient AS patient_id,
        TbFollowUp.FddVisit AS visit_date,  /* Datetime */
        TbFollowUp.FddVisitNext AS next_visit_date,  /* Datetime */
        TbFollowUp.FddExamen AS examination_date,  /* Datetime */
        TbFollowUp.FdnLymphocyteCD4 AS cd4,
        TbFollowUp.FdnHIVLoad AS viral_load,
        TbFollowUp.FdcStadeOMS AS stade_oms,
        TbFollowUp.FdnTb AS tb_research,
        TbFollowUp.FdsDiagnosis01 AS diagnosis_1,
        TbFollowUp.FdsDiagnosis02 AS diagnosis_2
    FROM TbFollowUp
    """


VISIT_DRUGS_SQL = \
    """
    SELECT TbFollowUpDrug.FdxReference AS id,
        TbFollowUpDrug.FdxReferenceFollowUp AS visit_id,
        TbFollowUpDrug.FdxReferenceDrug AS drug_id,
        TbFollowUpDrug.FdnPrescription AS prescription_value
    FROM TbFollowUpDrug
    """


PATIENT_DRUGS_SQL = \
    """
    SELECT TbPatientDrug.FdxReference AS id,
        TbPatientDrug.FdxReferencePatient AS patient_id,
        TbPatientDrug.FdxReferenceDrug AS drug_id,
        TbPatientDrug.FddBeginning AS beginning,  /* Datetime */
        TbPatientDrug.FdnDuration AS duration
    FROM TbPatientDrug
    """


VISIT_DIAGNOSIS_SQL = \
    """
    SELECT TbFollowUpDiagnosis.FdxReference AS id,
        TbFollowUpDiagnosis.FdxReferenceFollowUp AS visit_id,
        TbFollowUpDiagnosis.FdxReferenceDiagnosis AS diagnosis_id
    FROM TbFollowUpDiagnosis
    """


VISIT_TB_SQL = \
    """
    SELECT TbFollowUpTb.FdxReference AS id,
        TbFollowUpTb.FdxReferencePatient AS patient_id,
        TbFollowUpTb.FdxReferenceRegime AS regime_id,
        TbFollowUpTb.FddTreatmentFrom AS treatment_start,
        TbFollowUpTb.FddTreatmentTo AS treatment_to
    FROM TbFollowUpTb
    """


def query_patients_dataframe(cursor):
    cursor.execute(PATIENTS_SQL)
    data = cursor.fetchall()
    df = pd.DataFrame.from_records(
        data,
        index='id',
        columns=(
            'id',
            'patient_code',
            'hiv',
            'gender',
            'age',
            'age_unit',
            'age_date',  # Datetime
            'birth_date',  # Datetime
            'transferred',  # Datetime
            'decentralized',  # Datetime
            'dead',  # Datetime
            'entry_mode',
            'entry_mode_lookup'
        )
    )
    df['age_date'] = df['age_date'].apply(utils.to_datetime)
    df['birth_date'] = df['birth_date'].apply(utils.to_datetime)
    df['transferred'] = df['transferred'].apply(utils.to_datetime)
    df['decentralized'] = df['decentralized'].apply(utils.to_datetime)
    df['dead'] = df['dead'].apply(utils.to_datetime)
    df = df.assign(id=df.index)
    return df


def query_visits_dataframe(cursor):
    cursor.execute(VISITS_SQL)
    data = cursor.fetchall()
    df = pd.DataFrame.from_records(
        data,
        index='id',
        columns=(
            'id',
            'patient_id',
            'visit_date',  # Datetime
            'next_visit_date',  # Datetime
            'examination_date',  # Datetime
            'cd4',
            'viral_load',
            'stade_oms',
            'tb_research',
            'diagnosis_1',
            'diagnosis_2'
        )
    )
    df['visit_date'] = df['visit_date'].apply(utils.to_datetime)
    df['next_visit_date'] = df['next_visit_date'].apply(utils.to_datetime)
    df['examination_date'] = df['examination_date'].apply(utils.to_datetime)
    df = df.assign(
        id=df.index,
        tb_diagnosis=False,
        hepatitis_b_diagnosis=False
    )
    # Query diagnosis values
    diagnosis = query_visit_diagnosis_dataframe(cursor)
    # Tb diagnosis
    tb_diagnosis = get_tb_diagnosis_visit_ids(df, diagnosis)
    df.loc[tb_diagnosis, 'tb_diagnosis'] = True
    # Hepatitis B diagnosis
    hep_b_diagnosis = get_hepatitis_b_diagnosis_visit_ids(df, diagnosis)
    df.loc[hep_b_diagnosis, 'hepatitis_b_diagnosis'] = True
    # Tb research
    tb_ns = df['tb_research'] == constants.TB_RESEARCH_NS
    tb_not_ns = df['tb_research'] != constants.TB_RESEARCH_NS
    df.loc[tb_ns, 'tb_research'] = False
    df.loc[tb_not_ns, 'tb_research'] = True
    return df


def query_visit_diagnosis_dataframe(cursor):
    cursor.execute(VISIT_DIAGNOSIS_SQL)
    data = cursor.fetchall()
    df = pd.DataFrame.from_records(
        data,
        index='id',
        columns=(
            'id',
            'visit_id',
            'diagnosis_id'
        )
    )
    df = df.assign(id=df.index)
    return df


def get_tb_diagnosis_visit_ids(visits_df, diagnosis_df):
    c1 = diagnosis_df['diagnosis_id'].isin(constants.TB_DIAGNOSIS)
    d1 = diagnosis_df[c1]
    c2 = visits_df['diagnosis_1'].isin(constants.TB_KEYWORDS)
    c3 = visits_df['diagnosis_2'].isin(constants.TB_KEYWORDS)
    d2 = visits_df[c2 | c3]
    ids1 = pd.Index(d1['visit_id'].unique())
    ids2 = d2.index
    return ids1.union(ids2)


def get_hepatitis_b_diagnosis_visit_ids(visits_df, diagnosis_df):
    c1 = diagnosis_df['diagnosis_id'].isin(constants.HEPATITIS_B_DIAGNOSIS)
    d1 = diagnosis_df[c1]
    c2 = visits_df['diagnosis_1'].isin(constants.HEPATITIS_B_KEYWORDS)
    c3 = visits_df['diagnosis_2'].isin(constants.HEPATITIS_B_KEYWORDS)
    d2 = visits_df[c2 | c3]
    ids1 = pd.Index(d1['visit_id'].unique())
    ids2 = d2.index
    return ids1.union(ids2)


def query_visit_drugs_dataframe(cursor):
    cursor.execute(VISIT_DRUGS_SQL)
    data = cursor.fetchall()
    df = pd.DataFrame.from_records(
        data,
        index='id',
        columns=(
            'id',
            'visit_id',
            'drug_id',
            'prescription_value',
        )
    )
    df = df.assign(id=df.index)
    return df


def query_patient_drugs_dataframe(cursor):
    cursor.execute(PATIENT_DRUGS_SQL)
    data = cursor.fetchall()
    df = pd.DataFrame.from_records(
        data,
        index='id',
        columns=(
            'id',
            'patient_id',
            'drug_id',
            'beginning',  # Datetime
            'duration'
        )
    )
    df['beginning'] = df['beginning'].apply(utils.to_datetime)
    df = df.assign(id=df.index)
    return df


def query_visit_tb_dataframe(cursor):
    cursor.execute(VISIT_TB_SQL)
    data = cursor.fetchall()
    df = pd.DataFrame.from_records(
        data,
        index='id',
        columns=(
            'id',
            'patient_id',
            'regime_id',
            'treatment_start',  # Datetime
            'treatment_to',  # Datetime
        )
    )
    df['treatment_start'] = df['treatment_start'].apply(utils.to_datetime)
    df['treatment_to'] = df['treatment_to'].apply(utils.to_datetime)
    df = df.assign(id=df.index)
    return df