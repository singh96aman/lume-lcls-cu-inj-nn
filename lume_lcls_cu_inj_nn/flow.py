from typing import Dict

from prefect import Flow, task, case
from prefect import Parameter

from lume_services.results import Result
from lume_services.tasks import (
    configure_lume_services,
    prepare_lume_model_variables,
    check_local_execution,
    SaveDBResult,
    LoadDBResult,
    LoadFile,
    SaveFile,
)
from lume_services.files import TextFile
from lume_model.variables import InputVariable, OutputVariable
from prefect.storage import Module

from lume_lcls_cu_inj_nn.model import LCLSCuInjNN
from lume_lcls_cu_inj_nn import INPUT_VARIABLES, CU_INJ_MAPPING_TABLE

import torch
import matplotlib.pyplot as plt

from lume_model.utils import variables_from_yaml
from lume_model.torch import LUMEModule, PyTorchModel
import os

@task(log_stdout=True)
def format_result(
    input_variables: Dict[str, InputVariable],
    output_variables,
    output_variables_names
):
    outputs = {}
    output_variables = output_variables.tolist()
    output_variables_names = list(output_variables_names.keys())
    print('Output Variables List - ', output_variables_names)

    for i in range(len(output_variables)):
        outputs[output_variables_names[i]] = output_variables[i]

    return Result(inputs=input_variables, outputs=outputs)


@task(log_stdout=True)
def evaluate(formatted_input_vars, lume_module):
    all_input_values = []
    for key in formatted_input_vars:
        all_input_values.append(formatted_input_vars[key])

    all_input_values = torch.Tensor([all_input_values])
    with torch.no_grad():
        predictions = lume_module(all_input_values)
    print('Predictions - ', predictions)  
    return predictions

save_db_result_task = SaveDBResult(timeout=30)

@task(log_stdout=True)
def load_input(var_name, parameter):
    #Confirm Inputs are Correctly Loaded!
    print('Loaded ', str(var_name), ' with value - ', parameter)
    return parameter
    

with Flow("lume-lcls-cu-inj-nn", storage=Module(__name__)) as flow:

    print('Starting Flow Run')
    # CONFIGURE LUME-SERVICES
    # see https://slaclab.github.io/lume-services/workflows/#configuring-flows-for-use-with-lume-services
    
    configure = configure_lume_services()

    # CHECK WHETHER THE FLOW IS RUNNING LOCALLY
    # If the flow runs using a local backend, the results service will not be available
    running_local = check_local_execution()
    running_local.set_upstream(configure)

    input_variable_parameter_dict = {}
    
    for var_name, var in INPUT_VARIABLES.items():
        input_variable_parameter_dict[var_name] = load_input(var_name, Parameter(var_name, default=var.default))

    print('Input Variable Parameters - ',input_variable_parameter_dict)
    
    if os.path.exists('model/'):
        TORCH_MODEL_PATH = 'model/'
    elif os.path.exists('/lume-lcls-cu-inj-nn/lume_lcls_cu_inj_nn/model/'):
        #This is the Docker Path
        TORCH_MODEL_PATH = '/lume-lcls-cu-inj-nn/lume_lcls_cu_inj_nn/model/'
    elif os.path.exists('lume_lcls_cu_inj_nn/model/'):
        TORCH_MODEL_PATH = 'lume_lcls_cu_inj_nn/model/'
    else:
        print('Path Not Found')

    print('Reached Here with TORCH MODEL PATH - ', TORCH_MODEL_PATH)
    print(print(os.listdir()))
    
    input_transformer = torch.load(TORCH_MODEL_PATH+"input_transformer.pt")
    output_transformer = torch.load(TORCH_MODEL_PATH+"output_transformer.pt")
    input_variables_names, output_variables_names = variables_from_yaml(open(TORCH_MODEL_PATH+"variables.yml"))

    # create lume model
    lume_model = PyTorchModel(
        model_file=TORCH_MODEL_PATH+"model.pt",
        input_variables=input_variables_names,
        output_variables=output_variables_names,
        input_transformers=[input_transformer],
        output_transformers=[output_transformer],
    )
    lume_module = LUMEModule(
        model=lume_model,
        feature_order=lume_model.features,
        output_order=lume_model.outputs,
    )

    output_variables = evaluate(input_variable_parameter_dict, lume_module)

    # SAVE RESULTS TO RESULTS DATABASE, requires LUME-services results backend 
    with case(running_local, False):
        # CREATE LUME-services Result object
        formatted_result = format_result(
            input_variables=input_variable_parameter_dict, output_variables=output_variables, output_variables_names=output_variables_names
        )

        # RUN DATABASE_SAVE_TASK
        saved_model_rep = save_db_result_task(formatted_result)
        saved_model_rep.set_upstream(configure)


def get_flow():
    return flow
