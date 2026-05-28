# Medical Terminology and Coding Standards

## Standardized Nomenclature Systems

### SNOMED CT (Systematized Nomenclature of Medicine - Clinical Terms)

**Use:** A comprehensive clinical terminology set for electronic health records.

**Scope:**
- Clinical findings
- Symptoms
- Diagnoses
- Procedures/Interventions
- Body structures
- Biological organisms
- Substances
- Pharmaceuticals
- Specimens

**Structure:**
- Concepts with unique identifiers
- Descriptions (Preferred terms and synonyms)
- Relationships between concepts
- Hierarchical organization

**Examples:**
- Concept: Myocardial infarction
- SNOMED CT code: 22298006
- Parent: Heart disease
- Children: Acute myocardial infarction, Old myocardial infarction

**Advantages:**
- Enables semantic interoperability
- Supports Clinical Decision Support (CDS)
- Facilitates data analytics
- International standard

### LOINC (Logical Observation Identifiers Names and Codes)

**Use:** A universal code system for laboratory and clinical observation results.

**Components of a LOINC Code:**
1. **Component** (Analyte or measurement): What is being measured
2. **Property**: Characteristic attribute (Mass, volume, etc.)
3. **Timing**: Time of measurement (Point in time, 24 hours, etc.)
4. **System**: Specimen or system (Serum, urine, arterial blood)
5. **Scale**: Type of result (Quantitative, ordinal, nominal)
6. **Method**: Measurement method (When relevant to interpretation)

**Examples:**
- **Glucose [Mass/volume] in Serum or Plasma**: 2345-7
  - Component: Glucose
  - Property: Mass concentration
  - Timing: Point in time
  - System: Serum/Plasma
  - Scale: Quantitative

- **Hemoglobin A1c/Hemoglobin.total in Blood**: 4548-4
  - Component: Hemoglobin A1c/Hemoglobin.total
  - Property: Mass fraction
  - Timing: Point in time
  - System: Blood
  - Scale: Quantitative

**LOINC Sections:**
- Document types
- Survey instruments
- Clinical attachments
- Radiology codes
- Pathology codes

### ICD-10-CM (International Classification of Diseases, 10th Revision, Clinical Modification)

**Use:** Diagnosis and procedure coding for billing, epidemiology, and health statistics.

**Structure:**
- Alphanumeric codes (3-7 characters)
- 1st character: Letter (except U)
- 2nd-3rd characters: Numbers
- 4th-7th characters: Letters or numbers (decimal point after the 3rd character)
- Specifies laterality, severity, and encounter type

**Code Structure Example:**
- **S72.001A**: Fracture of unspecified part of neck of right femur, initial encounter
  - S: Injury category
  - 72: Femur
  - 001: Unspecified part of neck
  - A: Initial encounter for closed fracture
  - The 1 in the 5th position indicates the right side

**Common Categories:**
- A00-B99: Infectious diseases
- C00-D49: Neoplasms
- E00-E89: Endocrine, nutritional, metabolic
- F01-F99: Mental and behavioral
- G00-G99: Nervous system
- I00-I99: Circulatory system
- J00-J99: Respiratory system
- K00-K95: Digestive system
- M00-M99: Musculoskeletal
- N00-N99: Genitourinary
- S00-T88: Injury, poisoning

**7th Character Extension:**
- A: Initial encounter
- D: Subsequent encounter
- S: Sequela

**Placeholder X:**
- Used when a code requires a 7th character but has fewer than 6 characters.
- Example: T36.0X5A (Adverse effect of penicillins, initial encounter)

**Combination Codes:**
- A single code used to describe two diagnoses or a diagnosis with a manifestation.
- Example: E11.21 (Type 2 diabetes mellitus with diabetic nephropathy)

### CPT (Current Procedural Terminology)

**Use:** Procedure and service coding for billing.

**Maintained by:** American Medical Association (AMA)

**Categories:**
- **Category I**: Procedures and services (5-digit numeric codes)
- **Category II**: Performance measurement (4 digits + F)
- **Category III**: Emerging technology (4 digits + T)

**Category I Classifications:**
- 00100-01999: Anesthesia
- 10000-69990: Surgery
- 70000-79999: Radiology
- 80000-89999: Pathology and Laboratory
- 90000-99999: Medicine
- 99000-99607: Evaluation and Management (E/M)

**Common E/M Codes:**
- **99201-99215**: Office/Outpatient (New and Established patients)
- **99221-99239**: Hospital Inpatient Services
- **99281-99285**: Emergency Department Visits
- **99291-99292**: Critical Care
- **99304-99318**: Nursing Facility Services

