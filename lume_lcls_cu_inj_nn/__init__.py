from lume_lcls_cu_inj_nn.files import VARIABLE_FILE, CU_INJ_MAPPING_FILE
from lume_model.utils import variables_from_yaml
import pandas as pd

with open(VARIABLE_FILE, "r") as f:
    INPUT_VARIABLES, OUTPUT_VARIABLES = variables_from_yaml(f)

CU_INJ_MAPPING_TABLE = pd.read_csv(CU_INJ_MAPPING_FILE)
CU_INJ_MAPPING_TABLE.set_index("impact_name")


from . import _version
__version__ = _version.get_versions()['version']
