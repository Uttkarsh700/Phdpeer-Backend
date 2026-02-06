import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, Cell } from "recharts";
import { TrendingUp, TrendingDown, Download, Filter, Brain } from "lucide-react";
import { toast } from "sonner";

const UniversityDashboard = () => {
  const [selectedDept, setSelectedDept] = useState("all");
  const [selectedBand, setSelectedBand] = useState("all");
  const [activityFeed, setActivityFeed] = useState([
    "📊 3 researchers flagged at-risk this week.",
    "💼 2 new industry collaborations started (Cisco, Pfizer).",
    "🧠 Average RCI up +4% this quarter.",
    "📄 5 new publications entered the pipeline.",
  ]);

  // Add new activity every 5 seconds
  useEffect(() => {
    const activities = [
      "🎯 New milestone completed in Engineering dept.",
      "💰 €45K funding secured for Business research.",
      "📈 RCI improvement: 3 researchers moved to Thriving band.",
      "🤝 Cross-department collaboration initiated.",
      "⚠️ Supervision delay alert: 2 researchers need check-in.",
    ];

    const interval = setInterval(() => {
      const randomActivity = activities[Math.floor(Math.random() * activities.length)];
      setActivityFeed((prev) => [randomActivity, ...prev.slice(0, 9)]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const metrics = [
    { metric: "Avg Research Continuity Index (RCI)", value: "72.4", trend: "+4.2% QoQ", up: true },
    { metric: "At-Risk Researchers", value: "12%", trend: "▼ -1.3%", up: true },
    { metric: "Total Funding Tracked", value: "€1.46M", trend: "+€120k", up: true },
    { metric: "Active Projects", value: "92", trend: "+8 new", up: true },
    { metric: "Publications in Pipeline", value: "56", trend: "+9 under review", up: true },
  ];

  const heatmapData = [
    { name: "Dr. Amara Khan", dept: "Business", rci: 82, time: 6, funding: "€25,000", supervisor: "Dr. M. Rossi" },
    { name: "Dr. Lucas Moretti", dept: "Engineering", rci: 68, time: 12, funding: "€19,000", supervisor: "Dr. A. Chen" },
    { name: "Dr. Sara Nguyen", dept: "Social Sciences", rci: 58, time: 10, funding: "€21,000", supervisor: "Dr. K. O'Brien" },
    { name: "Dr. Ravi Menon", dept: "Computing", rci: 77, time: 5, funding: "€22,500", supervisor: "Dr. M. Rossi" },
    { name: "Dr. Emma Wilson", dept: "Business", rci: 91, time: 4, funding: "€28,000", supervisor: "Dr. L. Park" },
    { name: "Dr. James O'Connor", dept: "Engineering", rci: 74, time: 8, funding: "€23,500", supervisor: "Dr. A. Chen" },
    { name: "Dr. Priya Sharma", dept: "Computing", rci: 64, time: 14, funding: "€20,000", supervisor: "Dr. T. Kim" },
    { name: "Dr. Michael Brown", dept: "Social Sciences", rci: 85, time: 7, funding: "€26,000", supervisor: "Dr. K. O'Brien" },
  ];

  const fundingData = [
    { dept: "Business", allocated: 600000, utilized: 540000, roi: 89 },
    { dept: "Engineering", allocated: 400000, utilized: 380000, roi: 95 },
    { dept: "Social Sciences", allocated: 460000, utilized: 420000, roi: 91 },
    { dept: "Computing", allocated: 380000, utilized: 350000, roi: 92 },
  ];

  const publications = [
    { researcher: "Dr. Amara Khan", journal: "Entrepreneurship Theory & Practice", stage: "Under Review", impact: 5.4 },
    { researcher: "Dr. Lucas Moretti", journal: "Small Business Economics", stage: "Drafting", impact: 4.9 },
    { researcher: "Dr. Sara Nguyen", journal: "R&D Management", stage: "Accepted", impact: 3.7 },
    { researcher: "Dr. Emma Wilson", journal: "Strategic Management Journal", stage: "Revisions", impact: 6.2 },
  ];

  const getColor = (rci: number) => {
    if (rci >= 75) return "#00B37E"; // Green - Thriving
    if (rci >= 60) return "#F59E0B"; // Yellow - Vulnerable
    return "#EF4444"; // Red - At-Risk
  };

  const filteredHeatmap = heatmapData.filter((item) => {
    if (selectedDept !== "all" && item.dept !== selectedDept) return false;
    if (selectedBand === "thriving" && item.rci < 75) return false;
    if (selectedBand === "vulnerable" && (item.rci < 60 || item.rci >= 75)) return false;
    if (selectedBand === "at-risk" && item.rci >= 60) return false;
    return true;
  });

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#0E0E10] border border-[#E69219] rounded-lg p-3 shadow-lg">
          <p className="text-white font-semibold">{data.name}</p>
          <p className="text-[#C8C8C8] text-sm">{data.dept}</p>
          <p className="text-[#E69219] text-sm">RCI: {data.rci}</p>
          <p className="text-[#C8C8C8] text-sm">Funding: {data.funding}</p>
          <p className="text-[#C8C8C8] text-sm">Supervisor: {data.supervisor}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold mb-2">Frensei Institutional & Management Dashboard</h1>
              <p className="text-[#C8C8C8] text-lg">
                Real-time visibility into research continuity, funding, and outcomes, powered by Frensei's patent-pending ecosystem.
              </p>
            </div>
            <Badge className="bg-[#E69219] text-black hover:bg-[#DB5614] px-4 py-2 text-sm whitespace-nowrap">
              <Brain className="h-4 w-4 mr-2" />
              Powered by CETA™, CPA™, DTSP™, and SAL™ (Patent Pending)
            </Badge>
          </div>
        </div>

        <div className="flex gap-6">
          {/* Filter Sidebar */}
          <div className="w-64 flex-shrink-0">
            <Card className="bg-[#0E0E10] border-[#E69219]/20 sticky top-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Filter className="h-5 w-5" />
                  Filters
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm text-[#C8C8C8] mb-2 block">Department</label>
                  <Select value={selectedDept} onValueChange={setSelectedDept}>
                    <SelectTrigger className="bg-black border-[#E69219]/30 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Departments</SelectItem>
                      <SelectItem value="Business">Business</SelectItem>
                      <SelectItem value="Engineering">Engineering</SelectItem>
                      <SelectItem value="Social Sciences">Social Sciences</SelectItem>
                      <SelectItem value="Computing">Computing</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm text-[#C8C8C8] mb-2 block">RCI Band</label>
                  <Select value={selectedBand} onValueChange={setSelectedBand}>
                    <SelectTrigger className="bg-black border-[#E69219]/30 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Bands</SelectItem>
                      <SelectItem value="thriving">Thriving (75+)</SelectItem>
                      <SelectItem value="vulnerable">Vulnerable (60-75)</SelectItem>
                      <SelectItem value="at-risk">At-Risk (&lt;60)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="flex-1 space-y-6">
            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {metrics.map((item, idx) => (
                <Card key={idx} className="bg-[#0E0E10] border-t-2 border-t-[#E69219] border-[#E69219]/20 hover:shadow-[0_0_20px_rgba(230,146,25,0.3)] transition-all">
                  <CardContent className="p-4">
                    <p className="text-[#C8C8C8] text-xs mb-2">{item.metric}</p>
                    <p className="text-3xl font-bold text-white mb-1">{item.value}</p>
                    <div className="flex items-center gap-1 text-xs">
                      {item.up ? (
                        <TrendingUp className="h-3 w-3 text-[#00B37E]" />
                      ) : (
                        <TrendingDown className="h-3 w-3 text-[#EF4444]" />
                      )}
                      <span className={item.up ? "text-[#00B37E]" : "text-[#EF4444]"}>{item.trend}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Risk Heatmap */}
            <Card className="bg-[#0E0E10] border-[#E69219]/20">
              <CardHeader>
                <CardTitle className="text-white text-xl">Research Continuity Overview</CardTitle>
                <p className="text-[#C8C8C8] text-sm">Researcher distribution by RCI and time to completion</p>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis
                      type="number"
                      dataKey="time"
                      name="Time to Completion"
                      unit=" mo"
                      stroke="#C8C8C8"
                      label={{ value: "Time to Completion (months)", position: "insideBottom", offset: -10, fill: "#C8C8C8" }}
                    />
                    <YAxis
                      type="number"
                      dataKey="rci"
                      name="RCI"
                      stroke="#C8C8C8"
                      label={{ value: "Research Continuity Index", angle: -90, position: "insideLeft", fill: "#C8C8C8" }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Scatter data={filteredHeatmap} fill="#E69219">
                      {filteredHeatmap.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getColor(entry.rci)} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-6 mt-4">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[#00B37E]"></div>
                    <span className="text-sm text-[#C8C8C8]">Thriving (75+)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[#F59E0B]"></div>
                    <span className="text-sm text-[#C8C8C8]">Vulnerable (60-75)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[#EF4444]"></div>
                    <span className="text-sm text-[#C8C8C8]">At-Risk (&lt;60)</span>
                  </div>
                </div>
                <div className="mt-6 text-center">
                  <Button
                    onClick={() =>
                      toast.success("Intervention suggestions generated", {
                        description: "Check email for detailed action items.",
                      })
                    }
                    className="bg-[#E69219] text-black hover:bg-[#DB5614] hover:shadow-[0_0_20px_rgba(230,146,25,0.5)]"
                  >
                    View Intervention Suggestions
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Funding & Publications Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Funding Panel */}
              <Card className="bg-[#0E0E10] border-[#E69219]/20">
                <CardHeader>
                  <CardTitle className="text-white text-xl">Funding Utilization & ROI by Department</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={fundingData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis dataKey="dept" stroke="#C8C8C8" />
                      <YAxis stroke="#C8C8C8" />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#0E0E10", border: "1px solid #E69219", borderRadius: "8px" }}
                        labelStyle={{ color: "#fff" }}
                      />
                      <Bar dataKey="utilized" fill="#E69219" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="allocated" fill="#C8C8C8" radius={[8, 8, 0, 0]} opacity={0.3} />
                    </BarChart>
                  </ResponsiveContainer>
                  <div className="mt-6 space-y-3">
                    <p className="text-[#00B37E] text-center font-semibold">
                      Estimated loss prevented: €2.3M through early risk intervention.
                    </p>
                    <div className="flex gap-3 justify-center">
                      <Button
                        onClick={() => toast.success("📁 Funding report exported successfully")}
                        variant="outline"
                        className="border-[#E69219] text-[#E69219] hover:bg-[#E69219] hover:text-black"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Export Funding Report
                      </Button>
                      <Button
                        onClick={() => toast.info("Opening detailed breakdown...")}
                        className="bg-[#E69219] text-black hover:bg-[#DB5614]"
                      >
                        View Detailed Breakdown
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Publication Tracker */}
              <Card className="bg-[#0E0E10] border-[#E69219]/20">
                <CardHeader>
                  <CardTitle className="text-white text-xl">Publication & Impact Tracker</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow className="border-[#E69219]/20">
                        <TableHead className="text-[#C8C8C8]">Researcher</TableHead>
                        <TableHead className="text-[#C8C8C8]">Journal Target</TableHead>
                        <TableHead className="text-[#C8C8C8]">Stage</TableHead>
                        <TableHead className="text-[#C8C8C8]">Impact</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {publications.map((pub, idx) => (
                        <TableRow key={idx} className="border-[#E69219]/10 hover:bg-[#E69219]/5">
                          <TableCell className="text-white font-medium">{pub.researcher}</TableCell>
                          <TableCell className="text-[#C8C8C8] text-sm">{pub.journal}</TableCell>
                          <TableCell>
                            <Badge
                              className={
                                pub.stage === "Accepted"
                                  ? "bg-[#00B37E]/20 text-[#00B37E]"
                                  : pub.stage === "Under Review"
                                  ? "bg-[#E69219]/20 text-[#E69219]"
                                  : "bg-[#C8C8C8]/20 text-[#C8C8C8]"
                              }
                            >
                              {pub.stage}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-[#E69219] font-semibold">{pub.impact}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  <div className="flex gap-3 justify-center mt-6">
                    <Button
                      onClick={() => toast.success("Publication added to tracker")}
                      variant="outline"
                      className="border-[#E69219] text-[#E69219] hover:bg-[#E69219] hover:text-black"
                    >
                      Add New Publication
                    </Button>
                    <Button
                      onClick={() => toast.success("📁 Publication summary exported")}
                      className="bg-[#E69219] text-black hover:bg-[#DB5614]"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export Summary
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Activity Feed */}
          <div className="w-80 flex-shrink-0">
            <Card className="bg-[#0E0E10] border-[#E69219]/20 sticky top-6">
              <CardHeader>
                <CardTitle className="text-white">Institutional Activity Feed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-[800px] overflow-y-auto">
                  {activityFeed.map((activity, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-black/50 rounded-lg border border-[#E69219]/10 text-sm text-[#C8C8C8] animate-fade-in hover:border-[#E69219]/30 transition-all"
                    >
                      {activity}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-[#C8C8C8] text-sm py-6 border-t border-[#E69219]/20">
          <p>
            All insights generated through Frensei's proprietary algorithms, CETA™, CPA™, DTSP™, and SAL™, under a patent-pending
            end-to-end process patent. Institutional beta release Q1 2026.
          </p>
        </div>
      </div>
    </div>
  );
};

export default UniversityDashboard;
