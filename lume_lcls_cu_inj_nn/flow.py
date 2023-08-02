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

@task(log_stdout=True)
def model_predict(input_variables, settings):

    # settings are variables not read from epics
    for setting, value in settings.items():
        input_variables[setting].value = value

    model = LCLSCuInjNN()

    output_variables = model.evaluate(list(input_variables.values()))

    results = {
        var.name: var.value.astype('float64') for var in output_variables
    }

    results["x:y"] = results["x:y"].tolist()


    return results


@task(log_stdout=True)
def preprocessing_task(input_variables):
    # scale all values w.r.t. impact factor
    for var_name, var in input_variables.items():

        # if name included in scaling factors
        if (
            CU_INJ_MAPPING_TABLE["impact_name"]
            .str.contains(var_name, regex=False)
            .any()
        ):

            scaled_val = (
                var.value
                * CU_INJ_MAPPING_TABLE.loc[
                    CU_INJ_MAPPING_TABLE["impact_name"] == var_name, "impact_factor"
                ].item()
            )

            var.value = scaled_val
    print('Hey2')
    print(input_variables)
    return input_variables


@task(log_stdout=True)
def format_result(
    input_variables: Dict[str, InputVariable],
    output_variables,
):
    print('Hey 5')
    output_symbols = ["sigma_x", "sigma_y", "sigma_z", "norm_emit_x", "norm_emit_y"]
    inputs = {var_name: var.value for var_name, var in input_variables.items()}
    outputs = {}
    output_variables = output_variables.tolist()

    
    for i in range(len(output_variables)):
        outputs[output_symbols[i]] = output_variables[i]

    # convert array to list
    #outputs["x:y"] = outputs["x:y"].tolist()

    print('Final Result')
    print(Result(inputs=inputs, outputs=outputs))

    return Result(inputs=inputs, outputs=outputs)


@task(log_stdout=True)
def evaluate(formatted_input_vars):

    print('Hey 3')
    all_input_values = []
    for key in formatted_input_vars:
        all_input_values.append(formatted_input_vars[key].value)

    all_input_values = torch.Tensor([all_input_values])
    
    #model = LCLSCuInjNN()
    import os
    print(os.listdir())

    if os.path.exists('model/'):
        TORCH_MODEL_PATH = 'model/'
    else:
        TORCH_MODEL_PATH = '/lume-lcls-cu-inj-nn/lume_lcls_cu_inj_nn/model/'
    
    input_transformer = torch.load(TORCH_MODEL_PATH+"input_transformer.pt")
    output_transformer = torch.load(TORCH_MODEL_PATH+"output_transformer.pt")
    input_variables, output_variables = variables_from_yaml(open(TORCH_MODEL_PATH+"variables.yml"))

    # create lume model
    lume_model = PyTorchModel(
        model_file=TORCH_MODEL_PATH+"model.pt",
        input_variables=input_variables,
        output_variables=output_variables,
        input_transformers=[input_transformer],
        output_transformers=[output_transformer],
    )
    lume_module = LUMEModule(
        model=lume_model,
        feature_order=lume_model.features,
        output_order=lume_model.outputs,
    )

    with torch.no_grad():
        predictions = lume_module(all_input_values)

    print('Hey 4')
    print(predictions)

    return predictions

save_db_result_task = SaveDBResult(timeout=30)

with Flow("lume-lcls-cu-inj-nn", storage=Module(__name__)) as flow:

    print('Inside flow')
    
    # CONFIGURE LUME-SERVICES
    # see https://slaclab.github.io/lume-services/workflows/#configuring-flows-for-use-with-lume-services
    configure = configure_lume_services()

    # CHECK WHETHER THE FLOW IS RUNNING LOCALLY
    # If the flow runs using a local backend, the results service will not be available
    running_local = check_local_execution()
    running_local.set_upstream(configure)

    input_variable_parameter_dict = {
        var_name: Parameter(var_name, default=var.default)
        for var_name, var in INPUT_VARIABLES.items()
    }

    # ORGANIZE INPUT VARIABLE VALUES LUME-MODEL VARIABLES
    formatted_input_vars = prepare_lume_model_variables(
        input_variable_parameter_dict, INPUT_VARIABLES
    )

    print('Hey1')
    print(formatted_input_vars)

    # Perform scaling of variables
    processed_input_vars = preprocessing_task(formatted_input_vars)
    
    # RUN EVALUATION
    output_variables = evaluate(processed_input_vars)

    # SAVE RESULTS TO RESULTS DATABASE, requires LUME-services results backend 
    with case(running_local, False):
        # CREATE LUME-services Result object
        formatted_result = format_result(
            input_variables=processed_input_vars, output_variables=output_variables
        )

        # RUN DATABASE_SAVE_TASK
        saved_model_rep = save_db_result_task(formatted_result)
        saved_model_rep.set_upstream(configure)


def get_flow():
    return flow
