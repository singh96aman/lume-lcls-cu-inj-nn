from lume_lcls_cu_inj_nn.files import EPICS_CONFIG_FILE
from epics import PV, dbr
import click
import time
from functools import partial
from lume_services.models import Model
from lume_services.config import configure


import torch, os, json
import matplotlib.pyplot as plt

from lume_model.utils import variables_from_yaml
from lume_model.torch import LUMEModule, PyTorchModel

def monitor_callback(parameter_values, pvname, value, **kwargs):
    parameter_values[pvname] = value


@click.command()
@click.argument("model_id")
@click.argument("deployment_id")
@click.option('--distgen_tdist_length_value', default=3.06083484)
@click.option('--distgen_total_charge_value', default=250.0)
def main(model_id, deployment_id, distgen_tdist_length_value, distgen_total_charge_value):
    global PVNAME_TO_INPUT_MAP

    configure()
    
    PVNAME_TO_INPUT_MAP = json.load(open('lume_lcls_cu_inj_nn/info/pv_mapping.json'))['pv_name_to_sim_name']

    pvs, parameter_values = {}, {}

    for pvname in PVNAME_TO_INPUT_MAP.keys():
        parameter_values[pvname] = None

    parameter_values = {
        'distgen_tdist_length_value' : distgen_tdist_length_value,
        'distgen:total_charge:value' : distgen_total_charge_value
    }
        
    model = Model(model_id = model_id, deployment_id=deployment_id)

    for pvname in PVNAME_TO_INPUT_MAP.keys():
        pvs[pvname] = PV(pvname, auto_monitor=dbr.DBE_VALUE)
        pvs[pvname].add_callback(partial(monitor_callback, parameter_values))

    try:
        while True:
            time.sleep(3)
            print("Evaluating model for:")
            print(parameter_values)
            # only queue model once all have values
            if not any([parameter_val is None for parameter_val in parameter_values.values()]):
                print(parameter_values)
                # blocking call
                model.run(
                    parameters = parameter_values
                )
    except KeyboardInterrupt:
        for pv in pvs.values():
            pv.clear_auto_monitor()



if __name__ == "__main__":
    main()
