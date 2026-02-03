/**
 * Example: Schema-Driven Timeline Usage
 * 
 * Demonstrates how to use SchemaDrivenTimeline component
 * with backend-provided schema and data.
 */

import { SchemaDrivenTimeline } from './SchemaDrivenTimeline';
import type { TimelineSchema, TimelineData } from '@/types/timeline-schema';

/**
 * Example schema from backend
 * 
 * This would typically come from GET /api/v1/timelines/schema
 * or be included in the timeline response.
 */
const exampleSchema: TimelineSchema = {
  version: '1.0',
  stage: {
    entityType: 'stage',
    idField: 'id',
    orderField: 'stage_order',
    titleField: 'title',
    descriptionField: 'description',
    fields: [
      { key: 'id', label: 'ID', type: 'text' },
      { key: 'title', label: 'Title', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'stage_order', label: 'Order', type: 'number' },
      { key: 'duration_months', label: 'Duration', type: 'number' },
      { key: 'status', label: 'Status', type: 'status' },
      { key: 'start_date', label: 'Start Date', type: 'date' },
      { key: 'end_date', label: 'End Date', type: 'date' },
    ],
    headerFields: ['duration_months', 'status'],
    metadataFields: ['start_date', 'end_date'],
  },
  milestone: {
    entityType: 'milestone',
    idField: 'id',
    orderField: 'milestone_order',
    titleField: 'title',
    descriptionField: 'description',
    fields: [
      { key: 'id', label: 'ID', type: 'text' },
      { key: 'title', label: 'Title', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'milestone_order', label: 'Order', type: 'number' },
      { key: 'is_critical', label: 'Critical', type: 'boolean' },
      { key: 'is_completed', label: 'Completed', type: 'boolean' },
      { key: 'target_date', label: 'Target Date', type: 'date' },
      { key: 'actual_completion_date', label: 'Completion Date', type: 'date' },
      { key: 'deliverable_type', label: 'Deliverable Type', type: 'badge' },
    ],
    contentFields: ['deliverable_type'],
    metadataFields: ['target_date', 'actual_completion_date'],
  },
};

/**
 * Example timeline data from backend
 * 
 * Structure matches schema - no hardcoded field names.
 */
const exampleData: TimelineData = {
  timeline: {
    id: 'timeline-123',
    title: 'PhD Timeline',
    status: 'DRAFT',
  },
  stages: [
    {
      id: 'stage-1',
      title: 'Literature Review',
      description: 'Comprehensive review of existing research',
      stage_order: 1,
      duration_months: 6,
      status: 'IN_PROGRESS',
      start_date: '2024-01-01',
      end_date: '2024-06-30',
      milestones: [
        {
          id: 'milestone-1',
          title: 'Complete Literature Survey',
          description: 'Review and synthesize existing research',
          milestone_order: 1,
          is_critical: false,
          is_completed: true,
          target_date: '2024-02-15',
          actual_completion_date: '2024-02-10',
          deliverable_type: 'deliverable',
        },
        {
          id: 'milestone-2',
          title: 'Identify Research Gaps',
          description: 'Analyze literature to identify opportunities',
          milestone_order: 2,
          is_critical: true,
          is_completed: false,
          target_date: '2024-03-01',
          deliverable_type: 'analysis',
        },
      ],
    },
    {
      id: 'stage-2',
      title: 'Methodology Development',
      description: 'Develop research methodology and approach',
      stage_order: 2,
      duration_months: 4,
      status: 'NOT_STARTED',
      milestones: [
        {
          id: 'milestone-3',
          title: 'Design Research Framework',
          description: 'Create framework for research approach',
          milestone_order: 1,
          is_critical: true,
          is_completed: false,
          target_date: '2024-07-15',
          deliverable_type: 'framework',
        },
      ],
    },
  ],
};

/**
 * Example component using schema-driven timeline
 */
export function TimelineExample() {
  const handleMilestoneComplete = (milestoneId: string) => {
    console.log('Complete milestone:', milestoneId);
    // Call API to mark milestone as completed
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        {exampleData.timeline.title}
      </h1>

      {/* Schema-Driven Timeline */}
      <SchemaDrivenTimeline
        schema={exampleSchema}
        data={exampleData}
        onMilestoneComplete={handleMilestoneComplete}
        readOnly={false}
      />
    </div>
  );
}

/**
 * Example: Loading schema from backend
 * 
 * In a real implementation, you would fetch the schema:
 * 
 * ```tsx
 * const [schema, setSchema] = useState<TimelineSchema | null>(null);
 * 
 * useEffect(() => {
 *   // Fetch schema from backend
 *   fetch('/api/v1/timelines/schema')
 *     .then(res => res.json())
 *     .then(setSchema);
 * }, []);
 * 
 * if (!schema) return <Loading />;
 * 
 * return (
 *   <SchemaDrivenTimeline
 *     schema={schema}
 *     data={timelineData}
 *   />
 * );
 * ```
 */

export default TimelineExample;
