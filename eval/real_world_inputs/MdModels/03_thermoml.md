---
repo: "https://github.com/FAIRChemistry/FAIRFluids"
prefix: "thermoml"
---

# ThermoML
Description

## Root Objects

### DataReport
Description: Contains metadata and experimental context for a dataset related to a fluid system.

- citation
  - Type: Citation
  - Description: Citation information about the data report
- version
  - Type: Version
  - Description: Version information for the data report
- compound
  - Type: Compound[]
  - Description: List of compounds present in the fluid system
- pure_or_mixture_data
  - Type: PureOrMixtureData[]
  - Description: Data for pure substances or mixtures
- reaction_data
  - Type: ReactionData[]
  - Description: Data for chemical reactions

### Version
Description: Version information for the data report.

- n_version_major
  - Type: integer
  - Description: Major version number
- n_version_minor
  - Type: integer
  - Description: Minor version number

### Citation
Description: Contains bibliographic information about the source publication.

- book
  - Type: Book
  - Description: Book publication details
- journal
  - Type: Journal
  - Description: Journal publication details
- thesis
  - Type: Thesis
  - Description: Thesis publication details
- date_cit
  - Type: string
  - Description: Date of the citation
- e_language
  - Type: eLanguage, string
  - Description: Language of publication
- e_source_type
  - Type: eSourceType, string
  - Description: The source status type for a citation
- e_type
  - Type: eType, string
  - Description: The type of publication
- s_abstract
  - Type: string
  - Description: An abstract of the publication
- s_author
  - Type: string[]
  - Description: Author of publication
- s_cas_cit
  - Type: string
  - Description: The Chemical Abstracts Service citation
- s_document_origin
  - Type: string
  - Description: Company, institution, or conference name
- s_doi
  - Type: string
  - Description: DOI
- s_id_num
  - Type: string
  - Description: Identification number, e.g., a patent number or a document number
- s_keyword
  - Type: string[]
  - Description: Keywords associated with the publication
- s_location
  - Type: string
  - Description: Reference to a location
- s_page
  - Type: string
  - Description: Page range where the publication can be found
- s_pub_name
  - Type: string
  - Description: Name of the publication
- s_title
  - Type: string
  - Description: Title of the publication
- s_vol
  - Type: string
  - Description: Volume number
- trc_ref_id
  - Type: TRCRefID
  - Description: TRC reference identifier
- url_cit
  - Type: string
  - Description: URL to the publication
- yr_pub_yr
  - Type: string
  - Description: Publication year

### TRCRefID
Description: TRC reference identifier for distinguishing conflicts.

- n_authorn
  - Type: integer
  - Description: Integer identifier to distinguish conflicts
- s_author1
  - Type: string
  - Description: First 3 characters of Author 1 last name
- s_author2
  - Type: string
  - Description: First 3 characters of Author 2 last name
- yr_yr_pub
  - Type: integer
  - Description: Integer year of publication

### Book
Description: Book publication details.

- s_chapter
  - Type: string
  - Description: Chapter number
- s_edition
  - Type: string
  - Description: Edition number of the book
- s_editor
  - Type: string[]
  - Description: Editor of the book
- s_isbn
  - Type: string
  - Description: The International Standard Book Number
- s_publisher
  - Type: string
  - Description: Publisher name and city

### Journal
Description: Journal publication details.

- s_coden
  - Type: string
  - Description: The CODEN identification of the journal
- s_issn
  - Type: string
  - Description: The International Standard Subscription Number
- s_issue
  - Type: string
  - Description: Issue number, usually indicates month

### Thesis
Description: Thesis publication details.

- s_deg
  - Type: string
  - Description: Academic degree designation, e.g., MS or PhD
- s_deg_inst
  - Type: string
  - Description: Academic degree granting institution
- s_umi_pub_num
  - Type: string
  - Description: University Microfilms International Publication Number

### Compound
Description: Contains metadata for a chemical compound, including identifiers, names, and structural representations.

- biomaterial
  - Type: Biomaterial
  - Description: Biomaterial compound information
- ion
  - Type: Ion
  - Description: Ion compound information
- multicomponent_substance
  - Type: MulticomponentSubstance
  - Description: Multicomponent substance information
- polymer
  - Type: Polymer
  - Description: Polymer compound information
- e_speciation_state
  - Type: eSpeciationState, string
  - Description: Speciation state of the compound
- n_comp_index
  - Type: integer
  - Description: Index to link compounds to data
- n_pub_chem_id
  - Type: integer
  - Description: PubChem compound identifier
- reg_num
  - Type: RegNum
  - Description: Registration number information
- s_cas_name
  - Type: string
  - Description: CAS name of the compound
- s_common_name
  - Type: string[]
  - Description: Common names of the compound
- s_formula_molec
  - Type: string
  - Description: Molecular formula
- s_iupac_name
  - Type: string
  - Description: IUPAC name of the compound
- s_org_id
  - Type: SOrgID[]
  - Description: Organization identifiers
- s_smiles
  - Type: string[]
  - Description: SMILES notation
- s_standard_in_ch_i
  - Type: string
  - Description: Standard InChI string
- s_standard_in_ch_i_key
  - Type: string
  - Description: Standard InChI key
- sample
  - Type: Sample[]
  - Description: Sample information

### RegNum
Description: Registration number information for compounds.

- n_org_num
  - Type: integer
  - Description: Organization number
- n_casr_num
  - Type: integer
  - Description: CAS registry number
- s_organization
  - Type: string
  - Description: Organization name

### SOrgID
Description: Organization identifier information.

- s_org_identifier
  - Type: string
  - Description: Organization identifier
- s_organization
  - Type: string
  - Description: Organization name

### Polymer
Description: Polymer compound information.

- n_deg_of_polymerization_dispersity
  - Type: float
  - Description: Degree of polymerization dispersity
- n_mass_avg_mol_mass
  - Type: float
  - Description: Weight average molecular mass, kg/kmol
- n_molar_mass_dispersity
  - Type: float
  - Description: Molar mass dispersity
- n_number_avg_mol_mass
  - Type: float
  - Description: Number average molecular mass, kg/kmol
- n_peak_avg_mol_mass
  - Type: float
  - Description: Peak average molecular mass, kg/kmol
- n_viscosity_avg_mol_mass
  - Type: float
  - Description: Viscosity average molecular mass, kg/kmol
- n_z_avg_mol_mass
  - Type: float
  - Description: Z average molecular mass, kg/kmol

### Ion
Description: Ion compound information.

- n_charge
  - Type: integer
  - Description: Charge of the ion

### Biomaterial
Description: Biomaterial compound information.

- s_ec_number
  - Type: string
  - Description: EC number
- s_pdb_identifier
  - Type: string
  - Description: PDB identifier

### MulticomponentSubstance
Description: Multicomponent substance information.

- component
  - Type: Component[]
  - Description: List of components
- composition_basis
  - Type: string
  - Description: Composition basis
- type
  - Type: string
  - Description: Type of substance

### Component
Description: Component information for multicomponent substances.

- n_amount
  - Type: float
  - Description: Amount of component
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- n_sample_nm
  - Type: integer
  - Description: Sample number

### Sample
Description: Sample information for compounds.

- n_sample_nm
  - Type: integer
  - Description: Sample number
- component_sample
  - Type: ComponentSample[]
  - Description: Component sample information
- e_source
  - Type: eSource, string
  - Description: Source of the sample
- e_status
  - Type: eStatus, string
  - Description: Status of the sample
- purity
  - Type: Purity[]
  - Description: Purity of the sample

### ComponentSample
Description: Component sample information.

- n_comp_index
  - Type: integer
  - Description: Component index
- n_sample_nm
  - Type: integer
  - Description: Sample number
- reg_num
  - Type: RegNum
  - Description: Registration number

### Purity
Description: Purity information for samples.

- n_halide_mass_per_cent
  - Type: float
  - Description: Mass per cent of halide impurity
- n_halide_mass_per_cent_digits
  - Type: integer
  - Description: Digits for halide mass per cent
- n_halide_mol_per_cent
  - Type: float
  - Description: Mole per cent of halide impurity
- n_halide_mol_per_cent_digits
  - Type: integer
  - Description: Digits for halide mole per cent
- n_purity_mass
  - Type: float
  - Description: Purity value in mass percent
- n_purity_mass_digits
  - Type: integer
  - Description: Digits for purity mass
- n_purity_mol
  - Type: float
  - Description: Purity value in mole percent
- n_purity_mol_digits
  - Type: integer
  - Description: Digits for purity mole
- n_purity_vol
  - Type: float
  - Description: Purity value in volume percent
- n_purity_vol_digits
  - Type: integer
  - Description: Digits for purity volume
- n_step
  - Type: integer
  - Description: Step number
- n_unknown_per_cent
  - Type: float
  - Description: Purity value in not specified percent
- n_unknown_per_cent_digits
  - Type: integer
  - Description: Digits for unknown per cent
- n_water_mass_per_cent
  - Type: float
  - Description: Mass per cent of water
- n_water_mass_per_cent_digits
  - Type: integer
  - Description: Digits for water mass per cent
- n_water_mol_per_cent
  - Type: float
  - Description: Mole per cent of water
- n_water_mol_per_cent_digits
  - Type: integer
  - Description: Digits for water mole per cent
- e_anal_meth
  - Type: eAnalMeth[]
  - Description: Analytical method used to determine purity
- e_purif_method
  - Type: ePurifMethod[]
  - Description: Purification method
- s_anal_meth
  - Type: string[]
  - Description: Analytical method description
- s_purif_method
  - Type: string[]
  - Description: Purification method description

### PureOrMixtureData
Description: Data for pure substances or mixtures.

- component
  - Type: Component[]
  - Description: List of components
- phase_id
  - Type: PhaseID[]
  - Description: Phase identification information
- property
  - Type: Property[]
  - Description: List of properties
- auxiliary_substance
  - Type: AuxiliarySubstance[]
  - Description: Auxiliary substance information
- constraint
  - Type: Constraint[]
  - Description: Constraint information
- date_date_added
  - Type: string
  - Description: Date when data was added
- e_exp_purpose
  - Type: eExpPurpose, string
  - Description: Purpose of measurement
- equation
  - Type: Equation[]
  - Description: Equation information
