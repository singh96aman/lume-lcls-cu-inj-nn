from lume_lcls_cu_inj_nn.files import EPICS_CONFIG_FILE
from epics import PV, dbr
import click
import time
from functools import partial
from lume_services.models import Model
from lume_services.config import configure


PVNAME_TO_INPUT_MAP = {
    "ACCL:IN20:300:L0A_ADES": "L0A_scale:voltage",
    "ACCL:IN20:400:L0B_PDES": "L0B_phase:dtheta0_deg",
    "ACCL:IN20:300:L0A_PDES": "L0A_phase:dtheta0_deg",
    "QUAD:IN20:122:BACT": "SQ01:b1_gradient",
    "QUAD:IN20:121:BACT": "CQ01:b1_gradient",
    "SOLN:IN20:121:BACT": "SOL1:solenoid_field_scale",
    "BPMS:IN20:221:TMIT": "distgen:total_charge:value",
    "IRIS:LR20:130:CONFG_SEL": "distgen:r_dist:sigma_xy:value"
}

def monitor_callback(parameter_values, pvname, value, **kwargs):
    parameter_values[pvname] = value


@click.command()
@click.argument("model_id")
@click.argument("deployment_id")
@click.option('--distgen_tdist_length_value', default=7.499772441611215)
@click.option('--end_mean_z', default=4.6147002)
def main(model_id, deployment_id, distgen_tdist_length_value, end_mean_z):
    global PVNAME_TO_INPUT_MAP

    configure()

    pvs = {}
    parameter_values = {
        "distgen:t_dist:length:value" : distgen_tdist_length_value,
        "end_mean_z": end_mean_z,
    }

    for pvname in PVNAME_TO_INPUT_MAP.keys():
        parameter_values[pvname] = None

    model = Model(model_id = model_id, deployment_id=deployment_id)

    for pvname in PVNAME_TO_INPUT_MAP.keys():
        pvs[pvname] = PV(pvname, auto_monitor=dbr.DBE_VALUE)
        pvs[pvname].add_callback(partial(monitor_callback, parameter_values))

    try:
        while True:
            time.sleep(0.1)
            print("Evaluating model for:")
            print(parameter_values)
            # only queue model once all have values
            if not any([parameter_val is None for parameter_val in parameter_values.values()]):

                # blocking call
                model.run(
                    parameters = parameter_values
                )
    except KeyboardInterrupt:
        for pv in pvs.values():
            pv.clear_auto_monitor()



if __name__ == "__main__":
    main()