**Modifiers:**
- Two-digit codes added to CPT codes.
- Indicate that a service was altered but not changed in its definition.
- Examples:
  - -25: Significant, separately identifiable E/M service
  - -50: Bilateral procedure
  - -59: Distinct procedural service
  - -76: Repeat procedure by same physician
  - -RT/LT: Right side/Left side

### RxNorm

**Use:** Standardized names for clinical drugs and drug delivery devices.

**Structure:**
- Includes brand and generic names
- Dosage form
- Strength
- Links to other drug vocabularies (NDC, SNOMED CT)

**Examples:**
- Concept: Amoxicillin 500 MG Oral Capsule
- RxNorm CUI: 308191
- Ingredient: Amoxicillin
- Strength: 500 MG
- Dosage Form: Oral Capsule

## Medical Abbreviations

### Acceptable Standard Abbreviations

**Timing:**
- q: Every (q4h = every 4 hours)
- qd: Every day (Recommended to avoid - use "daily")
- bid: Twice a day
- tid: Three times a day
- qid: Four times a day
- qhs: At bedtime
- prn: As needed
- ac: Before meals
- pc: After meals
- hs: At bedtime

**Route:**
- PO: By mouth (per os)
- IV: Intravenous
- IM: Intramuscular
- SC/SQ/subcut: Subcutaneous
- SL: Sublingual
- PR: Per rectum
- NG: Nasogastric tube
- GT: Gastrostomy tube
- TD: Transdermal
- inh: Inhalation

**Frequency:**
- stat: Immediately
- now: Immediately
- continuous: Continuous
- PRN: As needed

**Laboratory Tests:**
- CBC: Complete Blood Count
- BMP: Basic Metabolic Panel
- CMP: Comprehensive Metabolic Panel
- LFTs: Liver Function Tests
- PT/INR: Prothrombin Time/International Normalized Ratio
- PTT/aPTT: Partial Thromboplastin Time/Activated PTT
- ESR: Erythrocyte Sedimentation Rate
- CRP: C-Reactive Protein
- ABG: Arterial Blood Gas
- UA: Urinalysis
- HbA1c: Hemoglobin A1c

**Diagnoses:**
- HTN: Hypertension
- DM: Diabetes Mellitus
- CHF: Congestive Heart Failure
- CAD: Coronary Artery Disease
- COPD: Chronic Obstructive Pulmonary Disease
- CVA: Cerebrovascular Accident (Stroke)
- MI: Myocardial Infarction
- PE: Pulmonary Embolism
- DVT: Deep Vein Thrombosis
- UTI: Urinary Tract Infection
- CKD: Chronic Kidney Disease
- ESRD: End-Stage Renal Disease

**Physical Examination:**
- HEENT: Head, Eyes, Ears, Nose, Throat
- PERRLA: Pupils Equal, Round, Reactive to Light and Accommodation
- EOMI: Extraocular Movements Intact
- JVP: Jugular Venous Pressure
- RRR: Regular Rate and Rhythm
- CTAB: Clear to Auscultation Bilaterally
- BS: Bowel Sounds or Breath Sounds (context-dependent)
- NT/ND: Non-tender, Non-distended
- FROM: Full Range of Motion

**Vital Signs:**
- BP: Blood Pressure
- HR: Heart Rate
- RR: Respiratory Rate
- T or Temp: Temperature
- SpO2: Peripheral Oxygen Saturation
- Wt: Weight
- Ht: Height
- BMI: Body Mass Index

### Prohibited Abbreviations (The Joint Commission)

**Abbreviations to Avoid:**

| Abbreviation | Intended Meaning | Problem | Use Instead |
|--------------|------------------|---------|-------------|
| U | Unit | Mistaken for 0, 4, or cc | Write "unit" |
| IU | International Unit | Mistaken for IV or 10 | Write "international unit" |
| Q.D., QD, q.d., qd | Daily | Mistaken for each other | Write "daily" |
| Q.O.D., QOD, q.o.d., qod | Every other day | Mistaken for QD or QID | Write "every other day" |
| Trailing zero (X.0 mg) | X mg | Decimal point missed | Never write a zero after a whole number (write X mg) |
| Lack of leading zero (.X mg) | 0.X mg | Decimal point missed | Always write a zero before a decimal (write 0.X mg) |
| MS, MSO4, MgSO4 | Morphine or Magnesium sulfate | Easily confused with each other | Write "morphine sulfate" or "magnesium sulfate" |

**Other Problematic Abbreviations:**
- µg: Microgram (mistaken for mg) → Write "mcg"
- cc: Cubic centimeter → Write "mL"
- hs: Half-strength or bedtime → Write "half-strength" or "bedtime"
- TIW: Three times weekly → Write "three times weekly"
- SC, SQ: Subcutaneous → Write "subcut" or "subcutaneous"
- D/C: Discharge or Discontinue → Write the full word
- AS, AD, AU: Left ear, right ear, both ears → Write "left ear," "right ear," "both ears"
- OS, OD, OU: Left eye, right eye, both eyes → Write "left eye," "right eye," "both eyes"