- n_pure_or_mixture_data_number
  - Type: integer
  - Description: Data number
- num_values
  - Type: NumValues[]
  - Description: Numerical values
- s_compiler
  - Type: string
  - Description: Compiler information
- s_contributor
  - Type: string
  - Description: Contributor information
- variable
  - Type: Variable[]
  - Description: Variable information

### AuxiliarySubstance
Description: Auxiliary substance information.

- e_function
  - Type: eFunction, string
  - Description: Function of the substance
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- s_function
  - Type: string
  - Description: Function description
- e_phase
  - Type: ePhase, string
  - Description: Phase information
- n_sample_nm
  - Type: integer
  - Description: Sample number

### Property
Description: Property information for measurements.

- e_presentation
  - Type: ePresentation, string
  - Description: Presentation method
- n_pressure_digits
  - Type: integer
  - Description: Pressure digits
- n_pressure_pa
  - Type: float
  - Description: Pressure in kPa
- n_prop_number
  - Type: integer
  - Description: Property number
- n_ref_pressure
  - Type: float
  - Description: Reference pressure
- n_ref_pressure_digits
  - Type: integer
  - Description: Reference pressure digits
- n_ref_temp
  - Type: float
  - Description: Reference temperature
- n_ref_temp_digits
  - Type: integer
  - Description: Reference temperature digits
- n_temperature_digits
  - Type: integer
  - Description: Temperature digits
- n_temperature_k
  - Type: float
  - Description: Temperature in K
- property_method_id
  - Type: PropertyMethodID
  - Description: Property method identification
- catalyst
  - Type: Catalyst[]
  - Description: Catalyst information
- combined_uncertainty
  - Type: CombinedUncertainty[]
  - Description: Combined uncertainty information
- curve_dev
  - Type: CurveDev[]
  - Description: Curve deviation information
- e_ref_state_type
  - Type: eRefStateType, string
  - Description: Reference state type
- e_standard_state
  - Type: eStandardState, string
  - Description: Standard state
- prop_device_spec
  - Type: PropDeviceSpec
  - Description: Property device specification
- prop_phase_id
  - Type: PropPhaseID[]
  - Description: Property phase identification
- prop_repeatability
  - Type: PropRepeatability
  - Description: Property repeatability
- prop_uncertainty
  - Type: PropUncertainty[]
  - Description: Property uncertainty
- ref_phase_id
  - Type: RefPhaseID
  - Description: Reference phase identification
- solvent
  - Type: Solvent
  - Description: Solvent information

### ReactionData
Description: Data for chemical reactions.

- e_reaction_type
  - Type: eReactionType, string
  - Description: Type of reaction
- participant
  - Type: Participant[]
  - Description: Reaction participants
- property
  - Type: Property[]
  - Description: Reaction properties
- auxiliary_substance
  - Type: AuxiliarySubstance[]
  - Description: Auxiliary substances
- constraint
  - Type: Constraint[]
  - Description: Reaction constraints
- date_date_added
  - Type: string
  - Description: Date when data was added
- e_exp_purpose
  - Type: eExpPurpose, string
  - Description: Purpose of measurement
- e_reaction_formalism
  - Type: eReactionFormalism, string
  - Description: Reaction formalism
- equation
  - Type: Equation[]
  - Description: Reaction equations
- n_electron_number
  - Type: integer
  - Description: Number of electrons
- n_reaction_data_number
  - Type: integer
  - Description: Reaction data number
- num_values
  - Type: NumValues[]
  - Description: Numerical values
- s_compiler
  - Type: string
  - Description: Compiler information
- s_contributor
  - Type: string
  - Description: Contributor information
- solvent
  - Type: Solvent[]
  - Description: Solvent information
- variable
  - Type: Variable[]
  - Description: Variable information

### Participant
Description: Reaction participant information.

- e_crystal_lattice_type
  - Type: eCrystalLatticeType, string
  - Description: Crystal lattice type
- e_phase
  - Type: ePhase, string
  - Description: Phase information
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- s_phase_description
  - Type: string
  - Description: Phase description
- e_composition_representation
  - Type: eCompositionRepresentation, string
  - Description: Composition representation
- e_standard_state
  - Type: eStandardState, string
  - Description: Standard state
- n_numerical_composition
  - Type: float
  - Description: Numerical composition
- n_sample_nm
  - Type: integer
  - Description: Sample number
- n_stoichiometric_coef
  - Type: float
  - Description: Stoichiometric coefficient

### Catalyst
Description: Catalyst information.

- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- e_phase
  - Type: ePhase, string
  - Description: Phase information

### PhaseID
Description: Phase identification information.

- e_crystal_lattice_type
  - Type: eCrystalLatticeType, string
  - Description: Crystal lattice type
- e_phase
  - Type: ePhase, string
  - Description: Phase information
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- s_phase_description
  - Type: string
  - Description: Phase description

### Constraint
Description: Constraint information.

- constraint_id
  - Type: ConstraintID
  - Description: Constraint identification
- n_constr_digits
  - Type: integer
  - Description: Constraint digits
- n_constraint_value
  - Type: float
  - Description: Constraint value
- constr_device_spec
  - Type: ConstrDeviceSpec
  - Description: Constraint device specification
- constr_repeatability
  - Type: ConstrRepeatability
  - Description: Constraint repeatability
- constr_uncertainty
  - Type: ConstrUncertainty[]
  - Description: Constraint uncertainty
- constraint_phase_id
  - Type: ConstraintPhaseID
  - Description: Constraint phase identification
- n_constraint_number
  - Type: integer
  - Description: Constraint number
- solvent
  - Type: Solvent
  - Description: Solvent information

### Variable
Description: Variable information.

- n_var_number
  - Type: integer
  - Description: Variable number
- variable_id
  - Type: VariableID
  - Description: Variable identification
- solvent
  - Type: Solvent
  - Description: Solvent information
- var_device_spec
  - Type: VarDeviceSpec
  - Description: Variable device specification
- var_phase_id
  - Type: VarPhaseID
  - Description: Variable phase identification
- var_repeatability
  - Type: VarRepeatability
  - Description: Variable repeatability
- var_uncertainty
  - Type: VarUncertainty[]
  - Description: Variable uncertainty

### Solvent
Description: Solvent information.

- e_phase
  - Type: ePhase, string
  - Description: Phase information
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number

### PropertyMethodID
Description: Property method identification information.

- n_comp_index
  - Type: integer
  - Description: Component index
- property_group
  - Type: PropertyGroup
  - Description: Property group information
- reg_num
  - Type: RegNum
  - Description: Registration number

### PropertyGroup
Description: Property group information.

- activity_fugacity_osmotic_prop
  - Type: ActivityFugacityOsmoticProp
  - Description: Activity, fugacity, and osmotic properties
- bio_properties
  - Type: BioProperties
  - Description: Biological properties
- composition_at_phase_equilibrium
  - Type: CompositionAtPhaseEquilibrium
  - Description: Composition at phase equilibrium
- criticals
  - Type: Criticals
  - Description: Critical properties
- excess_partial_apparent_energy_prop
  - Type: ExcessPartialApparentEnergyProp
  - Description: Excess partial apparent energy properties
- heat_capacity_and_derived_prop
  - Type: HeatCapacityAndDerivedProp
  - Description: Heat capacity and derived properties
- phase_transition
  - Type: PhaseTransition
  - Description: Phase transition properties
- reaction_equilibrium_prop
  - Type: ReactionEquilibriumProp
  - Description: Reaction equilibrium properties
- reaction_state_change_prop
  - Type: ReactionStateChangeProp
  - Description: Reaction state change properties
- refraction_surface_tension_sound_speed
  - Type: RefractionSurfaceTensionSoundSpeed
  - Description: Refraction, surface tension, and sound speed
- transport_prop
  - Type: TransportProp
  - Description: Transport properties
- vapor_p_boiling_t_azeotrop_tand_p
  - Type: VaporPBoilingTAzeotropTandP
  - Description: Vapor pressure, boiling temperature, azeotrope temperature and pressure
- volumetric_prop
  - Type: VolumetricProp
  - Description: Volumetric properties

### PropPhaseID
Description: Property phase identification information.

- e_bio_state
  - Type: eBioState, string
  - Description: Biological state
- e_crystal_lattice_type
  - Type: eCrystalLatticeType, string
  - Description: Crystal lattice type
- e_prop_phase
  - Type: ePropPhase, string
  - Description: Property phase
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- s_bio_state
  - Type: string
  - Description: Biological state description
- s_phase_description
  - Type: string
  - Description: Phase description

### RefPhaseID
Description: Reference phase identification information.

- e_crystal_lattice_type
  - Type: eCrystalLatticeType, string
  - Description: Crystal lattice type
- e_ref_phase
  - Type: eRefPhase, string
  - Description: Reference phase
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- s_phase_description
  - Type: string
  - Description: Phase description

### ConstraintID
Description: Constraint identification information.

- constraint_type
  - Type: ConstraintType
  - Description: Constraint type
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number

### ConstraintType
Description: Constraint type information.

- e_bio_variables
  - Type: eBioVariables, string
  - Description: Biological variables
- e_component_composition
  - Type: eComponentComposition, string
  - Description: Component composition
- e_miscellaneous
  - Type: eMiscellaneous, string
  - Description: Miscellaneous constraints
- e_participant_amount
  - Type: eParticipantAmount, string
  - Description: Participant amount
- e_pressure
  - Type: ePressure, string
  - Description: Pressure constraints
- e_solvent_composition
  - Type: eSolventComposition, string
  - Description: Solvent composition
- e_temperature
  - Type: eTemperature, string
  - Description: Temperature constraints

### ConstraintPhaseID
Description: Constraint phase identification information.

- e_constraint_phase
  - Type: eConstraintPhase, string
  - Description: Constraint phase
- e_crystal_lattice_type
  - Type: eCrystalLatticeType, string
  - Description: Crystal lattice type
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- s_phase_description
  - Type: string
  - Description: Phase description

### VariableID
Description: Variable identification information.

- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- variable_type
  - Type: VariableType
  - Description: Variable type

### VariableType
Description: Variable type information.

- e_bio_variables
  - Type: eBioVariables, string
  - Description: Biological variables
- e_component_composition
  - Type: eComponentComposition, string
  - Description: Component composition
