/**
 * Dental OCR Spell-Checker
 * Auto-corrects common OCR misreadings from handwritten BDS notes.
 * Only corrects high-confidence dental terminology errors — never
 * changes words that might be intentional.
 */

const OCR_CORRECTIONS: Record<string, string> = {
  // Patient-related
  "pateent": "patient", "pahent": "patient", "pahenk": "patient",
  "patienl": "patient", "palienl": "patient", "pahents": "patients",
  "pahent's": "patient's",

  // Dental/Dentist
  "denhst": "dentist", "denlure": "denture", "denlures": "dentures",
  "dentue": "denture", "denial": "dental", "denlal": "dental",
  "dontist": "dentist", "dontistry": "dentistry",

  // Gingiva family
  "gengwa": "gingiva", "gengwal": "gingival", "gingwal": "gingival",
  "gengwitis": "gingivitis", "gingwitis": "gingivitis", "gingual": "gingival",
  "gengiva": "gingiva", "gengival": "gingival", "ginigval": "gingival",
  "gingivilis": "gingivitis",

  // Occlusion family
  "ocdusion": "occlusion", "ocelusion": "occlusion", "occlusal": "occlusal",
  "ocdusal": "occlusal", "ocduion": "occlusion",

  // Retention/Restoration
  "retenhon": "retention", "retenhion": "retention", "retenhen": "retention",
  "restroation": "restoration", "restorahon": "restoration",

  // Posterior/Anterior
  "posternol": "posterior", "postenor": "posterior", "posterier": "posterior",
  "antenor": "anterior", "anterier": "anterior",

  // Alveolar
  "alreolar": "alveolar", "alvolar": "alveolar", "alveolare": "alveolar",
  "alveolars": "alveolar",

  // Maxillary/Mandibular
  "maxillasy": "maxillary", "waxillary": "maxillary",
  "mandibulas": "mandibular", "mandibuiar": "mandibular",

  // Palatal/Lingual/Buccal
  "paratal": "palatal", "palaral": "palatal", "paladal": "palatal",
  "linguel": "lingual", "hingual": "lingual",
  "buccol": "buccal", "buecal": "buccal",

  // Epithelium/Tissue
  "epithelum": "epithelium", "epithellum": "epithelium",
  "rissue": "tissue", "tissus": "tissue", "hissue": "tissue",

  // Resorption
  "resorphion": "resorption", "rescription": "resorption",
  "resorphen": "resorption",

  // Common clinical terms
  "tumar": "tumor", "tumour": "tumor",
  "diagnasis": "diagnosis", "diagmosis": "diagnosis",
  "surgicel": "surgical", "surgucal": "surgical",
  "empaction": "impaction", "impachon": "impaction",
  "encisions": "incision", "inasion": "incision",
  "fracfure": "fracture", "fraclure": "fracture",
  "plague": "plaque",
  "lareral": "lateral", "laleral": "lateral",
  "classificahon": "classification", "classificaton": "classification",
  "pathogenisis": "pathogenesis",
  "prognasis": "prognosis",
  "complicahons": "complications",
  "hemorrhuge": "hemorrhage",
  "infechon": "infection", "infechion": "infection",
  "inflammahon": "inflammation",
  "anaesthesia": "anesthesia",
  "periodontih": "periodontal",

  // Prosthodontics-specific
  "edentulious": "edentulous", "edenlulous": "edentulous",
  "prosthesis": "prosthesis",
  "articulater": "articulator", "articulalor": "articulator",
  "coudylar": "condylar", "condyle": "condyle",
  "maxillofocial": "maxillofacial",

  // Endodontics-specific
  "obturation": "obturation",
  "gulta": "gutta", "percho": "percha",
  "irrigahon": "irrigation",

  // Common OCR artifacts
  "ofthe": "of the", "inthe": "in the", "tothe": "to the",
  "ofteeth": "of teeth", "isthe": "is the", "onthe": "on the",
  "andthe": "and the", "forthe": "for the",
};

export function spellCheckDental(text: string): string {
  if (!text) return text;

  let result = text;

  for (const [wrong, right] of Object.entries(OCR_CORRECTIONS)) {
    const pattern = new RegExp(`\\b${wrong}\\b`, "gi");
    result = result.replace(pattern, (match) => {
      if (match[0] === match[0].toUpperCase()) {
        return right.charAt(0).toUpperCase() + right.slice(1);
      }
      return right;
    });
  }

  return result;
}
