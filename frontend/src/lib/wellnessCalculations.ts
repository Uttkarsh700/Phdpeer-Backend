export interface SectionScores {
  supervision: number[];
  progress: number[];
  clarity: number[];
  workload: number[];
  funding: number[];
  support: number[];
  wellbeing: number[];
  career: number[];
}

export interface AutoData {
  milestoneCompletion: number; // 0-100
  avgDelay: number; // days
  supervisorResponseTime: number; // days
}

export interface CalculationResults {
  D1: number;
  D2: number;
  D3: number;
  D4: number;
  D5: number;
  D6: number;
  D7: number;
  D8: number;
  RI: number;
  DI: number;
  RCI: number;
  previousRCI?: number;
  rciDelta?: number;
  band: "Thriving" | "Vulnerable" | "At-Risk";
}

// Convert Likert scores (1-5) to 0-100 scale
const scaleScore = (scores: number[]): number => {
  if (scores.length === 0) return 0;
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
  return ((avg - 1) / 4) * 100; // Convert 1-5 to 0-100
};

// Apply EMA smoothing
const applyEMA = (current: number, previous?: number, alpha: number = 0.3): number => {
  if (previous === undefined) return current;
  return alpha * current + (1 - alpha) * previous;
};

export const calculateWellnessIndices = (
  sections: SectionScores,
  autoData: AutoData,
  previousRCI?: number
): CalculationResults => {
  // Calculate D1-D8 (0-100 scale)
  const D1 = scaleScore(sections.supervision);
  const D2 = scaleScore(sections.progress);
  const D3 = scaleScore(sections.clarity);
  const D4 = scaleScore(sections.workload);
  const D5 = scaleScore(sections.funding);
  const D6 = scaleScore(sections.support);
  const D7 = scaleScore(sections.wellbeing);
  const D8 = scaleScore(sections.career);

  // Integrate auto data into relevant dimensions
  const D2_adjusted = (D2 + autoData.milestoneCompletion) / 2;
  const D1_adjusted = D1 * (1 - Math.min(autoData.supervisorResponseTime / 14, 0.3));

  // Calculate RI (Research Index): avg of research-focused dimensions
  const RI = (D1_adjusted + D2_adjusted + D3 + D4) / 4;

  // Calculate DI (Development Index): avg of development-focused dimensions
  const DI = (D5 + D6 + D7 + D8) / 4;

  // Calculate RCI (Research Climate Index): weighted combination
  const rawRCI = 0.6 * RI + 0.4 * DI;

  // Apply EMA smoothing if previous RCI exists
  const RCI = applyEMA(rawRCI, previousRCI, 0.3);

  // Calculate delta
  const rciDelta = previousRCI !== undefined ? RCI - previousRCI : undefined;

  // Determine band
  let band: "Thriving" | "Vulnerable" | "At-Risk";
  if (RCI >= 70) {
    band = "Thriving";
  } else if (RCI >= 40) {
    band = "Vulnerable";
  } else {
    band = "At-Risk";
  }

  return {
    D1,
    D2: D2_adjusted,
    D3,
    D4,
    D5,
    D6,
    D7,
    D8,
    RI,
    DI,
    RCI,
    previousRCI,
    rciDelta,
    band,
  };
};

export const getSectionColor = (section: keyof SectionScores): string => {
  const colors: Record<keyof SectionScores, string> = {
    supervision: "hsl(var(--wellness-supervision))",
    progress: "hsl(var(--wellness-progress))",
    clarity: "hsl(var(--wellness-clarity))",
    workload: "hsl(var(--wellness-workload))",
    funding: "hsl(var(--wellness-funding))",
    support: "hsl(var(--wellness-support))",
    wellbeing: "hsl(var(--wellness-wellbeing))",
    career: "hsl(var(--wellness-career))",
  };
  return colors[section];
};

export const getBandColor = (band: "Thriving" | "Vulnerable" | "At-Risk"): string => {
  const colors = {
    Thriving: "hsl(var(--success))",
    Vulnerable: "hsl(var(--warning))",
    "At-Risk": "hsl(var(--destructive))",
  };
  return colors[band];
};