- e_miscellaneous
  - Type: eMiscellaneous, string
  - Description: Miscellaneous variables
- e_participant_amount
  - Type: eParticipantAmount, string
  - Description: Participant amount
- e_pressure
  - Type: ePressure, string
  - Description: Pressure variables
- e_solvent_composition
  - Type: eSolventComposition, string
  - Description: Solvent composition
- e_temperature
  - Type: eTemperature, string
  - Description: Temperature variables

### VarPhaseID
Description: Variable phase identification information.

- e_crystal_lattice_type
  - Type: eCrystalLatticeType, string
  - Description: Crystal lattice type
- e_var_phase
  - Type: eVarPhase, string
  - Description: Variable phase
- n_comp_index
  - Type: integer
  - Description: Component index
- reg_num
  - Type: RegNum
  - Description: Registration number
- s_phase_description
  - Type: string
  - Description: Phase description

### NumValues
Description: Numerical values information.

- property_value
  - Type: PropertyValue[]
  - Description: Property values
- variable_value
  - Type: VariableValue[]
  - Description: Variable values

### PropertyValue
Description: Property value information.

- n_prop_digits
  - Type: integer
  - Description: Property digits
- n_prop_number
  - Type: integer
  - Description: Property number
- n_prop_value
  - Type: float
  - Description: Property value
- prop_limit
  - Type: PropLimit
  - Description: Property limit
- combined_uncertainty
  - Type: CombinedUncertainty[]
  - Description: Combined uncertainty
- curve_dev
  - Type: CurveDev[]
  - Description: Curve deviation
- n_prop_device_spec_value
  - Type: float
  - Description: Property device specification value
- prop_repeatability
  - Type: PropRepeatability
  - Description: Property repeatability
- prop_uncertainty
  - Type: PropUncertainty[]
  - Description: Property uncertainty

### VariableValue
Description: Variable value information.

- n_var_digits
  - Type: integer
  - Description: Variable digits
- n_var_number
  - Type: integer
  - Description: Variable number
- n_var_value
  - Type: float
  - Description: Variable value
- n_var_device_spec_value
  - Type: float
  - Description: Variable device specification value
- var_repeatability
  - Type: VarRepeatability
  - Description: Variable repeatability
- var_uncertainty
  - Type: VarUncertainty[]
  - Description: Variable uncertainty

### PropLimit
Description: Property limit information.

- n_prop_limit_digits
  - Type: integer
  - Description: Property limit digits
- n_prop_lower_limit_value
  - Type: float
  - Description: Property lower limit value
- n_prop_upper_limit_value
  - Type: float
  - Description: Property upper limit value

### CombinedUncertainty
Description: Combined uncertainty information.

- e_comb_uncert_eval_method
  - Type: eCombUncertEvalMethod, string
  - Description: Combined uncertainty evaluation method
- n_comb_uncert_assess_num
  - Type: integer
  - Description: Combined uncertainty assessment number
- asym_comb_expand_uncert
  - Type: AsymCombExpandUncert
  - Description: Asymmetric combined expanded uncertainty
- asym_comb_std_uncert
  - Type: AsymCombStdUncert
  - Description: Asymmetric combined standard uncertainty
- n_comb_coverage_factor
  - Type: float
  - Description: Combined coverage factor
- n_comb_expand_uncert_value
  - Type: float
  - Description: Combined expanded uncertainty value
- n_comb_std_uncert_value
  - Type: float
  - Description: Combined standard uncertainty value
- n_comb_uncert_lev_of_confid
  - Type: float
  - Description: Combined uncertainty level of confidence
- s_comb_uncert_eval_method
  - Type: string
  - Description: Combined uncertainty evaluation method description
- s_comb_uncert_evaluator
  - Type: string
  - Description: Combined uncertainty evaluator

### PropUncertainty
Description: Property uncertainty information.

- n_uncert_assess_num
  - Type: integer
  - Description: Uncertainty assessment number
- asym_expand_uncert
  - Type: AsymExpandUncert
  - Description: Asymmetric expanded uncertainty
- asym_std_uncert
  - Type: AsymStdUncert
  - Description: Asymmetric standard uncertainty
- n_coverage_factor
  - Type: float
  - Description: Coverage factor
- n_expand_uncert_value
  - Type: float
  - Description: Expanded uncertainty value
- n_std_uncert_value
  - Type: float
  - Description: Standard uncertainty value
- n_uncert_lev_of_confid
  - Type: float
  - Description: Uncertainty level of confidence
- s_uncert_eval_method
  - Type: string
  - Description: Uncertainty evaluation method
- s_uncert_evaluator
  - Type: string
  - Description: Uncertainty evaluator

### PropRepeatability
Description: Property repeatability information.

- e_repeat_method
  - Type: eRepeatMethod, string
  - Description: Repeat method
- n_prop_repeat_value
  - Type: float
  - Description: Property repeat value
- n_repetitions
  - Type: integer
  - Description: Number of repetitions
- s_repeat_evaluator
  - Type: string
  - Description: Repeat evaluator
- s_repeat_method
  - Type: string
  - Description: Repeat method description

### PropDeviceSpec
Description: Property device specification information.

- e_device_spec_method
  - Type: eDeviceSpecMethod, string
  - Description: Device specification method
- n_device_spec_lev_of_confid
  - Type: float
  - Description: Device specification level of confidence
- s_device_spec_evaluator
  - Type: string
  - Description: Device specification evaluator
- s_device_spec_method
  - Type: string
  - Description: Device specification method description

### CurveDev
Description: Curve deviation information.

- n_curve_dev_assess_num
  - Type: integer
  - Description: Curve deviation assessment number
- n_curve_dev_value
  - Type: float
  - Description: Curve deviation value
- s_curve_spec
  - Type: string
  - Description: Curve specification
- n_curve_rms_dev_value
  - Type: float
  - Description: Curve RMS deviation value
- n_curve_rms_relative_dev_value
  - Type: float
  - Description: Curve RMS relative deviation value
- s_curve_dev_evaluator
  - Type: string
  - Description: Curve deviation evaluator

### ConstrUncertainty
Description: Constraint uncertainty information.

- n_coverage_factor
  - Type: float
  - Description: Coverage factor
- n_expand_uncert_value
  - Type: float
  - Description: Expanded uncertainty value
- n_std_uncert_value
  - Type: float
  - Description: Standard uncertainty value
- n_uncert_lev_of_confid
  - Type: float
  - Description: Uncertainty level of confidence
- s_uncert_eval_method
  - Type: string
  - Description: Uncertainty evaluation method
- s_uncert_evaluator
  - Type: string
  - Description: Uncertainty evaluator

### ConstrRepeatability
Description: Constraint repeatability information.

- e_repeat_method
  - Type: eRepeatMethod, string
  - Description: Repeat method
- n_repeat_value
  - Type: float
  - Description: Repeat value
- n_repetitions
  - Type: integer
  - Description: Number of repetitions
- s_repeat_evaluator
  - Type: string
  - Description: Repeat evaluator
- s_repeat_method
  - Type: string
  - Description: Repeat method description

### ConstrDeviceSpec
Description: Constraint device specification information.

- e_device_spec_method
  - Type: eDeviceSpecMethod, string
  - Description: Device specification method
- n_device_spec_lev_of_confid
  - Type: float
  - Description: Device specification level of confidence
- n_device_spec_value
  - Type: float
  - Description: Device specification value
- s_device_spec_evaluator
  - Type: string
  - Description: Device specification evaluator
- s_device_spec_method
  - Type: string
  - Description: Device specification method description

### VarUncertainty
Description: Variable uncertainty information.

- n_uncert_assess_num
  - Type: integer
  - Description: Uncertainty assessment number
- n_coverage_factor
  - Type: float
  - Description: Coverage factor
- n_expand_uncert_value
  - Type: float
  - Description: Expanded uncertainty value
- n_std_uncert_value
  - Type: float
  - Description: Standard uncertainty value
- n_uncert_lev_of_confid
  - Type: float
  - Description: Uncertainty level of confidence
- s_uncert_eval_method
  - Type: string
  - Description: Uncertainty evaluation method
- s_uncert_evaluator
  - Type: string
  - Description: Uncertainty evaluator

### VarRepeatability
Description: Variable repeatability information.

- e_repeat_method
  - Type: eRepeatMethod, string
  - Description: Repeat method
- n_repetitions
  - Type: integer
  - Description: Number of repetitions
- n_var_repeat_value
  - Type: float
  - Description: Variable repeat value
- s_repeat_evaluator
  - Type: string
  - Description: Repeat evaluator
- s_repeat_method
  - Type: string
  - Description: Repeat method description

### VarDeviceSpec
Description: Variable device specification information.

- e_device_spec_method
  - Type: eDeviceSpecMethod, string
  - Description: Device specification method
- n_device_spec_lev_of_confid
  - Type: float
  - Description: Device specification level of confidence
- s_device_spec_evaluator
  - Type: string
  - Description: Device specification evaluator
- s_device_spec_method
  - Type: string
  - Description: Device specification method description

### AsymCombStdUncert
Description: Asymmetric combined standard uncertainty information.

- n_negative_value
  - Type: float
  - Description: Negative value
- n_positive_value
  - Type: float
  - Description: Positive value

### AsymCombExpandUncert
Description: Asymmetric combined expanded uncertainty information.

- n_negative_value
  - Type: float
  - Description: Negative value
- n_positive_value
  - Type: float
  - Description: Positive value

### AsymStdUncert
Description: Asymmetric standard uncertainty information.

- n_negative_value
  - Type: float
  - Description: Negative value
- n_positive_value
  - Type: float
  - Description: Positive value

### AsymExpandUncert
Description: Asymmetric expanded uncertainty information.

- n_negative_value
  - Type: float
  - Description: Negative value
- n_positive_value
  - Type: float
  - Description: Positive value

### Equation
Description: Equation information.

- e_eq_name
  - Type: eEqName, string
  - Description: Equation name
- s_eq_name
  - Type: string
  - Description: Equation name description
- url_math_source
  - Type: string
  - Description: URL to mathematical source
- covariance
  - Type: Covariance[]
  - Description: Covariance information
- eq_constant
  - Type: EqConstant[]
  - Description: Equation constants
- eq_constraint
  - Type: EqConstraint[]
  - Description: Equation constraints
