#!/usr/bin/env python3
"""Generate mind maps for subjects that lack them (OMFS through Perio)."""

import json
import os

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "content", "subjects")

MINDMAPS = {
    # ── OMFS (oral-surgery) ──────────────────────────────
    "oral-surgery": [
        {
            "id": "mm-maxfac-fractures",
            "title": "Maxillofacial Fractures – Classification & Management",
            "mermaid": """graph TD
    A["Maxillofacial Fractures"] --> B["Mandibular Fractures"]
    A --> C["Mid-face Fractures"]
    A --> D["Zygomatic Complex"]
    A --> E["Orbital Fractures"]
    A --> F["Frontal Bone / Sinus"]
    B --> B1["Symphysis / Parasymphysis"]
    B --> B2["Body"]
    B --> B3["Angle"]
    B --> B4["Condylar"]
    B --> B5["Ramus / Coronoid"]
    B3 --> B3a["Most common site"]
    B4 --> B4a["Intracapsular / Extracapsular"]
    C --> C1["Le Fort I – Guérin"]
    C --> C2["Le Fort II – Pyramidal"]
    C --> C3["Le Fort III – Craniofacial Disjunction"]
    C1 --> C1a["Transverse maxillary"]
    C2 --> C2a["Through nasion, lacrimal, infraorbital rim"]
    C3 --> C3a["Complete separation from cranium"]
    D --> D1["Tripod / Tetrapod fracture"]
    D --> D2["Arch fracture"]
    E --> E1["Blowout fracture"]
    E --> E2["Enophthalmos / Diplopia"]
    A --> G["Management Principles"]
    G --> G1["IMF / MMF"]
    G --> G2["ORIF with miniplates"]
    G --> G3["Champy's ideal lines of osteosynthesis"]"""
        },
        {
            "id": "mm-local-anesthesia",
            "title": "Local Anesthesia – Nerve Blocks & Techniques",
            "mermaid": """graph TD
    A["Local Anesthesia in OMFS"] --> B["Maxillary Blocks"]
    A --> C["Mandibular Blocks"]
    A --> D["Supplemental Techniques"]
    B --> B1["PSA – Posterior Superior Alveolar"]
    B --> B2["MSA – Middle Superior Alveolar"]
    B --> B3["ASA – Anterior Superior Alveolar"]
    B --> B4["Infraorbital Nerve Block"]
    B --> B5["Greater Palatine Block"]
    B --> B6["Nasopalatine Block"]
    C --> C1["IANB – Inferior Alveolar"]
    C --> C2["Lingual Nerve Block"]
    C --> C3["Long Buccal Nerve Block"]
    C --> C4["Mental / Incisive Block"]
    C1 --> C1a["Pterygomandibular space"]
    C1 --> C1b["Landmarks: coronoid notch, pterygomandibular raphe"]
    D --> D1["Gow-Gates Technique"]
    D --> D2["Vazirani-Akinosi – Closed mouth"]
    D --> D3["Infiltration"]
    D --> D4["Intraligamentary / PDL injection"]
    A --> E["Complications"]
    E --> E1["Trismus"]
    E --> E2["Hematoma"]
    E --> E3["Paresthesia"]
    E --> E4["Needle breakage"]
    E --> E5["Facial nerve paralysis"]"""
        },
        {
            "id": "mm-impacted-teeth",
            "title": "Impacted Teeth – Classification & Surgical Access",
            "mermaid": """graph TD
    A["Impacted Teeth"] --> B["Third Molars"]
    A --> C["Canines"]
    A --> D["Supernumerary – Mesiodens"]
    B --> B1["Mandibular 3rd Molar"]
    B --> B2["Maxillary 3rd Molar"]
    B1 --> E["Winter's Classification"]
    E --> E1["Mesioangular – Most common"]
    E --> E2["Distoangular"]
    E --> E3["Vertical"]
    E --> E4["Horizontal"]
    B1 --> F["Pell & Gregory"]
    F --> F1["Class I / II / III – Ramus relation"]
    F --> F2["Position A / B / C – Depth"]
    B2 --> G["Archer Classification"]
    C --> C1["Palatal – Most common"]
    C --> C2["Labial / Buccal"]
    A --> H["Indications for Removal"]
    H --> H1["Recurrent pericoronitis"]
    H --> H2["Caries / Resorption of adjacent tooth"]
    H --> H3["Pathological – Cyst / Tumor"]
    H --> H4["Orthodontic reasons"]
    A --> I["Surgical Steps"]
    I --> I1["Flap design – Envelope / Triangular"]
    I --> I2["Bone removal – Buccal guttering"]
    I --> I3["Tooth sectioning – Split technique"]
    I --> I4["Elevation & Delivery"]
    I --> I5["Debridement & Closure"]"""
        },
        {
            "id": "mm-odontogenic-infections",
            "title": "Odontogenic Infections – Fascial Spaces",
            "mermaid": """graph TD
    A["Odontogenic Infections"] --> B["Primary Spaces"]
    A --> C["Secondary Spaces"]
    A --> D["Management"]
    B --> B1["Buccal Space"]
    B --> B2["Canine / Infraorbital Space"]
    B --> B3["Submandibular Space"]
    B --> B4["Sublingual Space"]
    B --> B5["Submental Space"]
    B --> B6["Submasseteric Space"]
    C --> C1["Parapharyngeal Space"]
    C --> C2["Retropharyngeal Space"]
    C --> C3["Pterygomandibular Space"]
    C --> C4["Infratemporal Space"]
    C --> C5["Temporal Space"]
    B3 --- L1["Ludwig's Angina"]
    B4 --- L1
    B5 --- L1
    L1 --> L1a["Bilateral submandibular, sublingual, submental"]
    L1 --> L1b["Airway emergency"]
    C1 --> C1a["Danger: Mediastinitis via retropharyngeal"]
    D --> D1["I & D – Incision & Drainage"]
    D --> D2["Empirical antibiotics – Pen + Metronidazole"]
    D --> D3["Culture & Sensitivity"]
    D --> D4["Remove source – Extraction"]"""
        },
    ],

    # ── Community / Public Health ────────────────────────
    "public-health-dentistry": [
        {
            "id": "mm-preventive-dentistry",
            "title": "Preventive Dentistry – Levels & Methods",
            "mermaid": """graph TD
    A["Preventive Dentistry"] --> B["Primary Prevention"]
    A --> C["Secondary Prevention"]
    A --> D["Tertiary Prevention"]
    B --> B1["Health Promotion"]
    B --> B2["Specific Protection"]
    B1 --> B1a["Health education"]
    B1 --> B1b["Nutrition counseling"]
    B2 --> B2a["Fluorides"]
    B2 --> B2b["Pit & Fissure Sealants"]
    B2 --> B2c["Vaccination – Hep B"]
    B2a --> F1["Systemic – Water, Salt, Tablets"]
    B2a --> F2["Topical – APF, NaF, SnF2, Varnish"]
    F1 --> F1a["Optimal: 0.7-1.2 ppm"]
    F2 --> F2a["APF: 1.23% at pH 3.5"]
    C --> C1["Early Diagnosis"]
    C --> C2["Prompt Treatment"]
    C --> C3["Disability Limitation"]
    D --> D1["Rehabilitation"]
    D --> D2["Prosthetic replacement"]
    A --> E["ADA Caries Risk Assessment"]
    E --> E1["Low / Moderate / High Risk"]"""
        },
        {
            "id": "mm-dental-indices",
            "title": "Dental Indices – Classification & Key Indices",
            "mermaid": """graph TD
    A["Dental Indices"] --> B["Caries Indices"]
    A --> C["Periodontal Indices"]
    A --> D["Oral Hygiene Indices"]
    A --> E["Malocclusion Indices"]
    A --> F["Fluorosis Indices"]
    B --> B1["DMFT / dmft"]
    B --> B2["DMFS / dmfs"]
    B --> B3["Significant Caries Index – SiC"]
    C --> C1["GI – Gingival Index – Loe & Silness"]
    C --> C2["PI – Periodontal Index – Russell"]
    C --> C3["CPI – Community Periodontal Index"]
    C --> C4["CPITN – Treatment Needs"]
    C --> C5["PDI – Periodontal Disease Index – Ramfjord"]
    D --> D1["OHI-S – Greene & Vermillion"]
    D --> D2["DI-S + CI-S"]
    D --> D3["PHP – Patient Hygiene Performance"]
    D --> D4["PI – Plaque Index – Silness & Loe"]
    E --> E1["DAI – Dental Aesthetic Index"]
    E --> E2["IOTN – Index of Treatment Need"]
    F --> F1["Dean's Fluorosis Index"]
    F --> F2["TSIF – Tooth Surface Index of Fluorosis"]
    F --> F3["TF Index – Thylstrup & Fejerskov"]"""
        },
        {
            "id": "mm-biostatistics",
            "title": "Biostatistics – Key Concepts",
            "mermaid": """graph TD
    A["Biostatistics"] --> B["Measures of Central Tendency"]
    A --> C["Measures of Dispersion"]
    A --> D["Tests of Significance"]
    A --> E["Epidemiological Measures"]
    B --> B1["Mean"]
    B --> B2["Median"]
    B --> B3["Mode"]
    C --> C1["Range"]
    C --> C2["Standard Deviation"]
    C --> C3["Variance"]
    C --> C4["Coefficient of Variation"]
    D --> D1["Chi-square test – Categorical"]
    D --> D2["Student t-test – 2 means"]
    D --> D3["ANOVA – >2 means"]
    D --> D4["p-value < 0.05 = Significant"]
    E --> E1["Sensitivity"]
    E --> E2["Specificity"]
    E --> E3["PPV / NPV"]
    E --> E4["Odds Ratio"]
    E --> E5["Relative Risk"]
    E1 --> E1a["True Positives / All Diseased"]
    E2 --> E2a["True Negatives / All Healthy"]"""
        },
    ],

    # ── Oral Medicine ────────────────────────────────────
    "oral-medicine": [
        {
            "id": "mm-oral-lesions",
            "title": "Oral Mucosal Lesions – Classification",
            "mermaid": """graph TD
    A["Oral Mucosal Lesions"] --> B["White Lesions"]
    A --> C["Red Lesions"]
    A --> D["Ulcerative Lesions"]
    A --> E["Vesiculobullous"]
    A --> F["Pigmented Lesions"]
    B --> B1["Leukoplakia"]
    B --> B2["Oral Lichen Planus"]
    B --> B3["Oral Submucous Fibrosis"]
    B --> B4["White Sponge Nevus"]
    B --> B5["Candidiasis – Pseudomembranous"]
    B1 --> B1a["Potentially malignant"]
    B3 --> B3a["Areca nut – Trismus"]
    C --> C1["Erythroplakia"]
    C --> C2["Erythematous Candidiasis"]
    C --> C3["Median Rhomboid Glossitis"]
    C1 --> C1a["Highest malignant potential"]
    D --> D1["Aphthous Ulcers – RAS"]
    D --> D2["Traumatic Ulcer"]
    D --> D3["Oral Cancer – SCC"]
    D --> D4["Tuberculous Ulcer"]
    D1 --> D1a["Minor / Major / Herpetiform"]
    E --> E1["Pemphigus Vulgaris"]
    E --> E2["Bullous Pemphigoid"]
    E --> E3["Erythema Multiforme"]
    E1 --> E1a["Nikolsky sign +ve"]
    E1 --> E1b["Tzanck cells"]
    F --> F1["Melanotic Macule"]
    F --> F2["Melanoma"]
    F --> F3["Addison Disease"]"""
        },
        {
            "id": "mm-premalignant",
            "title": "Potentially Malignant Disorders – PMDs",
            "mermaid": """graph TD
    A["Potentially Malignant Disorders"] --> B["Conditions"]
    A --> C["Lesions"]
    A --> D["Habits"]
    B --> B1["Oral Submucous Fibrosis"]
    B --> B2["Oral Lichen Planus – Erosive"]
    B --> B3["Sideropenic Dysphagia – Plummer Vinson"]
    B --> B4["Syphilitic Glossitis"]
    B --> B5["Xeroderma Pigmentosum"]
    C --> C1["Leukoplakia"]
    C --> C2["Erythroplakia"]
    C --> C3["Palatal lesions of reverse smoking"]
    C --> C4["Actinic Cheilitis"]
    C2 --> C2a["51% malignant transformation – highest"]
    C1 --> C1a["3-6% malignant transformation"]
    D --> D1["Tobacco – Smoking & Smokeless"]
    D --> D2["Alcohol"]
    D --> D3["Areca nut / Betel quid"]
    A --> E["Malignant Transformation Signs"]
    E --> E1["Induration"]
    E --> E2["Fixation"]
    E --> E3["Speckled appearance"]
    E --> E4["Rapid growth"]
    A --> F["Diagnosis"]
    F --> F1["Biopsy – Gold standard"]
    F --> F2["Toluidine blue staining"]
    F --> F3["Brush biopsy"]"""
        },
        {
            "id": "mm-salivary-diseases",
            "title": "Salivary Gland Diseases – Overview",
            "mermaid": """graph TD
    A["Salivary Gland Diseases"] --> B["Inflammatory"]
    A --> C["Obstructive"]
    A --> D["Neoplastic"]
    A --> E["Autoimmune"]
    B --> B1["Acute Bacterial Sialadenitis"]
    B --> B2["Viral – Mumps"]
    B --> B3["Chronic Sialadenitis"]
    B1 --> B1a["Parotid most common"]
    B2 --> B2a["Bilateral parotid swelling"]
    C --> C1["Sialolithiasis"]
    C --> C2["Ranula – Floor of mouth"]
    C --> C3["Mucocele – Lower lip"]
    C1 --> C1a["Submandibular gland – 80-90%"]
    C1 --> C1b["Wharton's duct"]
    D --> D1["Pleomorphic Adenoma"]
    D --> D2["Warthin Tumor"]
    D --> D3["Mucoepidermoid Carcinoma"]
    D --> D4["Adenoid Cystic Carcinoma"]
    D1 --> D1a["Most common benign – Parotid"]
    D3 --> D3a["Most common malignant"]
    D4 --> D4a["Perineural invasion"]
    E --> E1["Sjogren Syndrome"]
    E1 --> E1a["Xerostomia + Keratoconjunctivitis sicca"]
    E1 --> E1b["Anti-SSA/Ro, Anti-SSB/La"]"""
        },
        {
            "id": "mm-oral-radiology",
            "title": "Oral Radiology – Techniques & Key Findings",
            "mermaid": """graph TD
    A["Oral Radiology"] --> B["Intraoral"]
    A --> C["Extraoral"]
    A --> D["Advanced Imaging"]
    B --> B1["IOPA – Periapical"]
    B --> B2["Bitewing"]
    B --> B3["Occlusal"]
    B1 --> B1a["Paralleling / Bisecting angle"]
    B2 --> B2a["Interproximal caries detection"]
    B3 --> B3a["Floor of mouth calculi"]
    C --> C1["OPG – Panoramic"]
    C --> C2["Lateral Cephalogram"]
    C --> C3["PA view – Waters / Caldwell"]
    C --> C4["SMV – Submentovertex"]
    C1 --> C1a["Screening / Impactions / Fractures"]
    C2 --> C2a["Orthodontic analysis"]
    D --> D1["CBCT"]
    D --> D2["CT Scan"]
    D --> D3["MRI"]
    D --> D4["Sialography"]
    D --> D5["Ultrasonography"]
    D1 --> D1a["3D imaging – Implant planning"]
    D3 --> D3a["TMJ soft tissue – Disc displacement"]
    D4 --> D4a["Duct visualization with contrast"]"""
        },
    ],

    # ── Pedodontics ──────────────────────────────────────
    "pedodontics": [
        {
            "id": "mm-behavior-management",
            "title": "Child Behavior Management Techniques",
            "mermaid": """graph TD
    A["Behavior Management"] --> B["Non-pharmacological"]
    A --> C["Pharmacological"]
    A --> D["Assessment"]
    B --> E["Basic Techniques"]
    B --> F["Advanced Techniques"]
    E --> E1["Tell-Show-Do"]
    E --> E2["Voice Control"]
    E --> E3["Positive Reinforcement"]
    E --> E4["Distraction"]
    E --> E5["Communication – Verbal / Non-verbal"]
    E --> E6["Modeling"]
    F --> F1["Desensitization"]
    F --> F2["HOME – Hand Over Mouth"]
    F --> F3["Protective Stabilization"]
    F --> F4["Aversive Conditioning"]
    C --> C1["Sedation"]
    C --> C2["General Anesthesia"]
    C1 --> C1a["Nitrous Oxide – N2O/O2"]
    C1 --> C1b["Oral Sedation – Midazolam"]
    C1 --> C1c["IV Sedation"]
    C2 --> C2a["Uncooperative / Special needs"]
    D --> D1["Frankl Classification"]
    D1 --> D1a["Definitely Negative"]
    D1 --> D1b["Negative"]
    D1 --> D1c["Positive"]
    D1 --> D1d["Definitely Positive"]"""
        },
        {
            "id": "mm-space-management",
            "title": "Space Management & Maintainers",
            "mermaid": """graph TD
    A["Space Management"] --> B["Space Maintainers"]
    A --> C["Space Regainers"]
    A --> D["When to Use"]
    B --> B1["Fixed"]
    B --> B2["Removable"]
    B1 --> B1a["Band & Loop"]
    B1 --> B1b["Crown & Loop"]
    B1 --> B1c["Lingual Arch"]
    B1 --> B1d["Transpalatal Arch – TPA"]
    B1 --> B1e["Nance Holding Arch"]
    B1 --> B1f["Distal Shoe"]
    B1a --> BA["Unilateral – Single tooth loss"]
    B1c --> BC["Bilateral mandibular"]
    B1e --> BE["Bilateral maxillary"]
    B1f --> BF["Before 1st molar eruption"]
    B2 --> B2a["Acrylic partial denture"]
    B2 --> B2b["Functional – With artificial teeth"]
    C --> C1["Active – Spring / Screw"]
    C --> C2["Passive – Lip bumper"]
    D --> D1["Primary 2nd molar early loss"]
    D --> D2["Multiple teeth lost"]
    D --> D3["Not needed if successor about to erupt"]"""
        },
        {
            "id": "mm-tooth-development",
            "title": "Tooth Development & Eruption Chronology",
            "mermaid": """graph TD
    A["Tooth Development"] --> B["Stages"]
    A --> C["Primary Teeth Eruption"]
    A --> D["Permanent Teeth Eruption"]
    A --> E["Developmental Disturbances"]
    B --> B1["Bud Stage"]
    B --> B2["Cap Stage"]
    B --> B3["Bell Stage"]
    B --> B4["Maturation"]
    B2 --> B2a["Enamel organ differentiates"]
    B3 --> B3a["IEE, OEE, Stellate reticulum, SI"]
    C --> C1["Lower Central Incisor – 6 mo"]
    C --> C2["Upper Central Incisor – 8 mo"]
    C --> C3["All primary – by 30 mo"]
    C --> C4["Root completion – 1 yr after eruption"]
    D --> D1["First Molar – 6 yr"]
    D --> D2["Central Incisor – 6-7 yr"]
    D --> D3["Premolars – 10-12 yr"]
    D --> D4["Second Molar – 12 yr"]
    D --> D5["Third Molar – 17-21 yr"]
    D1 --> D1a["First permanent tooth – No predecessor"]
    E --> E1["Enamel Hypoplasia"]
    E --> E2["Amelogenesis Imperfecta"]
    E --> E3["Dentinogenesis Imperfecta"]
    E --> E4["Turner Hypoplasia"]
    E4 --> E4a["Local infection from primary tooth"]"""
        },
        {
            "id": "mm-oral-habits",
            "title": "Oral Habits – Types & Management",
            "mermaid": """graph TD
    A["Oral Habits"] --> B["Nutritive Sucking"]
    A --> C["Non-nutritive Sucking"]
    A --> D["Other Habits"]
    B --> B1["Breastfeeding"]
    B --> B2["Bottle feeding"]
    C --> C1["Thumb Sucking"]
    C --> C2["Pacifier"]
    C --> C3["Finger Sucking"]
    C1 --> E["Effects"]
    E --> E1["Proclination of upper anteriors"]
    E --> E2["Retroclination of lower anteriors"]
    E --> E3["Anterior open bite"]
    E --> E4["Posterior crossbite"]
    E --> E5["Narrow maxillary arch"]
    C1 --> F["Management"]
    F --> F1["Counseling – Before age 3"]
    F --> F2["Reminder therapy"]
    F --> F3["Habit breaking appliance"]
    F3 --> F3a["Bluegrass appliance"]
    F3 --> F3b["Palatal crib – Rake"]
    F3 --> F3c["Quad helix"]
    D --> D1["Tongue Thrusting"]
    D --> D2["Mouth Breathing"]
    D --> D3["Bruxism"]
    D --> D4["Lip Biting / Sucking"]
    D2 --> D2a["Adenoid facies – Long face"]
    D1 --> D1a["Open bite"]"""
        },
    ],

    # ── Orthodontics ─────────────────────────────────────
    "orthodontics": [
        {
            "id": "mm-angles-classification",
            "title": "Angle's Classification of Malocclusion",
            "mermaid": """graph TD
    A["Angle's Classification"] --> B["Class I – Neutrocclusion"]
    A --> C["Class II – Distocclusion"]
    A --> D["Class III – Mesiocclusion"]
    B --> B1["Normal molar relationship"]
    B --> B2["MB cusp of upper 6 in buccal groove of lower 6"]
    B --> B3["Crowding / Spacing / Individual tooth malposition"]
    C --> C1["Division 1"]
    C --> C2["Division 2"]
    C --> C3["Subdivision – Unilateral"]
    C1 --> C1a["Proclined upper incisors"]
    C1 --> C1b["Increased overjet"]
    C1 --> C1c["Lip trap / Incompetent lips"]
    C2 --> C2a["Retroclined upper centrals"]
    C2 --> C2b["Proclined upper laterals"]
    C2 --> C2c["Deep bite"]
    C2 --> C2d["Covers-bite"]
    D --> D1["Mandibular prognathism"]
    D --> D2["Maxillary deficiency"]
    D --> D3["Anterior crossbite"]
    D --> D4["Pseudo – Functional shift"]
    D --> D5["True – Skeletal"]
    A --> E["Limitations"]
    E --> E1["Only antero-posterior – No vertical/transverse"]
    E --> E2["Based only on 1st molar"]
    E --> E3["No etiology considered"]"""
        },
        {
            "id": "mm-cephalometrics",
            "title": "Cephalometric Analysis – Key Landmarks & Angles",
            "mermaid": """graph TD
    A["Cephalometric Analysis"] --> B["Hard Tissue Landmarks"]
    A --> C["Soft Tissue Landmarks"]
    A --> D["Key Angles & Measurements"]
    B --> B1["Sella – S"]
    B --> B2["Nasion – N"]
    B --> B3["Porion – Po"]
    B --> B4["Orbitale – Or"]
    B --> B5["ANS / PNS"]
    B --> B6["Point A – Subspinale"]
    B --> B7["Point B – Supramentale"]
    B --> B8["Gonion – Go"]
    B --> B9["Menton – Me"]
    B --> B10["Gnathion – Gn"]
    C --> C1["Pronasale"]
    C --> C2["Subnasale"]
    C --> C3["Labrale superius / inferius"]
    C --> C4["Pogonion – Soft tissue"]
    D --> D1["SNA – 82° – Maxilla to cranial base"]
    D --> D2["SNB – 80° – Mandible to cranial base"]
    D --> D3["ANB – 2° – Skeletal relationship"]
    D --> D4["FMA – Frankfort Mandibular Angle – 25°"]
    D --> D5["IMPA – Lower incisor to mandibular plane – 90°"]
    D --> D6["Interincisal Angle – 135°"]
    D3 --> D3a["Class I: 2° / Class II: >4° / Class III: <0°"]"""
        },
        {
            "id": "mm-ortho-appliances",
            "title": "Orthodontic Appliances – Overview",
            "mermaid": """graph TD
    A["Orthodontic Appliances"] --> B["Removable"]
    A --> C["Fixed"]
    A --> D["Functional"]
    A --> E["Extraoral"]
    B --> B1["Hawley Retainer"]
    B --> B2["Expansion Plate"]
    B --> B3["Inclined Plane / Catlan's"]
    B --> B4["Active – Springs, Screws"]
    B --> B5["Passive – Space maintainers"]
    B1 --> B1a["Retention after fixed treatment"]
    C --> C1["Edgewise – Standard"]
    C --> C2["Pre-adjusted – MBT / Roth"]
    C --> C3["Begg – Light wire"]
    C --> C4["Self-ligating brackets"]
    C --> C5["Lingual orthodontics"]
    C2 --> C2a["Most widely used today"]
    D --> D1["Twin Block – Clark"]
    D --> D2["Activator – Andresen"]
    D --> D3["Bionator – Balters"]
    D --> D4["Frankel – FR"]
    D --> D5["Herbst Appliance"]
    D1 --> D1a["Class II correction – Mandibular advancement"]
    E --> E1["Headgear – Cervical pull / High pull"]
    E --> E2["Facemask – Reverse pull"]
    E --> E3["Chin cup"]
    E1 --> E1a["Class II – Distal force on maxilla"]
    E2 --> E2a["Class III – Protract maxilla"]"""
        },
        {
            "id": "mm-growth-development",
            "title": "Craniofacial Growth & Development",
            "mermaid": """graph TD
    A["Craniofacial Growth"] --> B["Growth Sites"]
    A --> C["Growth Mechanisms"]
    A --> D["Growth Patterns"]
    B --> B1["Cranial Base – Synchondroses"]
    B --> B2["Maxilla – Sutures & Periosteal"]
    B --> B3["Mandible – Condylar cartilage"]
    B --> B4["Nasal Septum Cartilage"]
    B1 --> B1a["Spheno-occipital – Last to fuse – 18-20 yr"]
    B2 --> B2a["Tuberosity – Posterior growth"]
    B3 --> B3a["Primary growth center of mandible"]
    C --> C1["Endochondral – Cartilage to bone"]
    C --> C2["Intramembranous – Direct bone"]
    C --> C3["Sutural Growth"]
    C --> C4["Periosteal Remodeling"]
    C --> C5["Appositional Growth"]
    D --> D1["Scammon's Growth Curves"]
    D1 --> D1a["Neural – Rapid early"]
    D1 --> D1b["General / Somatic – S-shaped"]
    D1 --> D1c["Lymphoid – Peak at 12 yr, then involute"]
    D1 --> D1d["Genital – Pubertal surge"]
    A --> E["Growth Theories"]
    E --> E1["Sicher – Sutural dominance"]
    E --> E2["Scott – Cartilage as primary center"]
    E --> E3["Moss – Functional matrix theory"]
    E --> E4["Van Limborgh – Multifactorial"]
    E3 --> E3a["Periosteal & Capsular matrices"]"""
        },
    ],

    # ── Periodontics ─────────────────────────────────────
    "periodontics": [
        {
            "id": "mm-periodontium-anatomy",
            "title": "Anatomy of Periodontium",
            "mermaid": """graph TD
    A["Periodontium"] --> B["Gingiva"]
    A --> C["Periodontal Ligament"]
    A --> D["Cementum"]
    A --> E["Alveolar Bone"]
    B --> B1["Free Gingiva"]
    B --> B2["Attached Gingiva"]
    B --> B3["Interdental Papilla – Col"]
    B --> B4["Gingival Sulcus – 0.5-3mm"]
    B1 --> B1a["Gingival margin to base of sulcus"]
    B2 --> B2a["Stippled, keratinized, immovable"]
    B3 --> B3a["Col – Concavity between papillae"]
    C --> C1["Principal Fibers"]
    C --> C2["Width: 0.15-0.38mm"]
    C --> C3["Functions: Support, Sensory, Remodeling"]
    C1 --> C1a["Alveolar crest"]
    C1 --> C1b["Horizontal"]
    C1 --> C1c["Oblique – Most numerous"]
    C1 --> C1d["Apical"]
    C1 --> C1e["Interradicular"]
    D --> D1["Acellular Extrinsic Fiber – Cervical"]
    D --> D2["Cellular Intrinsic Fiber – Apical"]
    D --> D3["Intermediate Cementum"]
    E --> E1["Cortical Plate – Lamina dura"]
    E --> E2["Cancellous / Spongy bone"]
    E --> E3["Alveolar bone proper – Cribriform plate"]
    E --> E4["Bundle bone"]"""
        },
        {
            "id": "mm-perio-classification",
            "title": "Periodontal Disease Classification – 2017 AAP/EFP",
            "mermaid": """graph TD
    A["2017 Classification"] --> B["Periodontal Health / Gingival Diseases"]
    A --> C["Periodontitis"]
    A --> D["Other Conditions"]
    B --> B1["Dental Biofilm-induced Gingivitis"]
    B --> B2["Non-dental biofilm-induced"]
    B1 --> B1a["On intact periodontium"]
    B1 --> B1b["On reduced periodontium"]
    C --> C1["Staging – Severity"]
    C --> C2["Grading – Progression Rate"]
    C1 --> C1a["Stage I – Initial"]
    C1 --> C1b["Stage II – Moderate"]
    C1 --> C1c["Stage III – Severe with potential tooth loss"]
    C1 --> C1d["Stage IV – Advanced with masticatory dysfunction"]
    C2 --> C2a["Grade A – Slow rate"]
    C2 --> C2b["Grade B – Moderate rate"]
    C2 --> C2c["Grade C – Rapid rate"]
    C1a --> S1["CAL 1-2mm"]
    C1b --> S2["CAL 3-4mm"]
    C1c --> S3["CAL ≥5mm"]
    D --> D1["Peri-implant Diseases"]
    D --> D2["Necrotizing Periodontal Diseases"]
    D --> D3["Periodontitis as manifestation of systemic disease"]
    D2 --> D2a["NUG / NUP / Necrotizing Stomatitis"]"""
        },
        {
            "id": "mm-perio-treatment",
            "title": "Periodontal Treatment Planning",
            "mermaid": """graph TD
    A["Periodontal Treatment"] --> B["Phase I – Non-Surgical"]
    A --> C["Phase II – Surgical"]
    A --> D["Phase III – Maintenance"]
    B --> B1["Oral Hygiene Instructions"]
    B --> B2["Scaling & Root Planing – SRP"]
    B --> B3["Antimicrobial Therapy"]
    B --> B4["Occlusal Adjustment"]
    B --> B5["Re-evaluation at 4-6 weeks"]
    B2 --> B2a["Hand instruments – Gracey curettes"]
    B2 --> B2b["Ultrasonic – Piezoelectric / Magnetostrictive"]
    B3 --> B3a["Systemic – Amoxicillin + Metronidazole"]
    B3 --> B3b["Local – Chlorhexidine / Minocycline"]
    C --> C1["Access Flap – Modified Widman"]
    C --> C2["Resective Surgery"]
    C --> C3["Regenerative Surgery"]
    C --> C4["Mucogingival Surgery"]
    C2 --> C2a["Osseous recontouring"]
    C2 --> C2b["Gingivectomy"]
    C3 --> C3a["GTR – Guided Tissue Regeneration"]
    C3 --> C3b["Bone grafts"]
    C3 --> C3c["EMD – Emdogain"]
    C4 --> C4a["Free gingival graft"]
    C4 --> C4b["Connective tissue graft"]
    C4 --> C4c["Coronally advanced flap"]
    D --> D1["Recall every 3 months"]
    D --> D2["Plaque / BOP assessment"]
    D --> D3["Supportive Periodontal Therapy – SPT"]"""
        },
        {
            "id": "mm-perio-flaps",
            "title": "Periodontal Flap Surgeries – Types",
            "mermaid": """graph TD
    A["Periodontal Flap Surgeries"] --> B["Based on Bone Exposure"]
    A --> C["Based on Flap Position"]
    A --> D["Based on Purpose"]
    B --> B1["Full Thickness – Mucoperiosteal"]
    B --> B2["Partial Thickness – Split"]
    B1 --> B1a["Bone exposed – Better access"]
    B2 --> B2a["Periosteum on bone – Better healing"]
    C --> C1["Non-displaced – Original position"]
    C --> C2["Apically Displaced"]
    C --> C3["Coronally Displaced"]
    C --> C4["Laterally Displaced"]
    C2 --> C2a["Crown lengthening"]
    C3 --> C3a["Root coverage"]
    C4 --> C4a["Adjacent recession coverage"]
    D --> D1["Access Flap"]
    D --> D2["Modified Widman Flap"]
    D --> D3["Kirkland Flap"]
    D --> D4["Neumann Flap"]
    D --> D5["ENAP – Excisional New Attachment Procedure"]
    D1 --> D1a["Debridement of root surface"]
    D2 --> D2a["Internal bevel, Crevicular, Interdental incisions"]
    D4 --> D4a["Full mucoperiosteal with releasing incision"]
    A --> E["Incisions"]
    E --> E1["Internal bevel – Primary"]
    E --> E2["Crevicular – Secondary"]
    E --> E3["Interdental – Tertiary"]
    E --> E4["Vertical releasing incisions"]"""
        },
    ],
}


def main():
    for slug, maps in MINDMAPS.items():
        path = os.path.join(APP_DIR, f"{slug}.json")
        with open(path) as f:
            data = json.load(f)

        existing_ids = {m["id"] for m in data.get("mindMaps", [])}
        existing = data.get("mindMaps", [])
        added = 0
        for mm in maps:
            if mm["id"] not in existing_ids:
                existing.append(mm)
                added += 1

        data["mindMaps"] = existing
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"{slug}: {added} mind maps added (total: {len(existing)})")


if __name__ == "__main__":
    main()
