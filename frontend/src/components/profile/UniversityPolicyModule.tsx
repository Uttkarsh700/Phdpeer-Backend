import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, Shield } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

export const UniversityPolicyModule = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card className="bg-card/50 border-border/50">
        <CollapsibleTrigger asChild>
          <CardContent className="p-6 cursor-pointer hover:bg-card/70 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-info/10 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-info" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground">
                    Institution-Specific Guidance
                  </h3>
                  <p className="text-sm text-muted-foreground">Modular policy insights</p>
                </div>
              </div>
              {isOpen ? (
                <ChevronUp className="w-5 h-5 text-muted-foreground" />
              ) : (
                <ChevronDown className="w-5 h-5 text-muted-foreground" />
              )}
            </div>
          </CardContent>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="px-6 pb-6 pt-0">
            <div className="space-y-4 pt-4 border-t border-border/30">
              <p className="text-sm text-muted-foreground">
                Your university's doctoral office can customize this section with program rules, 
                ethics guidance, and recommended pacing strategies tailored to your specific institution.
              </p>
              
              <div className="bg-muted/10 rounded-lg p-4 space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-1.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Program Timeline Requirements</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Standard completion: 3-4 years • Annual progress reviews required
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-1.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Ethics & Compliance</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Ethics approval required before data collection begins
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-1.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Supervision Guidelines</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Minimum bi-weekly meetings recommended during active research phases
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <Button
                  variant="outline"
                  className="w-full border-border/50 text-muted-foreground hover:bg-muted/10"
                  disabled
                >
                  Customize with University Policy (Admin Only)
                </Button>
                <p className="text-xs text-muted-foreground text-center mt-2">
                  This section is configured by your university administration
                </p>
              </div>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
};