- eq_parameter
  - Type: EqParameter[]
  - Description: Equation parameters
- eq_property
  - Type: EqProperty[]
  - Description: Equation properties
- eq_variable
  - Type: EqVariable[]
  - Description: Equation variables
- n_covariance_lev_of_confid
  - Type: float
  - Description: Covariance level of confidence

### ActivityFugacityOsmoticProp
Description: Activity, fugacity, and osmotic properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### BioProperties
Description: Biological properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### CompositionAtPhaseEquilibrium
Description: Composition at phase equilibrium.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### Criticals
Description: Critical properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### ExcessPartialApparentEnergyProp
Description: Excess partial apparent energy properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### HeatCapacityAndDerivedProp
Description: Heat capacity and derived properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### PhaseTransition
Description: Phase transition properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### ReactionEquilibriumProp
Description: Reaction equilibrium properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string[]
  - Description: Method name descriptions

### ReactionStateChangeProp
Description: Reaction state change properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string[]
  - Description: Method name descriptions

### RefractionSurfaceTensionSoundSpeed
Description: Refraction, surface tension, and sound speed properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### TransportProp
Description: Transport properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### VaporPBoilingTAzeotropTandP
Description: Vapor pressure, boiling temperature, azeotrope temperature and pressure properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### VolumetricProp
Description: Volumetric properties.

- critical_evaluation
  - Type: CriticalEvaluation
  - Description: Critical evaluation information
- e_method_name
  - Type: eMethodName, string
  - Description: Method name
- e_prop_name
  - Type: ePropName, string
  - Description: Property name
- prediction
  - Type: Prediction
  - Description: Prediction information
- s_method_name
  - Type: string
  - Description: Method name description

### CriticalEvaluation
Description: Critical evaluation information.

- equation_of_state
  - Type: EquationOfState
  - Description: Equation of state information
- multi_prop
  - Type: MultiProp
  - Description: Multiple property information
- single_prop
  - Type: SingleProp
  - Description: Single property information

### Prediction
Description: Prediction information.

- e_prediction_type
  - Type: ePredictionType, string
  - Description: Prediction type
- prediction_method_ref
  - Type: PredictionMethodRef[]
  - Description: Prediction method references
- s_prediction_method_description
  - Type: string
  - Description: Prediction method description
- s_prediction_method_name
  - Type: string
  - Description: Prediction method name

### PredictionMethodRef
Description: Prediction method reference information.

- book
  - Type: Book
  - Description: Book reference
- journal
  - Type: Journal
  - Description: Journal reference
- thesis
  - Type: Thesis
  - Description: Thesis reference
- date_cit
  - Type: string
  - Description: Citation date
- e_language
  - Type: eLanguage, string
  - Description: Language
- e_source_type
  - Type: eSourceType, string
  - Description: Source type
- e_type
  - Type: eType, string
  - Description: Publication type
- s_abstract
  - Type: string
  - Description: Abstract
- s_author
  - Type: string[]
  - Description: Authors
- s_cas_cit
  - Type: string
  - Description: CAS citation
- s_document_origin
  - Type: string
  - Description: Document origin
- s_doi
  - Type: string
  - Description: DOI
- s_id_num
  - Type: string
  - Description: ID number
- s_keyword
  - Type: string[]
  - Description: Keywords
- s_location
  - Type: string
  - Description: Location
- s_page
  - Type: string
  - Description: Page range
- s_pub_name
  - Type: string
  - Description: Publication name
- s_title
  - Type: string
  - Description: Title
- s_vol
  - Type: string
  - Description: Volume
- trc_ref_id
  - Type: TRCRefID
  - Description: TRC reference ID
- url_cit
  - Type: string
  - Description: URL citation
- yr_pub_yr
  - Type: string
  - Description: Publication year

### SingleProp
Description: Single property information.

- eval_single_prop_ref
  - Type: EvalSinglePropRef[]
  - Description: Single property evaluation references
- s_eval_single_prop_description
  - Type: string
  - Description: Single property evaluation description

### MultiProp
Description: Multiple property information.

- eval_multi_prop_ref
  - Type: EvalMultiPropRef[]
  - Description: Multiple property evaluation references
- s_eval_multi_prop_description
  - Type: string
  - Description: Multiple property evaluation description
- s_eval_multi_prop_list
  - Type: string
  - Description: Multiple property evaluation list

### EvalSinglePropRef
Description: Single property evaluation reference information.

- book
  - Type: Book
  - Description: Book reference
- journal
  - Type: Journal
  - Description: Journal reference
- thesis
  - Type: Thesis
  - Description: Thesis reference
- date_cit
  - Type: string
  - Description: Citation date
- e_language
  - Type: eLanguage, string
  - Description: Language
- e_source_type
  - Type: eSourceType, string
  - Description: Source type
- e_type
  - Type: eType, string
  - Description: Publication type
- s_abstract
  - Type: string
  - Description: Abstract
- s_author
  - Type: string[]
  - Description: Authors
- s_cas_cit
  - Type: string
  - Description: CAS citation
- s_document_origin
  - Type: string
  - Description: Document origin
- s_doi
  - Type: string
  - Description: DOI
- s_id_num
  - Type: string
  - Description: ID number
- s_keyword
  - Type: string[]
  - Description: Keywords
- s_location
  - Type: string
  - Description: Location
- s_page
  - Type: string
  - Description: Page range
- s_pub_name
  - Type: string
  - Description: Publication name
- s_title
  - Type: string
  - Description: Title
- s_vol
  - Type: string
  - Description: Volume
- trc_ref_id
  - Type: TRCRefID
  - Description: TRC reference ID
- url_cit
  - Type: string
  - Description: URL citation
- yr_pub_yr
  - Type: string
  - Description: Publication year

### EvalMultiPropRef
Description: Multiple property evaluation reference information.

- book
  - Type: Book
  - Description: Book reference
- journal
  - Type: Journal
  - Description: Journal reference
- thesis
  - Type: Thesis
  - Description: Thesis reference
- date_cit
  - Type: string
  - Description: Citation date
- e_language
  - Type: eLanguage, string
  - Description: Language
- e_source_type
  - Type: eSourceType, string
  - Description: Source type
- e_type
  - Type: eType, string
  - Description: Publication type
- s_abstract
  - Type: string
  - Description: Abstract
- s_author
  - Type: string[]
  - Description: Authors
- s_cas_cit
  - Type: string
  - Description: CAS citation
- s_document_origin
  - Type: string
  - Description: Document origin
- s_doi
  - Type: string
  - Description: DOI
- s_id_num
  - Type: string
  - Description: ID number
- s_keyword
  - Type: string[]
  - Description: Keywords
- s_location
  - Type: string
  - Description: Location
- s_page
  - Type: string
  - Description: Page range
- s_pub_name
  - Type: string
  - Description: Publication name
- s_title
  - Type: string
  - Description: Title
- s_vol
  - Type: string
  - Description: Volume
- trc_ref_id
  - Type: TRCRefID
  - Description: TRC reference ID
- url_cit
  - Type: string
  - Description: URL citation
- yr_pub_yr
  - Type: string
  - Description: Publication year

### EquationOfState
Description: Equation of state information.

- eval_eos_ref
  - Type: EvalEOSRef[]
  - Description: EOS evaluation references
- s_eval_eos_description
  - Type: string
  - Description: EOS evaluation description
- s_eval_eos_name
  - Type: string
  - Description: EOS evaluation name

### EvalEOSRef
Description: EOS evaluation reference information.

- book
  - Type: Book
  - Description: Book reference
- journal
  - Type: Journal
  - Description: Journal reference
- thesis
  - Type: Thesis
  - Description: Thesis reference
- date_cit
  - Type: string
  - Description: Citation date
- e_language
  - Type: eLanguage, string
  - Description: Language
- e_source_type
  - Type: eSourceType, string
  - Description: Source type
- e_type
  - Type: eType, string
  - Description: Publication type
- s_abstract
  - Type: string
  - Description: Abstract
- s_author
  - Type: string[]
  - Description: Authors
- s_cas_cit
  - Type: string
  - Description: CAS citation
- s_document_origin
  - Type: string
  - Description: Document origin
- s_doi
  - Type: string
  - Description: DOI
- s_id_num
  - Type: string
  - Description: ID number
- s_keyword
  - Type: string[]
  - Description: Keywords
- s_location
  - Type: string
  - Description: Location
- s_page
  - Type: string
  - Description: Page range
- s_pub_name
  - Type: string
  - Description: Publication name
- s_title
  - Type: string
  - Description: Title
- s_vol
  - Type: string
  - Description: Volume
- trc_ref_id
  - Type: TRCRefID
  - Description: TRC reference ID
- url_cit
  - Type: string
  - Description: URL citation
- yr_pub_yr
  - Type: string
  - Description: Publication year

### EqProperty
Description: Equation property information.

- n_prop_number
  - Type: integer
  - Description: Property number
- n_pure_or_mixture_data_number
  - Type: integer
  - Description: Pure or mixture data number
- n_reaction_data_number
  - Type: integer
  - Description: Reaction data number
- s_eq_symbol
  - Type: string
  - Description: Equation symbol
- n_eq_prop_index
  - Type: integer[]
  - Description: Equation property index
- n_eq_prop_range_max
  - Type: float
  - Description: Equation property range maximum
- n_eq_prop_range_min
  - Type: float
  - Description: Equation property range minimum
- s_other_prop_unit
  - Type: string
  - Description: Other property unit

### EqConstraint
Description: Equation constraint information.

- n_constraint_number
  - Type: integer
  - Description: Constraint number
- n_pure_or_mixture_data_number
  - Type: integer
  - Description: Pure or mixture data number
- n_reaction_data_number
  - Type: integer
  - Description: Reaction data number
- s_eq_symbol
  - Type: string
  - Description: Equation symbol
- n_eq_constraint_index
  - Type: integer[]
  - Description: Equation constraint index
- n_eq_constraint_range_max
  - Type: float
  - Description: Equation constraint range maximum
- n_eq_constraint_range_min
  - Type: float
  - Description: Equation constraint range minimum
- s_other_constraint_unit
  - Type: string
  - Description: Other constraint unit

### EqVariable
Description: Equation variable information.

