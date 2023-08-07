from lume_lcls_cu_inj_nn.flow import flow, output_variables


def test_flow_execution():
    # This will require defaults for all parameters

    print('Starting Flow')
    print(output_variables)
    
    flow.set_reference_tasks([output_variables])
    flow_run = flow.run(
            **{'distgen:r_dist:sigma_xy:value': 0.3922119814518944,
             'distgen:t_dist:length:value': 5.837769949968263,
             'distgen:total_charge:value': 250.0,
             'SOL1:solenoid_field_scale': 0.22998059682676109,
             'CQ01:b1_gradient': 0.00039223148891580177,
             'SQ01:b1_gradient': -0.006474140400668958,
             'L0A_scale:voltage': 58000000.0,
             'L0A_phase:dtheta0_deg': 2.7935416436475613,
             'L0B_scale:voltage': 70000000.0,
             'L0B_phase:dtheta0_deg': -9.868970006934532,
             'QA01:b1_gradient': 2.148610673734787,
             'QA02:b1_gradient': -2.415736249838486,
             'QE01:b1_gradient': 2.4072092546393677,
             'QE02:b1_gradient': 0.7181288513711621,
             'QE03:b1_gradient': -3.748759799913311,
             'QE04:b1_gradient': 2.3394975820698316
              }
    )

    print(flow_run)

    assert flow_run.is_successful()

print('Before')
print(output_variables)
test_flow_execution()
