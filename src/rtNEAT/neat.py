time_alive_minimum: int = 0
trait_param_mut_prob: float = 0
trait_mutation_power: float = 0 # Power of mutation on a signle trait param 
linktrait_mut_sig: float = 0 # Amount that mutation_num changes for a trait change inside a link
nodetrait_mut_sig: float = 0 # Amount a mutation_num changes on a link connecting a node that changed its trait 
weight_mut_power: float = 0 # The power of a linkweight mutation 
recur_prob: float = 0 # Prob. that a link mutation which doesn't have to be recurrent will be made recurrent 
disjoint_coeff: float = 0
excess_coeff: float = 0
mutataion_difference_coeff: float = 0
compat_threshold: float = 0
age_significance: float = 0 # How much does age matter? 
survival_thresh: float = 0 # Percent of ave fitness for survival 
mutate_only_prob: float = 0 # Prob. of a non-mating reproduction 
mutate_random_trait_prob: float = 0
mutate_link_trait_prob: float = 0
mutate_node_trait_prob: float = 0
mutate_link_weights_prob: float = 0
mutate_toggle_enable_prob: float = 0
mutate_gene_reenable_prob: float = 0
mutate_add_node_prob: float = 0
mutate_add_link_prob: float = 0
interspecies_mate_rate: float = 0 # Prob. of a mate being outside species 
mate_multipoint_prob: float = 0     
mate_multipoint_avg_prob: float = 0
mate_singlepoint_prob: float = 0
mate_only_prob: float = 0 # Prob. of mating without mutation 
recur_only_prob: float = 0  # Probability of forcing selection of ONLY links that are naturally recurrent 
pop_size: int = 0  # Size of population 
dropoff_age: int = 0  # Age where Species starts to be penalized 
newlink_tries: int = 0  # Number of tries mutate_add_link will attempt to find an open link 
print_every: int = 0 # Tells to print population to file every n generations 
babies_stolen: int = 0 # The number of babies to siphen off to the champions 
num_runs: int = 0
