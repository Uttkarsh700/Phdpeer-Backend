import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface GanttEvent {
  label: string;
  type: "internal" | "grant" | "cfp" | "data" | "journal";
  suggested_date: string;
  desc: string;
  isAdded: boolean;
  isCompleted: boolean;
}

interface GanttChartProps {
  events: GanttEvent[];
}

export const GanttChart = ({ events }: GanttChartProps) => {
  // Parse dates and calculate positions
  const parseDate = (dateStr: string): Date => {
    const [month, year] = dateStr.split(' ');
    const monthMap: { [key: string]: number } = {
      'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
      'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
    };
    return new Date(parseInt(year), monthMap[month], 1);
  };

  const dates = events.map(e => parseDate(e.suggested_date));
  const minDate = new Date(Math.min(...dates.map(d => d.getTime())));
  const maxDate = new Date(Math.max(...dates.map(d => d.getTime())));
  
  // Add padding to date range
  minDate.setMonth(minDate.getMonth() - 1);
  maxDate.setMonth(maxDate.getMonth() + 2);

  const totalMonths = (maxDate.getFullYear() - minDate.getFullYear()) * 12 + 
                      (maxDate.getMonth() - minDate.getMonth());

  // Generate month markers
  const monthMarkers: string[] = [];
  for (let i = 0; i <= totalMonths; i++) {
    const date = new Date(minDate);
    date.setMonth(date.getMonth() + i);
    monthMarkers.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
  }

  // Calculate position for each event
  const getPosition = (date: Date): number => {
    const months = (date.getFullYear() - minDate.getFullYear()) * 12 + 
                   (date.getMonth() - minDate.getMonth());
    return (months / totalMonths) * 100;
  };

  const typeColors = {
    internal: { bg: "bg-blue-500/80", border: "border-blue-500", text: "text-blue-400" },
    grant: { bg: "bg-green-500/80", border: "border-green-500", text: "text-green-400" },
    cfp: { bg: "bg-purple-500/80", border: "border-purple-500", text: "text-purple-400" },
    data: { bg: "bg-yellow-500/80", border: "border-yellow-500", text: "text-yellow-400" },
    journal: { bg: "bg-red-500/80", border: "border-red-500", text: "text-red-400" }
  };

  return (
    <Card className="bg-[#0E0E10] border-white/10">
      <CardHeader>
        <CardTitle className="text-white">Research Timeline - Gantt Chart</CardTitle>
        <CardDescription className="text-muted-foreground">
          Visual representation of your research milestones and deadlines
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative overflow-x-auto">
          <div className="min-w-[1000px]">
            {/* Timeline Header */}
            <div className="flex justify-between mb-2 pb-2 border-b border-white/10">
              {monthMarkers.filter((_, i) => i % 2 === 0).map((month, idx) => (
                <div key={idx} className="text-xs text-muted-foreground font-medium">
                  {month}
                </div>
              ))}
            </div>

            {/* Gantt Bars */}
            <div className="space-y-3 mt-6">
              {events.map((event, index) => {
                const eventDate = parseDate(event.suggested_date);
                const position = getPosition(eventDate);
                const barWidth = 8; // Width in percentage representing ~2 months
                const colors = typeColors[event.type];
                
                let statusBg = 'bg-muted/20';
                let statusBorder = 'border-muted';
                
                if (event.isCompleted) {
                  statusBg = 'bg-emerald-500/80';
                  statusBorder = 'border-emerald-500';
                } else if (event.isAdded) {
                  statusBg = colors.bg;
                  statusBorder = colors.border;
                }

                return (
                  <div key={index} className="relative">
                    {/* Event Label */}
                    <div className="flex items-center mb-1">
                      <div className="w-[200px] flex-shrink-0 pr-4">
                        <p className="text-sm text-foreground font-medium truncate" title={event.label}>
                          {event.label}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs ${colors.text} uppercase font-semibold`}>
                            {event.type}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {event.suggested_date}
                          </span>
                        </div>
                      </div>

                      {/* Timeline Bar Container */}
                      <div className="flex-1 relative h-8">
                        {/* Background Grid Lines */}
                        <div className="absolute inset-0 flex">
                          {monthMarkers.map((_, idx) => (
                            <div 
                              key={idx} 
                              className="flex-1 border-r border-white/5"
                            />
                          ))}
                        </div>

                        {/* Gantt Bar */}
                        <div
                          className={`absolute h-6 rounded border-2 ${statusBg} ${statusBorder} 
                                    transition-all duration-300 hover:scale-105 hover:shadow-lg 
                                    cursor-pointer group z-10`}
                          style={{ 
                            left: `${position}%`,
                            width: `${barWidth}%`,
                            top: '1px'
                          }}
                        >
                          {/* Status Indicator */}
                          <div className="absolute inset-0 flex items-center justify-center">
                            {event.isCompleted && (
                              <span className="text-white text-xs font-bold">✓</span>
                            )}
                            {event.isAdded && !event.isCompleted && (
                              <span className="text-white text-xs font-bold">●</span>
                            )}
                          </div>

                          {/* Tooltip */}
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 
                                        hidden group-hover:block z-20 w-72 p-3 
                                        bg-popover border border-border rounded-lg shadow-xl">
                            <p className="text-foreground font-semibold text-sm mb-1">
                              {event.label}
                            </p>
                            <p className="text-muted-foreground text-xs mb-2">
                              {event.desc}
                            </p>
                            <div className="flex justify-between items-center">
                              <span className={`text-xs ${colors.text} font-semibold`}>
                                {event.suggested_date}
                              </span>
                              <span className={`text-xs px-2 py-1 rounded ${
                                event.isCompleted 
                                  ? 'bg-emerald-500 text-white' 
                                  : event.isAdded 
                                    ? `${colors.bg} text-white` 
                                    : 'bg-muted text-muted-foreground'
                              }`}>
                                {event.isCompleted ? 'Completed' : event.isAdded ? 'Added' : 'Pending'}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Date Marker Line */}
                        <div
                          className="absolute w-px h-8 bg-white/20"
                          style={{ 
                            left: `${position}%`,
                            top: '0'
                          }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="mt-8 pt-4 border-t border-white/10">
              <div className="flex flex-wrap gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-muted/20 border-2 border-muted" />
                  <span className="text-muted-foreground">Pending</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-blue-500/80 border-2 border-blue-500" />
                  <span className="text-muted-foreground">Added</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-emerald-500/80 border-2 border-emerald-500" />
                  <span className="text-muted-foreground">Completed</span>
                </div>
                <div className="ml-8 flex items-center gap-4">
                  {Object.entries(typeColors).map(([type, colors]) => (
                    <div key={type} className="flex items-center gap-2">
                      <span className={`${colors.text} text-xs uppercase font-semibold`}>
                        {type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
