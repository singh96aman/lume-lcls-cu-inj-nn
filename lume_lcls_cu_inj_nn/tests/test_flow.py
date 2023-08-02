from lume_lcls_cu_inj_nn.flow import flow, output_variables


def test_flow_execution():
    # This will require defaults for all parameters

    print('Starting Flow')
    print(output_variables)
    
    flow.set_reference_tasks([output_variables])
    flow_run = flow.run(
            **{
                        "distgen:r_dist:sigma_xy:value": 0.4130,
                        "distgen:total_charge:value": 250.0, 
                        "distgen:t_dist:length:value":7.499772441611215, 
                        "SOL1:solenoid_field_scale": 0.17, 
                        "CQ01:b1_gradient":-0.0074,
                        "SQ01:b1_gradient": -0.0074,
                        "L0A_phase:dtheta0_deg": -8.8997,
                        "L0A_scale:voltage": 70000000.0,
                        "distgen:t_dist:length:value": 7.499772441611215,
                        "L0B_scale:voltage": 0,
                        "L0B_phase:dtheta0_deg": 0,
                        "QA01:b1_gradient": 0,
                        "QA02:b1_gradient": 0,
                        "QE01:b1_gradient": 0,
                        "QE02:b1_gradient": 0,
                        "QE03:b1_gradient": 0,
                        "QE04:b1_gradient": 0                     
        }
    )

    print(flow_run)

    assert flow_run.is_successful()

print('Before')
print(output_variables)
test_flow_execution()
