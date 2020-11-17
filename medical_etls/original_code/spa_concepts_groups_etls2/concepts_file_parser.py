import utils

PXORDX=0
OLDPXORDX=1
CODETYPE=2
CONCEPT_CLASS_ID=3
CONCEPT_ID=4
VOCABULARY_ID=5
DOMAIN_ID=6
TRACK=7
STANDARD_CONCEPT=8
CODE=9
CODEWITHPERIODS=10
CODESCHEME=11
LONG_DESC=12
SHORT_DESC=13
CODE_STATUS=14
CODE_CHANGE=15
CODE_CHANGE_YEAR=16
CODE_PLANNED_TYPE=17
CODE_BILLING_STATUS=18
CODE_CMS_CLAIM_STATUS=19
SEX_CD=20
ROOT1_CD=21
ROOT1_DESC=22
ROOT2_CD=23
ROOT2_DESC=24
ROOT3_CD=25
ROOT3_DESC=26
ROOT4_CD=27
ROOT4_DESC=28
ROOT5_CD=29
ROOT5_DESC=30
ROOT6_CD=31
ROOT6_DESC=32
ROOT7_CD=33
ROOT7_DESC=34
ROOT8_CD=35
ROOT8_DESC=36
ROOT9_CD=37
ROOT9_DESC=38
ROOT10_CD=39
ROOT10_DESC=40
ANAT_OR_COND=41
PL_COND_CLSS_CD1=42
PL_COND_CLSS_DESC1=43
PL_COND_CLSS_CD2=44
PL_COND_CLSS_DESC2=45
PL_COND_CLSS_CD3=46
PL_COND_CLSS_DESC3=47
PL_COND_CLSS_CD4=48
PL_COND_CLSS_DESC4=49
POA_CODE_STATUS=50
POA_CODE_CHANGE=51
POA_CODE_CHANGE_YEAR=52
VALID_START_DATE=53
VALID_END_DATE=54
INVALID_REASON=55
CREATE_DATE=56
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         

# def get_unique_domains(file_path):
#     seq = utils.read_csv_file(file_path, delimiter='\t')
#     domains = map(lambda t: _create_domain(t), seq)
#     return {utils.get_domain_key(d): d for d in domains}.values()

# def _create_domain(item):
#     dict
#     return dict(name=utils.get_value_or_default(item[DOMAIN_ID]))

# def get_concepts(file_path):
#     seq = utils.read_csv_file(file_path, delimiter='\t')
#     return map(_create_concept, seq)

def get_root_hierarchy(item):
    return dict(root_cd1=utils.get_value_or_default(item[ROOT1_CD]),
                root_description1=utils.get_value_or_default(item[ROOT1_DESC]),
                root_cd2=utils.get_value_or_default(item[ROOT2_CD]),
                root_description2=utils.get_value_or_default(item[ROOT2_DESC]),
                root_cd3=utils.get_value_or_default(item[ROOT3_CD]),
                root_description3=utils.get_value_or_default(item[ROOT3_DESC]),
                root_cd4=utils.get_value_or_default(item[ROOT4_CD]),
                root_description4=utils.get_value_or_default(item[ROOT4_DESC]),
                root_cd5=utils.get_value_or_default(item[ROOT5_CD]),
                root_description5=utils.get_value_or_default(item[ROOT5_DESC]),
                root_cd6=utils.get_value_or_default(item[ROOT6_CD]),
                root_description6=utils.get_value_or_default(item[ROOT6_DESC]),
                root_cd7=utils.get_value_or_default(item[ROOT7_CD]),
                root_description7=utils.get_value_or_default(item[ROOT7_DESC]),
                root_cd8=utils.get_value_or_default(item[ROOT8_CD]),
                root_description8=utils.get_value_or_default(item[ROOT8_DESC]),
                root_cd9=utils.get_value_or_default(item[ROOT9_CD]),
                root_description9=utils.get_value_or_default(item[ROOT9_DESC]),
                root_cd10=utils.get_value_or_default(item[ROOT10_CD]),
                root_description10=utils.get_value_or_default(item[ROOT10_DESC]))

def get_concept(item):
    return dict(pxordx=utils.get_value_or_default(item[PXORDX]),
                old_pxordx=utils.get_value_or_default(item[OLDPXORDX]),
                code_type=utils.get_value_or_default(item[CODETYPE]),
                concept_class_id=utils.get_value_or_default(item[CONCEPT_CLASS_ID]),
                concept_id=utils.get_value_or_default(item[CONCEPT_ID]),
                vocabulary_id = utils.get_value_or_default(item[VOCABULARY_ID]),
                domain_id=utils.get_value_or_default(item[DOMAIN_ID]),
                track=utils.get_value_or_default(item[TRACK]),
                standard_concept=utils.get_value_or_default(item[STANDARD_CONCEPT]),
                code=utils.get_value_or_default(item[CODE]),
                code_with_periods=utils.get_value_or_default(item[CODEWITHPERIODS]),
                code_scheme=utils.get_value_or_default(item[CODESCHEME]),
                long_description=utils.get_value_or_default(item[LONG_DESC]),
                short_description=utils.get_value_or_default(item[SHORT_DESC]),
                code_status=utils.get_value_or_default(item[CODE_STATUS]),
                code_change=utils.get_value_or_default(item[CODE_CHANGE]),
                code_change_year=utils.try_convert_int(item[CODE_CHANGE_YEAR]),
                code_planned_type=utils.get_value_or_default(item[CODE_PLANNED_TYPE]),
                code_billing_status=utils.try_convert_bool(item[CODE_BILLING_STATUS]),
                code_cms_claim_status=utils.try_convert_bool(item[CODE_CMS_CLAIM_STATUS]),
                sex_code=utils.get_value_or_default(item[SEX_CD]),
                #roots=_create_root_hierarchy(item),
                anatomy_or_condition=utils.get_value_or_default(item[ANAT_OR_COND]),
                pl_condition_class_code1=utils.get_value_or_default(item[PL_COND_CLSS_CD1]),
                pl_condition_class_description1=utils.get_value_or_default(item[PL_COND_CLSS_DESC1]),
                pl_condition_class_code2=utils.get_value_or_default(item[PL_COND_CLSS_CD2]),
                pl_condition_class_description2=utils.get_value_or_default(item[PL_COND_CLSS_DESC2]),
                pl_condition_class_code3=utils.get_value_or_default(item[PL_COND_CLSS_CD3]),
                pl_condition_class_description3=utils.get_value_or_default(item[PL_COND_CLSS_DESC3]),
                pl_condition_class_code4=utils.get_value_or_default(item[PL_COND_CLSS_CD4]),
                pl_condition_class_description4=utils.get_value_or_default(item[PL_COND_CLSS_DESC4]),
                poa_code_status=utils.get_value_or_default(item[POA_CODE_STATUS]),
                poa_code_change=utils.get_value_or_default(item[POA_CODE_CHANGE]),
                poa_code_change_year=utils.try_convert_int(item[POA_CODE_CHANGE_YEAR]),
                valid_start_date=utils.try_convert_date(value=item[VALID_START_DATE], value_format='%Y%m%d'),
                valid_end_date=utils.try_convert_date(value=item[VALID_END_DATE], value_format='%Y%m%d'),
                invalid_reason=utils.get_value_or_default(item[INVALID_REASON]))
