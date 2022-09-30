from pkg_resources import resource_filename

VARIABLE_FILE = resource_filename("lume_lcls_cu_inj_nn.files", "variables.yml")

MODEL_FILE = resource_filename(
    "lume_lcls_cu_inj_nn.files", "model_1b_AS_f_xy.h5"
)

CU_INJ_MAPPING_FILE = resource_filename(
    "lume_lcls_cu_inj_nn.files", "cu_inj_impact.csv"
)

EPICS_CONFIG_FILE =resource_filename(
    "lume_lcls_cu_inj_nn.files", "epics_config.yml"
)
