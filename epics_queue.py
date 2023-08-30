from lume_lcls_cu_inj_nn.files import EPICS_CONFIG_FILE
from epics import PV, dbr
import click
import time
from functools import partial
from lume_services.models import Model
from lume_services.config import configure
import shutil

import torch, os, json, csv
import matplotlib.pyplot as plt

from lume_model.utils import variables_from_yaml
from lume_model.torch import LUMEModule, PyTorchModel

def monitor_callback(parameter_values, pvname, value, **kwargs):
    parameter_values[pvname] = value


def run_batch_processing(model, batch_file_location):
    print('Batch File location Exists - Program will run NN for these entries and archive them. Program will be exited')
    print('So, Please restart to connect to PVs. This is for testing purpose only.')

    input_variables_names, output_variables_names = variables_from_yaml(open("lume_lcls_cu_inj_nn/model/variables.yml"))

    archive_dir = batch_file_location+'/archive'
    
    #To Archive Later
    if not os.path.exists(archive_dir):
        os.mkdir(archive_dir)
    
    for file in os.listdir(batch_file_location):
        print(file)
        if file.endswith(".csv"):
            print('Loading File - ', file)
            file_parameter_inputs = []  
            f = open(batch_file_location+"/"+file, 'r')
            csvreader = csv.reader(f, delimiter=',')
            parameter_values = {}
            for row in csvreader:
                for i, col in enumerate(list(input_variables_names.keys())):
                    parameter_values[col] = float(row[i])
                if len(parameter_values) > 0 :
                    file_parameter_inputs.append(parameter_values)
            f.close()

        if file.endswith(".csv") and len(file_parameter_inputs) > 0:
            for parameter_values in file_parameter_inputs:
                print('Running for - ', parameter_values)
                model.run(parameters = parameter_values)
                time.sleep(3)
    
    for file_name in os.listdir(batch_file_location):
        shutil.move(os.path.join(batch_file_location, file_name), archive_dir)
    
    exit(1)

@click.command()
@click.argument("model_id")
@click.argument("deployment_id")
@click.argument("batch_file_location", default='batch_file_location')
@click.option('--distgen_tdist_length_value', default=3.06083484)
@click.option('--distgen_total_charge_value', default=250.0)
def main(model_id, deployment_id, batch_file_location, distgen_tdist_length_value, distgen_total_charge_value):
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

    if os.path.exists(batch_file_location):
        run_batch_processing(model, batch_file_location)
    
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