## Drug Nomenclature

### Generic vs. Brand Names

**Best Practice:** Use generic names in medical documentation.

**Examples:**
- Acetaminophen (Generic) vs. Tylenol (Brand)
- Ibuprofen (Generic) vs. Advil, Motrin (Brand)
- Atorvastatin (Generic) vs. Lipitor (Brand)
- Metformin (Generic) vs. Glucophage (Brand)
- Lisinopril (Generic) vs. Zestril, Prinivil (Brand)

**When to Include Brand Names:**
- Patient education (for easier identification)
- New patented drugs without generic names
- Narrow therapeutic index drugs with bioequivalence concerns
- Biologics

### Dosage Forms

**Solid Oral:**
- Tablet
- Capsule
- Caplet
- Chewable tablet
- Orally disintegrating tablet (ODT)
- Extended-release (ER, XR, SR)
- Delayed-release (DR)

**Liquid Oral:**
- Solution
- Suspension
- Syrup
- Elixir
- Drops

**Injectable:**
- Solution for injection
- Powder for injection (requires reconstitution)
- Intravenous infusion
- Intramuscular injection
- Subcutaneous injection

**Topical:**
- Cream
- Ointment
- Gel
- Lotion
- Paste
- Patch (Transdermal)
- Foam
- Spray

**Others:**
- Suppository (Rectal, Vaginal)
- Inhaler (MDI, DPI)
- Nebulizer solution
- Ophthalmic (Eye drops, Ointment)
- Otic (Ear drops)
- Nasal spray

### Elements of a Prescription

**A complete prescription includes:**
1. Patient name and date of birth
2. Date
3. Medication name (Generic preferred)
4. Strength/Concentration
5. Dosage form
6. Quantity to dispense
7. Sig (Directions for use)
8. Number of refills
9. Prescriber signature and credentials
10. DEA number (for controlled substances)

**Sig (Directions for Use):**
- Clear, specific instructions
- Route of administration
- Frequency
- Duration (if applicable)
- Special instructions

**Examples:**
- "Take 1 tablet by mouth twice daily with food for 10 days"
- "Apply a thin layer to the affected area three times daily"
- "Instill 1 drop into each eye every 4 hours while awake"

## Anatomical Terminology

### Directional Terms

**Superior/Inferior:**
- Superior: Toward the head
- Inferior: Toward the feet
- Cranial: Toward the skull
- Caudal: Toward the tail/feet

**Anterior/Posterior:**
- Anterior: Toward the front/belly
- Posterior: Toward the back
- Ventral: Toward the belly side
- Dorsal: Toward the back side

**Medial/Lateral:**
- Medial: Toward the midline
- Lateral: Away from the midline

**Proximal/Distal:**
- Proximal: Closer to the trunk or point of origin
- Distal: Farther from the trunk or point of origin

**Superficial/Deep:**
- Superficial: Toward the surface
- Deep: Away from the surface

### Body Planes

**Sagittal plane:** Divides the body into left and right
- Midsagittal: Exactly through the midline
- Parasagittal: Parallel to the midline

**Coronal (frontal) plane:** Divides the body into anterior and posterior

**Transverse (axial) plane:** Divides the body into superior and inferior

### Standard Anatomical Position

- Body standing erect
- Feet parallel
- Arms at the sides
- Palms facing forward
- Head facing forward

### Regional Terms

**Head and Neck:**
- Cephalic: Head
- Frontal: Forehead
- Orbital: Eye socket
- Nasal: Nose
- Oral: Mouth
- Cervical: Neck
- Occipital: Back of head

**Trunk:**
- Thoracic: Chest
- Abdominal: Abdomen
- Pelvic: Pelvis
- Lumbar: Lower back
- Sacral: Between the hips

**Limbs:**
- Brachial: Arm
- Antebrachial: Forearm
- Carpal: Wrist
- Manual: Hand
- Digital: Fingers/Toes
- Femoral: Thigh
- Crural: Leg (lower)
- Tarsal: Ankle
- Pedal: Foot

## Laboratory Units and Conversions

### Common Laboratory Units

**Hematology:**
- RBC: × 10⁶/μL or × 10¹²/L
- WBC: × 10³/μL or × 10⁹/L
- Hemoglobin: g/dL or g/L
- Hematocrit: % or fraction
- Platelets: × 10³/μL or × 10⁹/L
- MCV: fL
- MCHC: g/dL or g/L

**Chemistry:**
- Glucose: mg/dL or mmol/L
- BUN: mg/dL or mmol/L
- Creatinine: mg/dL or μmol/L
- Sodium, Potassium, Chloride: mEq/L or mmol/L
- Calcium: mg/dL or mmol/L
- Albumin: g/dL or g/L
- Bilirubin: mg/dL or μmol/L
- Cholesterol: mg/dL or mmol/L

