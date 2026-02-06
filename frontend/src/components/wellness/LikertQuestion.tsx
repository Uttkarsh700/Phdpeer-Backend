import { useState } from "react";
import { cn } from "@/lib/utils";

interface LikertQuestionProps {
  question: string;
  value: number;
  onChange: (value: number) => void;
}

const LIKERT_OPTIONS = [
  { value: 1, label: "Strongly Disagree" },
  { value: 2, label: "Disagree" },
  { value: 3, label: "Neutral" },
  { value: 4, label: "Agree" },
  { value: 5, label: "Strongly Agree" },
];

export const LikertQuestion = ({
  question,
  value,
  onChange,
}: LikertQuestionProps) => {
  const [hovered, setHovered] = useState<number | null>(null);

  return (
    <div className="space-y-3">
      <p className="text-sm font-medium text-foreground">{question}</p>
      <div className="flex gap-2 justify-between">
        {LIKERT_OPTIONS.map((option) => (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            onMouseEnter={() => setHovered(option.value)}
            onMouseLeave={() => setHovered(null)}
            className={cn(
              "relative flex flex-col items-center gap-1 p-2 rounded-lg transition-all",
              "hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring",
              value === option.value && "bg-primary/10"
            )}
          >
            <div
              className={cn(
                "w-10 h-10 rounded-full border-2 flex items-center justify-center",
                "transition-all duration-200",
                value === option.value
                  ? "border-primary bg-primary text-primary-foreground scale-110"
                  : hovered === option.value
                  ? "border-primary/50 scale-105"
                  : "border-muted-foreground/30"
              )}
            >
              <span className="text-sm font-semibold">{option.value}</span>
            </div>
            <span
              className={cn(
                "text-[10px] text-center max-w-[60px] transition-opacity",
                hovered === option.value || value === option.value
                  ? "opacity-100"
                  : "opacity-60"
              )}
            >
              {option.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};