- n_pure_or_mixture_data_number
  - Type: integer
  - Description: Pure or mixture data number
- n_reaction_data_number
  - Type: integer
  - Description: Reaction data number
- n_var_number
  - Type: integer
  - Description: Variable number
- s_eq_symbol
  - Type: string
  - Description: Equation symbol
- n_eq_var_index
  - Type: integer[]
  - Description: Equation variable index
- n_eq_var_range_max
  - Type: float
  - Description: Equation variable range maximum
- n_eq_var_range_min
  - Type: float
  - Description: Equation variable range minimum
- s_other_var_unit
  - Type: string
  - Description: Other variable unit

### EqParameter
Description: Equation parameter information.

- n_eq_par_digits
  - Type: integer
  - Description: Equation parameter digits
- n_eq_par_value
  - Type: float
  - Description: Equation parameter value
- s_eq_par_symbol
  - Type: string
  - Description: Equation parameter symbol
- n_eq_par_index
  - Type: integer[]
  - Description: Equation parameter index
- n_eq_par_number
  - Type: integer
  - Description: Equation parameter number

### EqConstant
Description: Equation constant information.

- n_eq_constant_digits
  - Type: integer
  - Description: Equation constant digits
- n_eq_constant_value
  - Type: float
  - Description: Equation constant value
- s_eq_constant_symbol
  - Type: string
  - Description: Equation constant symbol
- n_eq_constant_index
  - Type: integer[]
  - Description: Equation constant index

### Covariance
Description: Covariance information.

- n_covariance_value
  - Type: float
  - Description: Covariance value
- n_eq_par_number1
  - Type: integer
  - Description: First equation parameter number
- n_eq_par_number2
  - Type: integer
  - Description: Second equation parameter number

## Enumerations

### eType

```python
BOOK = 'book'
JOURNAL = 'journal'
REPORT = 'report'
PATENT = 'patent'
THESIS = 'thesis'
CONFERENCEPROCEEDINGS = 'conferenceProceedings'
ARCHIVEDDOCUMENT = 'archivedDocument'
PERSONALCORRESPONDENCE = 'personalCorrespondence'
PUBLISHEDTRANSLATION = 'publishedTranslation'
UNSPECIFIED = 'unspecified'
```

### eSourceType

```python
ORIGINAL = 'Original'
CHEMICALABSTRACTS = 'ChemicalAbstracts'
OTHER = 'Other'
```

### eLanguage

```python
CHINESE = 'Chinese'
ENGLISH = 'English'
FRENCH = 'French'
GERMAN = 'German'
JAPANESE = 'Japanese'
POLISH = 'Polish'
RUSSIAN = 'Russian'
OTHER_LANGUAGE = 'Other language'
```

### eSpeciationState

```python
EQUILIBRIUM = 'equilibrium'
SINGLE_SPECIES = 'single species'
```

### eSource

```python
COMMERCIAL_SOURCE = 'Commercial source'
SYNTHESIZED_BY_THE_AUTHORS = 'Synthesized by the authors'
SYNTHESIZED_BY_OTHERS = 'Synthesized by others'
STANDARD_REFERENCE_MATERIAL_SRM = 'Standard Reference Material (SRM)'
ISOLATED_FROM_A_NATURAL_PRODUCT = 'Isolated from a natural product'
NOT_STATED_IN_THE_DOCUMENT = 'Not stated in the document'
NO_SAMPLE_USED = 'No sample used'
```

### eStatus

```python
UNKNOWN = 'unknown'
NOTDESCRIBED = 'notDescribed'
PREVIOUSPAPER = 'previousPaper'
NOSAMPLE = 'noSample'
```

### ePurifMethod

```python
IMPURITY_ADSORPTION = 'Impurity adsorption'
VACUUM_DEGASIFICATION = 'Vacuum degasification'
CHEMICAL_REAGENT_TREATMENT = 'Chemical reagent treatment'
CRYSTALLIZATION_FROM_MELT = 'Crystallization from melt'
CRYSTALLIZATION_FROM_SOLUTION = 'Crystallization from solution'
LIQUID_CHROMATOGRAPHY = 'Liquid chromatography'
DRIED_WITH_CHEMICAL_REAGENT = 'Dried with chemical reagent'
DRIED_IN_A_DESICCATOR = 'Dried in a desiccator'
DRIED_BY_OVEN_HEATING = 'Dried by oven heating'
DRIED_BY_VACUUM_HEATING = 'Dried by vacuum heating'
DEGASSED_BY_BOILING_OR_ULTRASONICALLY = 'De-gassed by boiling or ultrasonically'
DEGASSED_BY_EVACUATION = 'De-gassed by evacuation'
DEGASSED_BY_FREEZING_AND_MELTING_IN_VACUUM = 'De-gassed by freezing and melting in vacuum'
FRACTIONAL_CRYSTALLIZATION = 'Fractional crystallization'
FRACTIONAL_DISTILLATION = 'Fractional distillation'
MOLECULAR_SIEVE_TREATMENT = 'Molecular sieve treatment'
UNSPECIFIED = 'Unspecified'
PREPARATIVE_GAS_CHROMATOGRAPHY = 'Preparative gas chromatography'
SUBLIMATION = 'Sublimation'
STEAM_DISTILLATION = 'Steam distillation'
SOLVENT_EXTRACTION = 'Solvent extraction'
SALTING_OUT_OF_SOLUTION = 'Salting out of solution'
ZONE_REFINING = 'Zone refining'
OTHER = 'Other'
NONE_USED = 'None used'
```

### eAnalMeth

```python
CHEMICAL_ANALYSIS = 'Chemical analysis'
DIFFERENCE_BETWEEN_BUBBLE_AND_DEW_TEMPERATURES = 'Difference between bubble and dew temperatures'
DENSITY = 'Density'
DSC = 'DSC'
ESTIMATION = 'Estimation'
GAS_CHROMATOGRAPHY = 'Gas chromatography'
FRACTION_MELTING_IN_AN_ADIABATIC_CALORIMETER = 'Fraction melting in an adiabatic calorimeter'
MASS_SPECTROMETRY = 'Mass spectrometry'
NMR_PROTON = 'NMR (proton)'
NMR_OTHER = 'NMR (other)'
NOT_KNOWN = 'Not known'
SPECTROSCOPY = 'Spectroscopy'
THERMAL_ANALYSIS_USING_TEMPERATURETIME_MEASUREMENT = 'Thermal analysis using temperature-time measurement'
ACIDBASE_TITRATION = 'Acid-base titration'
OTHER_TYPES_OF_TITRATION = 'Other types of titration'
MASS_LOSS_ON_DRYING = 'Mass loss on drying'
KARL_FISCHER_TITRATION = 'Karl Fischer titration'
HPLC = 'HPLC'
ION_CHROMATOGRAPHY = 'Ion chromatography'
IONSELECTIVE_ELECTRODE = 'Ion-selective electrode'
CO2_YIELD_IN_COMBUSTION_PRODUCTS = 'CO2 yield in combustion products'
OTHER = 'Other'
ESTIMATED_BY_THE_COMPILER = 'Estimated by the compiler'
STATED_BY_SUPPLIER = 'Stated by supplier'
```

### eFunction

```python
COFACTOR = 'Cofactor'
BUFFER = 'Buffer'
INERT = 'Inert'
```

### eExpPurpose

```python
PRINCIPAL_OBJECTIVE_OF_THE_WORK = 'Principal objective of the work'
SECONDARY_PURPOSE_BYPRODUCT_OF_OTHER_OBJECTIVE = 'Secondary purpose (by-product of other objective)'
DETERMINED_FOR_IDENTIFICATION_OF_A_SYNTHESIZED_COMPOUND = 'Determined for identification of a synthesized compound'
```

### ePropName

```python
THERMODYNAMIC_EQUILIBRIUM_CONSTANT = 'Thermodynamic equilibrium constant'
EQUILIBRIUM_CONSTANT_IN_TERMS_OF_MOLALITY_MOLKGN = 'Equilibrium constant in terms of molality, (mol/kg)^n'
EQUILIBRIUM_CONSTANT_IN_TERMS_OF_AMOUNT_CONCENTRATION_MOLARITY_MOLDM3N = 'Equilibrium constant in terms of amount concentration (molarity), (mol/dm3)^n'
EQUILIBRIUM_CONSTANT_IN_TERMS_OF_PARTIAL_PRESSURE_KPAN = 'Equilibrium constant in terms of partial pressure, kPa^n'
EQUILIBRIUM_CONSTANT_IN_TERMS_OF_MOLE_FRACTION = 'Equilibrium constant in terms of mole fraction'
NATURAL_LOGARITHM_OF_THERMODYNAMIC_EQUILIBRIUM_CONSTANT = 'Natural logarithm of thermodynamic equilibrium constant'
NATURAL_LOGARITHM_OF_EQUILIBRIUM_CONSTANT_IN_TERMS_OF_MOLALITY_MOLKGN = 'Natural logarithm of equilibrium constant in terms of molality, (mol/kg)^n'
NATURAL_LOGARITHM_OF_EQUILIBRIUM_CONSTANT_IN_TERMS_OF_AMOUNT_CONCENTRATION_MOLARITY_MOLDM3N = 'Natural logarithm of equilibrium constant in terms of amount concentration (molarity), (mol/dm3)^n'
NATURAL_LOGARITHM_OF_EQUILIBRIUM_CONSTANT_IN_TERMS_OF_PARTIAL_PRESSURE_KPAN = 'Natural logarithm of equilibrium constant in terms of partial pressure, kPa^n'
NATURAL_LOGARITHM_OF_EQUILIBRIUM_CONSTANT_IN_TERMS_OF_MOLE_FRACTION = 'Natural logarithm of equilibrium constant in terms of mole fraction'
DECADIC_LOGARITHM_OF_THERMODYNAMIC_EQUILIBRIUM_CONSTANT = 'Decadic logarithm of thermodynamic equilibrium constant'
DECADIC_LOGARITHM_OF_EQUILIBRIUM_CONSTANT_IN_TERMS_OF_MOLALITY_MOLKGN = 'Decadic logarithm of equilibrium constant in terms of molality, (mol/kg)^n'
DECADIC_LOGARITHM_OF_EQUILIBRIUM_CONSTANT_IN_TERMS_OF_AMOUNT_CONCENTRATION_MOLARITY_MOLDM3N = 'Decadic logarithm of equilibrium constant in terms of amount concentration (molarity), (mol/dm3)^n'
DECADIC_LOGARITHM_OF_EQUILIBRIUM_CONSTANT_IN_TERMS_OF_PARTIAL_PRESSURE_KPAN = 'Decadic logarithm of equilibrium constant in terms of partial pressure, kPa^n'
DECADIC_LOGARITHM_OF_EQUILIBRIUM_CONSTANT_IN_TERMS_OF_MOLE_FRACTION = 'Decadic logarithm of equilibrium constant in terms of mole fraction'
```