**Therapeutic Drug Levels:**
- Usually: mcg/mL, ng/mL, or μmol/L

### Unit Conversions (Selected)

**Glucose:**
- mg/dL ÷ 18 = mmol/L
- mmol/L × 18 = mg/dL

**Creatinine:**
- mg/dL × 88.4 = μmol/L
- μmol/L ÷ 88.4 = mg/dL

**Bilirubin:**
- mg/dL × 17.1 = μmol/L
- μmol/L ÷ 17.1 = mg/dL

**Cholesterol:**
- mg/dL × 0.0259 = mmol/L
- mmol/L × 38.67 = mg/dL

**Hemoglobin:**
- g/dL × 10 = g/L
- g/L ÷ 10 = g/dL

## Grading and Staging Systems

### Cancer Staging (TNM)

**T (Primary Tumor):**
- TX: Cannot be assessed
- T0: No evidence of primary tumor
- Tis: Carcinoma in situ
- T1-T4: Size and/or extent of the primary tumor

**N (Regional Lymph Nodes):**
- NX: Cannot be assessed
- N0: No regional lymph node metastasis
- N1-N3: Involvement of regional lymph nodes

**M (Distant Metastasis):**
- M0: No distant metastasis
- M1: Distant metastasis present

**Stage Groupings:**
- Stage 0: Tis N0 M0
- Stage I-III: Various T and N combinations, M0
- Stage IV: Any T, Any N, M1

### NYHA Functional Classification (Heart Failure)

- **Class I**: No limitation of physical activity. Ordinary physical activity does not cause symptoms.
- **Class II**: Slight limitation of physical activity. Comfortable at rest, but ordinary activity results in symptoms.
- **Class III**: Marked limitation of physical activity. Comfortable at rest, but less than ordinary activity causes symptoms.
- **Class IV**: Unable to carry on any physical activity without discomfort. Symptoms present even at rest.

### Child-Pugh Score (Liver Disease)

**Parameters:** Bilirubin, Albumin, INR, Ascites, Encephalopathy

**Classes:**
- **Class A (5-6 points)**: Well-compensated disease
- **Class B (7-9 points)**: Significant functional impairment
- **Class C (10-15 points)**: Decompensated disease

### Glasgow Coma Scale (GCS)

**Eye Opening (1-4):**
- 4: Spontaneous
- 3: To speech
- 2: To pain
- 1: None

**Verbal Response (1-5):**
- 5: Oriented
- 4: Confused
- 3: Inappropriate words
- 2: Incomprehensible sounds
- 1: None

**Motor Response (1-6):**
- 6: Obeys commands
- 5: Localizes pain
- 4: Withdraws from pain
- 3: Flexion to pain (decorticate posturing)
- 2: Extension to pain (decerebrate posturing)
- 1: None

**Total Score:** 3-15 (3 is worst, 15 is best)
- Severe: ≤8
- Moderate: 9-12
- Mild: 13-15

## Medical Prefixes and Suffixes

### Common Prefixes

- **a-/an-**: Without, lack of (anemia, aphasia)
- **brady-**: Slow (bradycardia)
- **dys-**: Abnormal, difficult (dyspnea, dysuria)
- **hyper-**: Excessive, above (hypertension, hyperglycemia)
- **hypo-**: Below, deficient (hypotension, hypoglycemia)
- **poly-**: Many (polyuria, polydipsia)
- **tachy-**: Fast (tachycardia, tachypnea)
- **macro-**: Large (macrocephaly)
- **micro-**: Small (microcephaly)
- **hemi-**: Half (hemiplegia)
- **bi-/di-**: Two/Double (bilateral, diplopia)

### Common Suffixes

- **-algia**: Pain (arthralgia, neuralgia)
- **-ectomy**: Surgical removal (appendectomy, cholecystectomy)
- **-emia**: Blood condition (anemia, leukemia)
- **-itis**: Inflammation (appendicitis, arthritis)
- **-oma**: Tumor (carcinoma, melanoma)
- **-osis**: Abnormal condition (cirrhosis, osteoporosis)
- **-pathy**: Disease (neuropathy, nephropathy)
- **-penia**: Deficiency (thrombocytopenia, neutropenia)
- **-plasty**: Surgical repair/shaping (rhinoplasty, angioplasty)
- **-scopy**: Visual examination (colonoscopy, bronchoscopy)
- **-stomy**: Surgical opening (colostomy, tracheostomy)

---

This reference guide provides a comprehensive overview of medical terminology, coding systems, abbreviations, and nomenclature standards. Follow these guidelines to ensure accuracy and standardization in clinical documentation.