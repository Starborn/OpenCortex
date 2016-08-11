import opencortex.build as oc
import sys

'''
Simple network using cells from ACNet model

'''


def generate(reference = "ACNet",
             num_pyr = 48,
             num_bask = 12,
             scalex=1,
             scaley=1,
             scalez=1,
             connections=True,
             global_delay = 0,
             duration = 1000,
             format='xml'):


    nml_doc, network = oc.generate_network(reference)

    oc.add_cell_and_channels(nml_doc, 'acnet2/pyr_4_sym.cell.nml','pyr_4_sym')
    oc.add_cell_and_channels(nml_doc, 'acnet2/bask.cell.nml','bask')
    
    xDim = 500*scalex
    yDim = 50*scaley
    zDim = 500*scalez

    pop_pyr = oc.add_population_in_rectangular_region(network, 'pop_pyr',
                                                  'pyr_4_sym', num_pyr,
                                                  0,0,0, xDim,yDim,zDim)

    pop_bask = oc.add_population_in_rectangular_region(network, 'pop_bask',
                                                  'bask', num_bask,
                                                  0,yDim,0, xDim,yDim+yDim,zDim)

    ampa_syn = oc.add_exp_two_syn(nml_doc, id="AMPA_syn", 
                             gbase="30e-9S", erev="0mV",
                             tau_rise="0.003s", tau_decay="0.0031s")

    ampa_syn_inh = oc.add_exp_two_syn(nml_doc, id="AMPA_syn_inh", 
                             gbase="0.15e-9S", erev="0mV",
                             tau_rise="0.003s", tau_decay="0.0031s")

    gaba_syn = oc.add_exp_two_syn(nml_doc, id="GABA_syn", 
                             gbase="0.6e-9S", erev="-0.080V",
                             tau_rise="0.005s", tau_decay="0.012s")

    gaba_syn_inh = oc.add_exp_two_syn(nml_doc, id="GABA_syn_inh", 
                             gbase="0S", erev="-0.080V",
                             tau_rise="0.003s", tau_decay="0.008s")

    pfs = oc.add_poisson_firing_synapse(nml_doc, id="poissonFiringSyn",
                                       average_rate="30 Hz", synapse_id=ampa_syn.id)

    oc.add_inputs_to_population(network, "Stim0",
                                pop_pyr, pfs.id, all_cells=True)
                                
                                
    total_conns = 0
    if connections:

        this_syn=ampa_syn.id
        proj = oc.add_chem_projection0(nml_doc, 
                                        network,
                                        "Proj_pyr_pyr",
                                        pop_pyr,
                                        pop_pyr,
                                        targeting_mode='convergent',
                                        synapse_list=[this_syn],
                                        pre_segment_group = 'soma_group',
                                        post_segment_group = 'dendrite_group',
                                        number_conns_per_cell=7,
                                        delays_dict = {this_syn:global_delay})
        if proj:                           
            total_conns += len(proj[0].connection_wds)

        this_syn=ampa_syn_inh.id
        proj = oc.add_chem_projection0(nml_doc, 
                                        network,
                                        "Proj_pyr_bask",
                                        pop_pyr,
                                        pop_bask,
                                        targeting_mode='convergent',
                                        synapse_list=[this_syn],
                                        pre_segment_group = 'soma_group',
                                        post_segment_group = 'all',
                                        number_conns_per_cell=21,
                                        delays_dict = {this_syn:global_delay})
        if proj:                           
            total_conns += len(proj[0].connection_wds)

        this_syn=gaba_syn.id
        proj = oc.add_chem_projection0(nml_doc, 
                                        network,
                                        "Proj_bask_pyr",
                                        pop_bask,
                                        pop_pyr,
                                        targeting_mode='convergent',
                                        synapse_list=[this_syn],
                                        pre_segment_group = 'soma_group',
                                        post_segment_group = 'all',
                                        number_conns_per_cell=21,
                                        delays_dict = {this_syn:global_delay})
        if proj:                           
            total_conns += len(proj[0].connection_wds)

        this_syn=gaba_syn_inh.id
        proj = oc.add_chem_projection0(nml_doc, 
                                        network,
                                        "Proj_bask_bask",
                                        pop_bask,
                                        pop_bask,
                                        targeting_mode='convergent',
                                        synapse_list=[this_syn],
                                        pre_segment_group = 'soma_group',
                                        post_segment_group = 'all',
                                        number_conns_per_cell=5,
                                        delays_dict = {this_syn:global_delay})
        if proj:                           
            total_conns += len(proj[0].connection_wds)
        
        
    if num_pyr != 48 or num_bask!=12:
        new_reference = '%s_%scells_%sconns'%(nml_doc.id,num_pyr+num_bask,total_conns)
        network.id = new_reference
        nml_doc.id = new_reference
    nml_file_name = '%s.net.%s'%(network.id,'nml.h5' if format == 'hdf5' else 'nml')
    oc.save_network(nml_doc, 
                    nml_file_name, 
                    validate=(format=='xml'),
                    format = format)

    if format=='xml':
        lems_file_name = oc.generate_lems_simulation(nml_doc, network, 
                                nml_file_name, 
                                duration =      duration, 
                                dt =            0.025)
    else:
        lems_file_name = None
                                
    return nml_doc, nml_file_name, lems_file_name


if __name__ == '__main__':
    
    if '-test' in sys.argv:
        
        generate(num_pyr = 2,
                 num_bask=2,
                 duration = 500,
                 global_delay = 2)
    else:
        generate(global_delay = 1)