### eMethodName

```python
STATIC_EQUILIBRATION = 'Static equilibration'
DYNAMIC_EQUILIBRATION = 'Dynamic equilibration'
CHROMATOGRAPHY = 'Chromatography'
IR_SPECTROMETRY = 'IR spectrometry'
UV_SPECTROSCOPY = 'UV spectroscopy'
NMR_SPECTROMETRY = 'NMR spectrometry'
TITRATION = 'Titration'
POTENTIAL_DIFFERENCE_OF_AN_ELECTROCHEMICAL_CELL = 'Potential difference of an electrochemical cell'
ANION_EXCHANGE = 'Anion exchange'
CATION_EXCHANGE = 'Cation exchange'
CELL_POTENTIAL_WITH_GLASS_ELECTRODE = 'Cell potential with glass electrode'
CELL_POTENTIAL_WITH_PLATINUM_ELECTRODE = 'Cell potential with platinum electrode'
CELL_POTENTIAL_WITH_QUINHYDRONE_ELECTRODE = 'Cell potential with quinhydrone electrode'
CELL_POTENTIAL_WITH_REDOX_ELECTRODE = 'Cell potential with redox electrode'
COLORIMETRY = 'Colorimetry'
CONDUCTIVITY_MEASUREMENT = 'Conductivity measurement'
COULOMETRY = 'Coulometry'
CRYOSCOPY = 'Cryoscopy'
DISTRIBUTION_BETWEEN_TWO_PHASES = 'Distribution between two phases'
ION_SELECTIVE_ELECTRODE = 'Ion selective electrode'
MOLAR_VOLUME_DETERMINATION = 'Molar volume determination'
POLAROGRAPHY = 'Polarography'
POTENTIOMETRY = 'Potentiometry'
PROTON_RELAXATION = 'Proton relaxation'
RATE_OF_REACTION = 'Rate of reaction'
SOLUBILITY_MEASUREMENT = 'Solubility measurement'
SPECTROPHOTOMETRY = 'Spectrophotometry'
THERMAL_LENSING_SPECTROPHOTOMETRY = 'Thermal lensing spectrophotometry'
TRANSIENT_CONDUCTIVITY_MEASUREMENT = 'Transient conductivity measurement'
SOLVENT_EXTRACTION = 'Solvent extraction'
VOLTAMMETRY = 'Voltammetry'
OTHER = 'Other'
```

### ePredictionType

```python
AB_INITIO = 'Ab initio'
MOLECULAR_DYNAMICS = 'Molecular dynamics'
SEMIEMPIRICAL_QUANTUM_METHODS = 'Semiempirical quantum methods'
MOLECULAR_MECHANICS = 'Molecular mechanics'
STATISTICAL_MECHANICS = 'Statistical mechanics'
CORRESPONDING_STATES = 'Corresponding states'
CORRELATION = 'Correlation'
GROUP_CONTRIBUTION = 'Group contribution'
```

### ePropPhase

```python
CRYSTAL_5 = 'Crystal 5'
CRYSTAL_4 = 'Crystal 4'
CRYSTAL_3 = 'Crystal 3'
CRYSTAL_2 = 'Crystal 2'
CRYSTAL_1 = 'Crystal 1'
CRYSTAL = 'Crystal'
CRYSTAL_OF_UNKNOWN_TYPE = 'Crystal of unknown type'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_1 = 'Crystal of intercomponent compound 1'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_2 = 'Crystal of intercomponent compound 2'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_3 = 'Crystal of intercomponent compound 3'
METASTABLE_CRYSTAL = 'Metastable crystal'
GLASS = 'Glass'
SMECTIC_LIQUID_CRYSTAL = 'Smectic liquid crystal'
SMECTIC_LIQUID_CRYSTAL_1 = 'Smectic liquid crystal 1'
SMECTIC_LIQUID_CRYSTAL_2 = 'Smectic liquid crystal 2'
NEMATIC_LIQUID_CRYSTAL = 'Nematic liquid crystal'
NEMATIC_LIQUID_CRYSTAL_1 = 'Nematic liquid crystal 1'
NEMATIC_LIQUID_CRYSTAL_2 = 'Nematic liquid crystal 2'
CHOLESTERIC_LIQUID_CRYSTAL = 'Cholesteric liquid crystal'
LIQUID_CRYSTAL_OF_UNKNOWN_TYPE = 'Liquid crystal of unknown type'
LIQUID = 'Liquid'
LIQUID_MIXTURE_1 = 'Liquid mixture 1'
LIQUID_MIXTURE_2 = 'Liquid mixture 2'
LIQUID_MIXTURE_3 = 'Liquid mixture 3'
SOLUTION = 'Solution'
SOLUTION_1 = 'Solution 1'
SOLUTION_2 = 'Solution 2'
SOLUTION_3 = 'Solution 3'
SOLUTION_4 = 'Solution 4'
FLUID_SUPERCRITICAL_OR_SUBCRITICAL_PHASES = 'Fluid (supercritical or subcritical phases)'
IDEAL_GAS = 'Ideal gas'
GAS = 'Gas'
AIR_AT_1_ATMOSPHERE = 'Air at 1 atmosphere'
```

### eCrystalLatticeType

```python
CUBIC = 'Cubic'
TETRAGONAL = 'Tetragonal'
HEXAGONAL = 'Hexagonal'
RHOMBOHEDRAL = 'Rhombohedral'
ORTHORHOMBIC = 'Orthorhombic'
MONOCLINIC = 'Monoclinic'
TRICLINIC = 'Triclinic'
```

### eBioState

```python
NATIVE = 'Native'
DENATURATED = 'Denaturated'
```

### ePresentation

```python
DIRECT_VALUE_X = 'Direct value, X'
DIFFERENCE_BETWEEN_UPPER_AND_LOWER_TEMPERATURE_XT2XT1 = 'Difference between upper and lower temperature, X(T2)-X(T1)'
DIFFERENCE_BETWEEN_UPPER_AND_LOWER_PRESSURE_XP2XP1 = 'Difference between upper and lower pressure, X(P2)-X(P1)'
MEAN_BETWEEN_UPPER_AND_LOWER_TEMPERATURE_XT2XT12 = 'Mean between upper and lower temperature, [X(T2)+X(T1)]/2'
DIFFERENCE_WITH_THE_REFERENCE_STATE_XXREF = 'Difference with the reference state, X-X(REF)'
RATIO_WITH_THE_REFERENCE_STATE_XXREF = 'Ratio with the reference state, X/X(REF)'
RATIO_OF_DIFFERENCE_WITH_THE_REFERENCE_STATE_TO_THE_REFERENCE_STATE_XXREFXREF = 'Ratio of difference with the reference state to the reference state, [X-X(REF)]/X(REF)'
```

### eRefStateType

```python
REFERENCE_PHASE_WITH_THE_SAME_COMPOSITION_AT_FIXED_TEMPERATURE_AND_PRESSURE = 'Reference phase with the same composition at fixed temperature and pressure'
REFERENCE_PHASE_WITH_THE_SAME_COMPOSITION_TEMPERATURE_AND_PRESSURE = 'Reference phase with the same composition, temperature and pressure'
REFERENCE_PHASE_AT_FIXED_TEMPERATURE_AND_THE_SAME_PRESSURE = 'Reference phase at fixed temperature and the same pressure'
REFERENCE_PHASE_AT_THE_SAME_TEMPERATURE_AND_FIXED_PRESSURE = 'Reference phase at the same temperature and fixed pressure'
IDEAL_GAS_AT_THE_SAME_AMOUNT_DENSITY_TEMPERATURE_AND_COMPOSITION = 'Ideal gas at the same amount density, temperature, and composition'
IDEAL_MIXTURE_OF_PURE_FLUID_COMPONENTS_AT_THE_SAME_AMOUNT_DENSITY_TEMPERATURE_AND_COMPOSITION = 'Ideal mixture of pure fluid components at the same amount density, temperature, and composition'
PHASE_IN_EQUILIBRIUM_WITH_PRIMARY_PHASE_AT_THE_SAME_TEMPERATURE_AND_PRESSURE = 'Phase in equilibrium with primary phase at the same temperature and pressure'
PURE_COMPONENTS_IN_THE_SAME_PROPORTION_AT_FIXED_TEMPERATURE_AND_PRESSURE = 'Pure components in the same proportion at fixed temperature and pressure'
PURE_COMPONENTS_IN_THE_SAME_PROPORTION_AT_THE_SAME_TEMPERATURE_AND_PRESSURE = 'Pure components in the same proportion at the same temperature and pressure'
PURE_SOLVENT_AT_THE_TEMPERATURE_OF_THE_SAME_PHASE_EQUILIBRIUM = 'Pure solvent at the temperature of the same phase equilibrium'
PURE_SOLVENT_AT_THE_SAME_TEMPERATURE_AND_PRESSURE = 'Pure solvent at the same temperature and pressure'
PURE_SOLUTE_AT_THE_SAME_TEMPERATURE_AND_PRESSURE = 'Pure solute at the same temperature and pressure'
```

### eRefPhase

