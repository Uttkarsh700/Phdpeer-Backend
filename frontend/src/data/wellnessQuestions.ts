export interface Question {
  id: string;
  text: string;
}

export interface WellnessSection {
  id: string;
  title: string;
  description: string;
  questions: Question[];
}

export const wellnessSections: WellnessSection[] = [
  {
    id: "supervision",
    title: "Supervision",
    description: "Quality and effectiveness of supervisory support",
    questions: [
      { id: "sup1", text: "My supervisor provides clear and constructive feedback on my work" },
      { id: "sup2", text: "I have regular and meaningful meetings with my supervisor" },
      { id: "sup3", text: "My supervisor is responsive to my questions and concerns" },
      { id: "sup4", text: "I feel supported in developing my research skills" },
    ],
  },
  {
    id: "progress",
    title: "Progress",
    description: "Research advancement and milestone achievement",
    questions: [
      { id: "prog1", text: "I am making satisfactory progress on my research milestones" },
      { id: "prog2", text: "I feel confident about completing my research on time" },
      { id: "prog3", text: "My research goals are clearly defined and achievable" },
      { id: "prog4", text: "I have overcome recent research challenges effectively" },
    ],
  },
  {
    id: "clarity",
    title: "Clarity",
    description: "Understanding of research direction and expectations",
    questions: [
      { id: "clar1", text: "I have a clear understanding of my research objectives" },
      { id: "clar2", text: "I know what is expected of me in my research program" },
      { id: "clar3", text: "The path to completing my degree is well-defined" },
      { id: "clar4", text: "I understand how my work contributes to the broader field" },
    ],
  },
  {
    id: "workload",
    title: "Workload",
    description: "Balance and manageability of research and other responsibilities",
    questions: [
      { id: "work1", text: "My current workload is manageable and sustainable" },
      { id: "work2", text: "I have adequate time to focus on my research" },
      { id: "work3", text: "I can balance research with other commitments effectively" },
      { id: "work4", text: "I rarely feel overwhelmed by my responsibilities" },
      { id: "work5", text: "I have control over my work schedule and priorities" },
    ],
  },
  {
    id: "funding",
    title: "Funding",
    description: "Financial support and resource availability",
    questions: [
      { id: "fund1", text: "I have adequate funding to support my research" },
      { id: "fund2", text: "I am not worried about my financial situation" },
      { id: "fund3", text: "I have access to the resources I need for my research" },
      { id: "fund4", text: "Funding concerns do not impact my research productivity" },
    ],
  },
  {
    id: "support",
    title: "Support",
    description: "Departmental and peer support systems",
    questions: [
      { id: "supp1", text: "I feel part of a supportive research community" },
      { id: "supp2", text: "I can rely on peers for collaboration and support" },
      { id: "supp3", text: "The department provides adequate support services" },
      { id: "supp4", text: "I feel valued and respected in my research environment" },
    ],
  },
  {
    id: "wellbeing",
    title: "Well-being",
    description: "Physical and mental health status",
    questions: [
      { id: "well1", text: "I maintain a healthy work-life balance" },
      { id: "well2", text: "I feel mentally and physically well" },
      { id: "well3", text: "I engage in regular self-care activities" },
      { id: "well4", text: "Stress and anxiety do not significantly impact my daily life" },
      { id: "well5", text: "I feel energized and motivated most days" },
    ],
  },
  {
    id: "career",
    title: "Career",
    description: "Future career prospects and professional development",
    questions: [
      { id: "car1", text: "I am optimistic about my future career prospects" },
      { id: "car2", text: "I am developing skills relevant to my career goals" },
      { id: "car3", text: "I have a clear plan for my post-research career" },
      { id: "car4", text: "I feel my research will open doors for future opportunities" },
    ],
  },
];
