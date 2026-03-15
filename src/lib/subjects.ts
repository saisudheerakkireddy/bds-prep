export interface Question {
  id: string;
  question: string;
  answer: string;
  analogy?: string;
  highYield: boolean;
  topic: string;
  yearsAsked?: string[];
}

export interface MindMap {
  id: string;
  title: string;
  /** Mermaid diagram syntax string */
  mermaid: string;
  relatedQuestionIds: string[];
}

export interface Subject {
  slug: string;
  name: string;
  shortName: string;
  paperCode: string;
  examDate: string; // ISO date
  examDay: string;
  color: string; // tailwind color key
  icon: string; // emoji
  questions: Question[];
  mindMaps: MindMap[];
}

/** Exam schedule — source: Controller of Examinations, AP */
export const subjects: Subject[] = [
  {
    slug: "prosthodontics",
    name: "Prosthodontics and Crown & Bridge",
    shortName: "Prostho",
    paperCode: "429/409",
    examDate: "2026-03-25",
    examDay: "Wednesday",
    color: "blue",
    icon: "🦷",
    questions: [],
    mindMaps: [],
  },
  {
    slug: "conservative-dentistry",
    name: "Conservative Dentistry and Endodontics",
    shortName: "Cons & Endo",
    paperCode: "430/410",
    examDate: "2026-03-28",
    examDay: "Saturday",
    color: "emerald",
    icon: "🔬",
    questions: [],
    mindMaps: [],
  },
  {
    slug: "oral-surgery",
    name: "Oral Maxillofacial Surgery",
    shortName: "OMFS",
    paperCode: "431/412",
    examDate: "2026-03-30",
    examDay: "Monday",
    color: "red",
    icon: "🏥",
    questions: [],
    mindMaps: [],
  },
  {
    slug: "public-health-dentistry",
    name: "Public Health Dentistry",
    shortName: "Community",
    paperCode: "432",
    examDate: "2026-04-01",
    examDay: "Wednesday",
    color: "teal",
    icon: "🌍",
    questions: [],
    mindMaps: [],
  },
  {
    slug: "oral-medicine",
    name: "Oral Medicine & Radiology",
    shortName: "Oral Med",
    paperCode: "425/413",
    examDate: "2026-04-04",
    examDay: "Saturday",
    color: "purple",
    icon: "📋",
    questions: [],
    mindMaps: [],
  },
  {
    slug: "pedodontics",
    name: "Paediatric & Preventive Dentistry",
    shortName: "Pedo",
    paperCode: "426/415",
    examDate: "2026-04-06",
    examDay: "Monday",
    color: "pink",
    icon: "👶",
    questions: [],
    mindMaps: [],
  },
  {
    slug: "orthodontics",
    name: "Orthodontics & Dentofacial Orthopaedics",
    shortName: "Ortho",
    paperCode: "427/411",
    examDate: "2026-04-08",
    examDay: "Wednesday",
    color: "amber",
    icon: "📐",
    questions: [],
    mindMaps: [],
  },
  {
    slug: "periodontics",
    name: "Periodontics",
    shortName: "Perio",
    paperCode: "428/414",
    examDate: "2026-04-10",
    examDay: "Friday",
    color: "cyan",
    icon: "🧬",
    questions: [],
    mindMaps: [],
  },
];

/** Helper: days remaining until exam */
export function daysUntilExam(examDate: string): number {
  const now = new Date();
  const exam = new Date(examDate);
  const diff = exam.getTime() - now.getTime();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

/** Helper: overall progress (exams completed / total) */
export function examProgress(): {
  completed: number;
  total: number;
  nextSubject: Subject | null;
} {
  const now = new Date();
  const completed = subjects.filter(
    (s) => new Date(s.examDate) < now
  ).length;
  const nextSubject =
    subjects.find((s) => new Date(s.examDate) >= now) ?? null;
  return { completed, total: subjects.length, nextSubject };
}