```python
CRYSTAL_5 = 'Crystal 5'
CRYSTAL_4 = 'Crystal 4'
CRYSTAL_3 = 'Crystal 3'
CRYSTAL_2 = 'Crystal 2'
CRYSTAL_1 = 'Crystal 1'
CRYSTAL = 'Crystal'
CRYSTAL_OF_UNKNOWN_TYPE = 'Crystal of unknown type'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_1 = 'Crystal of intercomponent compound 1'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_2 = 'Crystal of intercomponent compound 2'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_3 = 'Crystal of intercomponent compound 3'
METASTABLE_CRYSTAL = 'Metastable crystal'
GLASS = 'Glass'
SMECTIC_LIQUID_CRYSTAL = 'Smectic liquid crystal'
SMECTIC_LIQUID_CRYSTAL_1 = 'Smectic liquid crystal 1'
SMECTIC_LIQUID_CRYSTAL_2 = 'Smectic liquid crystal 2'
NEMATIC_LIQUID_CRYSTAL = 'Nematic liquid crystal'
NEMATIC_LIQUID_CRYSTAL_1 = 'Nematic liquid crystal 1'
NEMATIC_LIQUID_CRYSTAL_2 = 'Nematic liquid crystal 2'
CHOLESTERIC_LIQUID_CRYSTAL = 'Cholesteric liquid crystal'
LIQUID_CRYSTAL_OF_UNKNOWN_TYPE = 'Liquid crystal of unknown type'
LIQUID = 'Liquid'
LIQUID_MIXTURE_1 = 'Liquid mixture 1'
LIQUID_MIXTURE_2 = 'Liquid mixture 2'
LIQUID_MIXTURE_3 = 'Liquid mixture 3'
SOLUTION = 'Solution'
SOLUTION_1 = 'Solution 1'
SOLUTION_2 = 'Solution 2'
SOLUTION_3 = 'Solution 3'
SOLUTION_4 = 'Solution 4'
FLUID_SUPERCRITICAL_OR_SUBCRITICAL_PHASES = 'Fluid (supercritical or subcritical phases)'
IDEAL_GAS = 'Ideal gas'
GAS = 'Gas'
AIR_AT_1_ATMOSPHERE = 'Air at 1 atmosphere'
```

### eStandardState

```python
PURE_COMPOUND = 'Pure compound'
PURE_LIQUID_SOLUTE = 'Pure liquid solute'
STANDARD_MOLALITY_1_MOLKG_SOLUTE = 'Standard molality (1 mol/kg) solute'
STANDARD_AMOUNT_CONCENTRATION_1_MOLDM3_SOLUTE = 'Standard amount concentration (1 mol/dm3) solute'
INFINITE_DILUTION_SOLUTE = 'Infinite dilution solute'
```

### eCombUncertEvalMethod

```python
PROPAGATION_OF_EVALUATED_STANDARD_UNCERTAINTIES = 'Propagation of evaluated standard uncertainties'
COMPARISON_WITH_REFERENCE_PROPERTY_VALUES = 'Comparison with reference property values'
```

### eRepeatMethod

```python
STANDARD_DEVIATION_OF_A_SINGLE_VALUE_BIASED = 'Standard deviation of a single value (biased)'
STANDARD_DEVIATION_OF_A_SINGLE_VALUE_UNBIASED = 'Standard deviation of a single value (unbiased)'
STANDARD_DEVIATION_OF_THE_MEAN = 'Standard deviation of the mean'
OTHER = 'Other'
```

### eDeviceSpecMethod

```python
SPECIFIED_BY_THE_MANUFACTURER = 'Specified by the manufacturer'
CERTIFIED_OR_CALIBRATED_BY_A_THIRD_PARTY = 'Certified or calibrated by a third party'
CALIBRATED_BY_THE_EXPERIMENTALIST = 'Calibrated by the experimentalist'
```

### ePhase

```python
CRYSTAL_5 = 'Crystal 5'
CRYSTAL_4 = 'Crystal 4'
CRYSTAL_3 = 'Crystal 3'
CRYSTAL_2 = 'Crystal 2'
CRYSTAL_1 = 'Crystal 1'
CRYSTAL = 'Crystal'
CRYSTAL_OF_UNKNOWN_TYPE = 'Crystal of unknown type'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_1 = 'Crystal of intercomponent compound 1'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_2 = 'Crystal of intercomponent compound 2'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_3 = 'Crystal of intercomponent compound 3'
METASTABLE_CRYSTAL = 'Metastable crystal'
GLASS = 'Glass'
SMECTIC_LIQUID_CRYSTAL = 'Smectic liquid crystal'
SMECTIC_LIQUID_CRYSTAL_1 = 'Smectic liquid crystal 1'
SMECTIC_LIQUID_CRYSTAL_2 = 'Smectic liquid crystal 2'
NEMATIC_LIQUID_CRYSTAL = 'Nematic liquid crystal'
NEMATIC_LIQUID_CRYSTAL_1 = 'Nematic liquid crystal 1'
NEMATIC_LIQUID_CRYSTAL_2 = 'Nematic liquid crystal 2'
CHOLESTERIC_LIQUID_CRYSTAL = 'Cholesteric liquid crystal'
LIQUID_CRYSTAL_OF_UNKNOWN_TYPE = 'Liquid crystal of unknown type'
LIQUID = 'Liquid'
LIQUID_MIXTURE_1 = 'Liquid mixture 1'
LIQUID_MIXTURE_2 = 'Liquid mixture 2'
LIQUID_MIXTURE_3 = 'Liquid mixture 3'
SOLUTION = 'Solution'
SOLUTION_1 = 'Solution 1'
SOLUTION_2 = 'Solution 2'
SOLUTION_3 = 'Solution 3'
SOLUTION_4 = 'Solution 4'
FLUID_SUPERCRITICAL_OR_SUBCRITICAL_PHASES = 'Fluid (supercritical or subcritical phases)'
IDEAL_GAS = 'Ideal gas'
GAS = 'Gas'
AIR_AT_1_ATMOSPHERE = 'Air at 1 atmosphere'
```

### eTemperature

```python
TEMPERATURE_K = 'Temperature, K'
UPPER_TEMPERATURE_K = 'Upper temperature, K'
LOWER_TEMPERATURE_K = 'Lower temperature, K'
```

### ePressure

```python
PRESSURE_KPA = 'Pressure, kPa'
PARTIAL_PRESSURE_KPA = 'Partial pressure, kPa'
UPPER_PRESSURE_KPA = 'Upper pressure, kPa'
LOWER_PRESSURE_KPA = 'Lower pressure, kPa'
```

### eComponentComposition

```python
MOLE_FRACTION = 'Mole fraction'
MASS_FRACTION = 'Mass fraction'
MOLALITY_MOLKG = 'Molality, mol/kg'
AMOUNT_CONCENTRATION_MOLARITY_MOLDM3 = 'Amount concentration (molarity), mol/dm3'
VOLUME_FRACTION = 'Volume fraction'
RATIO_OF_AMOUNT_OF_SOLUTE_TO_MASS_OF_SOLUTION_MOLKG = 'Ratio of amount of solute to mass of solution, mol/kg'
RATIO_OF_MASS_OF_SOLUTE_TO_VOLUME_OF_SOLUTION_KGM3 = 'Ratio of mass of solute to volume of solution, kg/m3'
AMOUNT_RATIO_OF_SOLUTE_TO_SOLVENT = 'Amount ratio of solute to solvent'
MASS_RATIO_OF_SOLUTE_TO_SOLVENT = 'Mass ratio of solute to solvent'
VOLUME_RATIO_OF_SOLUTE_TO_SOLVENT = 'Volume ratio of solute to solvent'
INITIAL_MOLE_FRACTION_OF_SOLUTE = 'Initial mole fraction of solute'
FINAL_MOLE_FRACTION_OF_SOLUTE = 'Final mole fraction of solute'
INITIAL_MASS_FRACTION_OF_SOLUTE = 'Initial mass fraction of solute'
FINAL_MASS_FRACTION_OF_SOLUTE = 'Final mass fraction of solute'
INITIAL_MOLALITY_OF_SOLUTE_MOLKG = 'Initial molality of solute, mol/kg'
FINAL_MOLALITY_OF_SOLUTE_MOLKG = 'Final molality of solute, mol/kg'
```

### eSolventComposition

```python
SOLVENT_MOLE_FRACTION = 'Solvent: Mole fraction'
SOLVENT_MASS_FRACTION = 'Solvent: Mass fraction'
SOLVENT_VOLUME_FRACTION = 'Solvent: Volume fraction'
SOLVENT_MOLALITY_MOLKG = 'Solvent: Molality, mol/kg'
SOLVENT_AMOUNT_CONCENTRATION_MOLARITY_MOLDM3 = 'Solvent: Amount concentration (molarity), mol/dm3'
SOLVENT_AMOUNT_RATIO_OF_COMPONENT_TO_OTHER_COMPONENT_OF_BINARY_SOLVENT = 'Solvent: Amount ratio of component to other component of binary solvent'
SOLVENT_MASS_RATIO_OF_COMPONENT_TO_OTHER_COMPONENT_OF_BINARY_SOLVENT = 'Solvent: Mass ratio of component to other component of binary solvent'
SOLVENT_VOLUME_RATIO_OF_COMPONENT_TO_OTHER_COMPONENT_OF_BINARY_SOLVENT = 'Solvent: Volume ratio of component to other component of binary solvent'
SOLVENT_RATIO_OF_AMOUNT_OF_COMPONENT_TO_MASS_OF_SOLVENT_MOLKG = 'Solvent: Ratio of amount of component to mass of solvent, mol/kg'
SOLVENT_RATIO_OF_COMPONENT_MASS_TO_VOLUME_OF_SOLVENT_KGM3 = 'Solvent: Ratio of component mass to volume of solvent, kg/m3'
```

### eMiscellaneous

```python
WAVELENGTH_NM = 'Wavelength, nm'
FREQUENCY_MHZ = 'Frequency, MHz'
MOLAR_VOLUME_M3MOL = 'Molar volume, m3/mol'
SPECIFIC_VOLUME_M3KG = 'Specific volume, m3/kg'
MASS_DENSITY_KGM3 = 'Mass density, kg/m3'
AMOUNT_DENSITY_MOLM3 = 'Amount density, mol/m3'
MOLAR_ENTROPY_JKMOL = 'Molar entropy, J/K/mol'
RELATIVE_ACTIVITY = '(Relative) activity'
ACTIVITY_COEFFICIENT = 'Activity coefficient'
```

### eBioVariables

