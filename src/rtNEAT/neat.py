    
class Config:
    @staticmethod
    def set_inputs_outputs(num_inputs, num_outputs):
        Config.num_inputs = num_inputs
        Config.num_outputs = num_outputs
        
    @staticmethod
    def configure(
        # Network structures
        num_inputs: int = 96,
        num_outputs: int = 12,
    
        # Mutations
        ## Disable gene
        disable_prob: float = 0.05,
        enable_prob: float = 0.1,
        weight_mutate_power: float = 0.5,
        link_mutate_prob: float = 0.1,
         ## Node mutation
        node_mutate_prob: float = 0.1,
        mutate_bias_prob: float = 0.1,
        ## add link mutation
        new_link_prob: float = 0.1,
        add_link_prob: float = 0.05,
        add_link_tries: int = 20,
        recurrence_only_prob: float = 0,
        # add node mutation
        add_node_prob: float = 0.02,
        
        # Mating
        mate_multipoint_prob: float = 0,
        
        # Compatibility
        disjoint_coeff: float = 1.0,
        excess_coeff: float = 1.0,
        node_diff_coeff: float = 0.5,
        link_diff_coeff: float = 0.5,
        mutation_difference_coeff: float = 0.5,
        compatibility_threshod: float = 3.0,
        ):
        # Network structures
        Config.num_inputs: int = num_inputs
        Config.num_outputs: int = num_outputs
        
        # Mutations
        ## Disable gene
        Config.disable_prob: float = disable_prob
        Config.enable_prob: float = enable_prob
        ## link weight mutation
        Config.weight_mutate_power: float  = weight_mutate_power
        Config.link_mutate_prob: float  = link_mutate_prob
        Config.new_link_prob: float = new_link_prob
        ## Node mutation
        Config.node_mutate_prob: float  = node_mutate_prob
        Config.mutate_bias_prob: float = mutate_bias_prob
        ## add link mutation
        Config.add_link_prob: float = add_link_prob
        Config.add_link_tries: int = add_link_tries
        Config.recurrence_only_prob: float = recurrence_only_prob
        # add node mutation
        Config.add_node_prob: float = add_node_prob
        
        # Mating
        Config.mate_multipoint_prob: float = mate_multipoint_prob
        
        # Compatibility
        Config.disjoint_coeff: float = disjoint_coeff
        Config.excess_coeff: float = excess_coeff
        Config.mutation_difference_coeff: float = mutation_difference_coeff
        Config.compatibility_threshod: float = compatibility_threshod
        Config.node_diff_coeff: float = node_diff_coeff
        Config.link_diff_coeff: float = link_diff_coeff
        
        # Predictions
        """ Config.activation_function: Callable[[float], float] = activation_function
        Config.aggregation_func: Callable[[List[float]], float] = aggregation_func """
    
    
    

class NEAT:
    time_alive_minimum: int = 0
    trait_param_mut_prob: float = 0
    trait_mutation_power: float = 0 # Power of mutation on a signle trait param 
    linktrait_mutation_sig: float = 0 # Amount that mutation_num changes for a trait change inside a link
    nodetrait_mutation_sig: float = 0 # Amount a mutation_num changes on a link connecting a node that changed its trait 
    weight_mutation_power: float = 0 # The power of a linkweight mutation 
    recur_prob: float = 0 # Prob. that a link mutation which doesn't have to be recurrent will be made recurrent 
    disjoint_coeff: float = 1.0
    excess_coeff: float = 1.0
    mutation_difference_coeff: float = 1.0
    compat_threshold: float = 0
    age_significance: float = 0 # How much does age matter? 
    survival_thresh: float = 0 # Percent of ave fitness for survival 
    mutate_only_prob: float = 0 # Prob. of a non-mating reproduction 
    mutate_random_trait_prob: float = 0
    mutate_link_trait_prob: float = 0
    mutate_node_trait_prob: float = 0
    mutate_link_weights_prob: float = 0
    mutate_new_link_prob: float = 0.0
    mutate_toggle_enable_prob: float = 0
    mutate_gene_reenable_prob: float = 0
    mutate_add_node_prob: float = 0
    mutate_add_link_prob: float = 0
    interspecies_mate_rate: float = 0 # Prob. of a mate being outside species 
    mate_multipoint_prob: float = 0     
    mate_multipoint_avg_prob: float = 0
    mate_singlepoint_prob: float = 0
    mate_only_prob: float = 0 # Prob. of mating without mutation 
    recurrence_only_prob: float = 0  # Probability of forcing selection of ONLY links that are naturally recurrent 
    pop_size: int = 0  # Size of population 
    dropoff_age: int = 0  # Age where Species starts to be penalized 
    newlink_tries: int = 0  # Number of tries mutate_add_link will attempt to find an open link 
    print_every: int = 0 # Tells to print population to file every n generations 
    babies_stolen: int = 0 # The number of babies to siphen off to the champions 
    num_runs: int = 0

