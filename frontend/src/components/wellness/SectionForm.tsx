import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LikertQuestion } from "./LikertQuestion";
import { RingGauge } from "./RingGauge";
import { WellnessSection } from "@/data/wellnessQuestions";
import { getSectionColor } from "@/lib/wellnessCalculations";

interface SectionFormProps {
  section: WellnessSection;
  responses: Record<string, number>;
  onResponseChange: (questionId: string, value: number) => void;
}

export const SectionForm = ({
  section,
  responses,
  onResponseChange,
}: SectionFormProps) => {
  const sectionResponses = section.questions
    .map((q) => responses[q.id])
    .filter((r) => r !== undefined);
  
  const maxScore = section.questions.length * 5;
  const currentScore = sectionResponses.reduce((sum, r) => sum + r, 0);
  const color = getSectionColor(section.id as any);

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <CardTitle className="text-xl">{section.title}</CardTitle>
            <CardDescription className="mt-1">
              {section.description}
            </CardDescription>
          </div>
          <RingGauge
            score={currentScore}
            maxScore={maxScore}
            color={color}
            size={80}
            strokeWidth={8}
          />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {section.questions.map((question) => (
          <LikertQuestion
            key={question.id}
            question={question.text}
            value={responses[question.id] || 0}
            onChange={(value) => onResponseChange(question.id, value)}
          />
        ))}
      </CardContent>
    </Card>
  );
};