```python
PH = 'pH'
IONIC_STRENGTH_MOLALITY_BASIS_MOLKG = 'Ionic strength (molality basis), mol/kg'
IONIC_STRENGTH_AMOUNT_CONCENTRATION_BASIS_MOLDM3 = 'Ionic strength (amount concentration basis), mol/dm3'
PC_AMOUNT_CONCENTRATION_BASIS = 'pC (amount concentration basis)'
SOLVENT_PC_AMOUNT_CONCENTRATION_BASIS = 'Solvent: pC (amount concentration basis)'
```

### eParticipantAmount

```python
AMOUNT_MOL = 'Amount, mol'
MASS_KG = 'Mass, kg'
```

### eConstraintPhase

```python
CRYSTAL_5 = 'Crystal 5'
CRYSTAL_4 = 'Crystal 4'
CRYSTAL_3 = 'Crystal 3'
CRYSTAL_2 = 'Crystal 2'
CRYSTAL_1 = 'Crystal 1'
CRYSTAL = 'Crystal'
CRYSTAL_OF_UNKNOWN_TYPE = 'Crystal of unknown type'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_1 = 'Crystal of intercomponent compound 1'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_2 = 'Crystal of intercomponent compound 2'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_3 = 'Crystal of intercomponent compound 3'
METASTABLE_CRYSTAL = 'Metastable crystal'
GLASS = 'Glass'
SMECTIC_LIQUID_CRYSTAL = 'Smectic liquid crystal'
SMECTIC_LIQUID_CRYSTAL_1 = 'Smectic liquid crystal 1'
SMECTIC_LIQUID_CRYSTAL_2 = 'Smectic liquid crystal 2'
NEMATIC_LIQUID_CRYSTAL = 'Nematic liquid crystal'
NEMATIC_LIQUID_CRYSTAL_1 = 'Nematic liquid crystal 1'
NEMATIC_LIQUID_CRYSTAL_2 = 'Nematic liquid crystal 2'
CHOLESTERIC_LIQUID_CRYSTAL = 'Cholesteric liquid crystal'
LIQUID_CRYSTAL_OF_UNKNOWN_TYPE = 'Liquid crystal of unknown type'
LIQUID = 'Liquid'
LIQUID_MIXTURE_1 = 'Liquid mixture 1'
LIQUID_MIXTURE_2 = 'Liquid mixture 2'
LIQUID_MIXTURE_3 = 'Liquid mixture 3'
SOLUTION = 'Solution'
SOLUTION_1 = 'Solution 1'
SOLUTION_2 = 'Solution 2'
SOLUTION_3 = 'Solution 3'
SOLUTION_4 = 'Solution 4'
FLUID_SUPERCRITICAL_OR_SUBCRITICAL_PHASES = 'Fluid (supercritical or subcritical phases)'
IDEAL_GAS = 'Ideal gas'
GAS = 'Gas'
AIR_AT_1_ATMOSPHERE = 'Air at 1 atmosphere'
```

### eVarPhase

```python
CRYSTAL_5 = 'Crystal 5'
CRYSTAL_4 = 'Crystal 4'
CRYSTAL_3 = 'Crystal 3'
CRYSTAL_2 = 'Crystal 2'
CRYSTAL_1 = 'Crystal 1'
CRYSTAL = 'Crystal'
CRYSTAL_OF_UNKNOWN_TYPE = 'Crystal of unknown type'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_1 = 'Crystal of intercomponent compound 1'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_2 = 'Crystal of intercomponent compound 2'
CRYSTAL_OF_INTERCOMPONENT_COMPOUND_3 = 'Crystal of intercomponent compound 3'
METASTABLE_CRYSTAL = 'Metastable crystal'
GLASS = 'Glass'
SMECTIC_LIQUID_CRYSTAL = 'Smectic liquid crystal'
SMECTIC_LIQUID_CRYSTAL_1 = 'Smectic liquid crystal 1'
SMECTIC_LIQUID_CRYSTAL_2 = 'Smectic liquid crystal 2'
NEMATIC_LIQUID_CRYSTAL = 'Nematic liquid crystal'
NEMATIC_LIQUID_CRYSTAL_1 = 'Nematic liquid crystal 1'
NEMATIC_LIQUID_CRYSTAL_2 = 'Nematic liquid crystal 2'
CHOLESTERIC_LIQUID_CRYSTAL = 'Cholesteric liquid crystal'
LIQUID_CRYSTAL_OF_UNKNOWN_TYPE = 'Liquid crystal of unknown type'
LIQUID = 'Liquid'
LIQUID_MIXTURE_1 = 'Liquid mixture 1'
LIQUID_MIXTURE_2 = 'Liquid mixture 2'
LIQUID_MIXTURE_3 = 'Liquid mixture 3'
SOLUTION = 'Solution'
SOLUTION_1 = 'Solution 1'
SOLUTION_2 = 'Solution 2'
SOLUTION_3 = 'Solution 3'
SOLUTION_4 = 'Solution 4'
FLUID_SUPERCRITICAL_OR_SUBCRITICAL_PHASES = 'Fluid (supercritical or subcritical phases)'
IDEAL_GAS = 'Ideal gas'
GAS = 'Gas'
AIR_AT_1_ATMOSPHERE = 'Air at 1 atmosphere'
```

### eEqName

```python
THERMOMLANTOINEVAPORPRESSURE = 'ThermoML.Antoine.VaporPressure'
THERMOMLCUSTOMEXPANSION = 'ThermoML.CustomExpansion'
THERMOMLHELMHOLTZ3GENERALEOS = 'ThermoML.Helmholtz3General.EOS'
THERMOMLHELMHOLTZ4GENERALEOS = 'ThermoML.Helmholtz4General.EOS'
THERMOMLWAGNERLINEARVAPORPRESSURE = 'ThermoML.WagnerLinear.VaporPressure'
THERMOMLWAGNER25LINEARVAPORPRESSURE = 'ThermoML.Wagner25Linear.VaporPressure'
THERMOMLWAGNER36LINEARVAPORPRESSURE = 'ThermoML.Wagner36Linear.VaporPressure'
THERMOMLPOLYNOMIALEXPANSION = 'ThermoML.PolynomialExpansion'
THERMOMLSPANWAGNER12NONPOLAREOS = 'ThermoML.SpanWagner12Nonpolar.EOS'
THERMOMLSPANWAGNER12POLAREOS = 'ThermoML.SpanWagner12Polar.EOS'
```

### eCompositionRepresentation

```python
AMOUNT_RATIO_OF_SOLVENT_TO_PARTICIPANT = 'Amount ratio of solvent to participant'
MOLALITY_AMOUNT_OF_PARTICIPANT_PER_MASS_OF_SOLVENT_MOLKG = 'Molality - amount of participant per mass of solvent, mol/kg'
AMOUNT_OF_PARTICIPANT_PER_MASS_OF_SOLUTION_MOLKG = 'Amount of participant per mass of solution, mol/kg'
AMOUNT_CONCENTRATION_AMOUNT_OF_PARTICIPANT_PER_VOLUME_OF_SOLUTION_MOLDM3 = 'Amount concentration - amount of participant per volume of solution, mol/dm3'
AMOUNT_RATIO_OF_PARTICIPANT_TO_SOLVENT = 'Amount ratio of participant to solvent'
MASS_RATIO_OF_PARTICIPANT_TO_SOLVENT = 'Mass ratio of participant to solvent'
VOLUME_RATIO_OF_PARTICIPANT_TO_SOLVENT = 'Volume ratio of participant to solvent'
MASS_OF_PARTICIPANT_PER_VOLUME_OF_SOLUTION_KGM3 = 'Mass of participant per volume of solution, kg/m3'
```

### eReactionFormalism

```python
CHEMICAL = 'chemical'
BIOCHEMICAL = 'biochemical'
```

### eReactionType

```python
COMBUSTION_WITH_OXYGEN = 'Combustion with oxygen'
ADDITION_OF_VARIOUS_COMPOUNDS_TO_UNSATURATED_COMPOUNDS = 'Addition of various compounds to unsaturated compounds'
ADDITION_OF_WATER_TO_A_LIQUID_OR_SOLID_TO_PRODUCE_A_HYDRATE = 'Addition of water to a liquid or solid to produce a hydrate'
ATOMIZATION_OR_FORMATION_FROM_ATOMS = 'Atomization (or formation from atoms)'
COMBUSTION_WITH_OTHER_ELEMENTS_OR_COMPOUNDS = 'Combustion with other elements or compounds'
ESTERIFICATION = 'Esterification'
EXCHANGE_OF_ALKYL_GROUPS = 'Exchange of alkyl groups'
EXCHANGE_OF_HYDROGEN_ATOMS_WITH_OTHER_GROUPS = 'Exchange of hydrogen (atoms) with other groups'
FORMATION_OF_A_COMPOUND_FROM_ELEMENTS_IN_THEIR_STABLE_STATE = 'Formation of a compound from elements in their stable state'
HALOGENATION_ADDITION_OF_OR_REPLACEMENT_BY_A_HALOGEN = 'Halogenation (addition of or replacement by a halogen)'
HYDROGENATION_ADDITION_OF_HYDROGEN_TO_UNSATURATED_COMPOUNDS = 'Hydrogenation (addition of hydrogen to unsaturated compounds)'
HYDROHALOGENATION = 'Hydrohalogenation'
HYDROLYSIS_OF_IONS = 'Hydrolysis of ions'
OTHER_REACTIONS_WITH_WATER = 'Other reactions with water'
ION_EXCHANGE = 'Ion exchange'
NEUTRALIZATION_REACTION_OF_AN_ACID_WITH_A_BASE = 'Neutralization (reaction of an acid with a base)'
OXIDATION_WITH_OXIDIZING_AGENTS_OTHER_THAN_OXYGEN = 'Oxidation with oxidizing agents other than oxygen'
OXIDATION_WITH_OXYGEN_NOT_COMPLETE = 'Oxidation with oxygen (not complete)'
POLYMERIZATION_ALL_OTHER_TYPES = 'Polymerization (all other types)'
HOMONUCLEAR_DIMERIZATION = 'Homonuclear dimerization'
SOLVOLYIS_SOLVENTS_OTHER_THAN_WATER = 'Solvolyis (solvents other than water)'
STEREOISOMERISM = 'Stereoisomerism'
STRUCTURAL_ISOMERIZATION = 'Structural isomerization'
FORMATION_OF_ION = 'Formation of ion'
OTHER_REACTIONS = 'Other reactions'
```

