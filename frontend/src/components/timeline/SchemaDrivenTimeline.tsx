/**
 * Schema-Driven Timeline Component
 * 
 * Renders timeline stages and milestones based on backend-provided schema.
 * 
 * Features:
 * - No hardcoded field names
 * - Adapts automatically to new fields
 * - UI driven by schema configuration
 * - Supports custom field types and formatters
 * 
 * @example
 * ```tsx
 * <SchemaDrivenTimeline
 *   schema={timelineSchema}
 *   data={timelineData}
 *   onMilestoneComplete={handleComplete}
 *   readOnly={false}
 * />
 * ```
 */

import React from 'react';
import type { TimelineSchema, TimelineData, FieldConfig } from '@/types/timeline-schema';

export interface SchemaDrivenTimelineProps {
  /** Schema configuration from backend */
  schema: TimelineSchema;
  /** Timeline data to render */
  data: TimelineData;
  /** Optional callback for milestone completion */
  onMilestoneComplete?: (milestoneId: string) => void;
  /** Whether timeline is read-only */
  readOnly?: boolean;
  /** Optional custom field renderers */
  customRenderers?: Record<string, (value: any, field: FieldConfig, data: any) => React.ReactNode>;
}

/**
 * Render a field value based on its type and configuration
 */
function renderField(
  value: any,
  field: FieldConfig,
  data: Record<string, any>,
  customRenderers?: Record<string, (value: any, field: FieldConfig, data: any) => React.ReactNode>
): React.ReactNode {
  // Check for custom renderer first
  if (customRenderers && customRenderers[field.key]) {
    return customRenderers[field.key](value, field, data);
  }

  // Handle null/undefined values
  if (value === null || value === undefined) {
    return field.defaultValue ?? null;
  }

  // Render based on field type
  switch (field.type) {
    case 'text':
      return <span className={field.className}>{String(value)}</span>;

    case 'number':
      const numValue = typeof value === 'number' ? value : parseFloat(value);
      if (isNaN(numValue)) return null;
      return <span className={field.className}>{numValue}</span>;

    case 'date':
      try {
        const date = new Date(value);
        if (isNaN(date.getTime())) return null;
        return (
          <span className={field.className}>
            {date.toLocaleDateString()}
          </span>
        );
      } catch {
        return null;
      }

    case 'boolean':
      return (
        <span className={field.className}>
          {value ? 'Yes' : 'No'}
        </span>
      );

    case 'status':
      const statusValue = String(value).toUpperCase();
      const statusColors: Record<string, string> = {
        'COMPLETED': 'bg-green-100 text-green-800',
        'IN_PROGRESS': 'bg-blue-100 text-blue-800',
        'NOT_STARTED': 'bg-gray-100 text-gray-800',
        'PENDING': 'bg-gray-100 text-gray-800',
        'ON_TRACK': 'bg-green-100 text-green-800',
        'DELAYED': 'bg-yellow-100 text-yellow-800',
        'OVERDUE': 'bg-red-100 text-red-800',
      };
      const statusColor = statusColors[statusValue] || 'bg-gray-100 text-gray-800';
      return (
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor} ${field.className || ''}`}>
          {statusValue.replace('_', ' ')}
        </span>
      );

    case 'badge':
      const badgeValue = String(value);
      return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${field.className || 'bg-gray-100 text-gray-800'}`}>
          {badgeValue}
        </span>
      );

    case 'progress':
      const progressValue = typeof value === 'number' ? value : parseFloat(value);
      if (isNaN(progressValue)) return null;
      return (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full"
            style={{ width: `${Math.min(100, Math.max(0, progressValue))}%` }}
          />
        </div>
      );

    default:
      return <span className={field.className}>{String(value)}</span>;
  }
}

/**
 * Render a stage based on schema
 */
function renderStage(
  stage: Record<string, any>,
  schema: TimelineSchema,
  milestones: Array<Record<string, any>>,
  props: SchemaDrivenTimelineProps
): React.ReactNode {
  const stageSchema = schema.stage;
  const milestoneSchema = schema.milestone;

  // Get title and description from schema-defined fields
  const title = stage[stageSchema.titleField] || 'Untitled Stage';
  const description = stageSchema.descriptionField 
    ? stage[stageSchema.descriptionField] 
    : null;

  // Get order value
  const order = stage[stageSchema.orderField] || 0;

  // Get header fields
  const headerFields = stageSchema.headerFields || [];
  const metadataFields = stageSchema.metadataFields || [];

  return (
    <div key={stage[stageSchema.idField]} className="bg-white rounded-lg shadow">
      {/* Stage Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3">
              {/* Order Badge */}
              <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm font-semibold">
                {order}
              </span>
              
              {/* Title and Description */}
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
                {description && (
                  <p className="mt-1 text-sm text-gray-600">{description}</p>
                )}
              </div>
            </div>
          </div>

          {/* Header Fields */}
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            {headerFields.map(fieldKey => {
              const field = stageSchema.fields.find(f => f.key === fieldKey);
              if (!field) return null;
              const value = stage[field.key];
              if (value === null || value === undefined) return null;
              
              return (
                <div key={fieldKey}>
                  {renderField(value, field, stage, props.customRenderers)}
                </div>
              );
            })}
          </div>
        </div>

        {/* Metadata Fields */}
        {metadataFields.length > 0 && (
          <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
            {metadataFields.map(fieldKey => {
              const field = stageSchema.fields.find(f => f.key === fieldKey);
              if (!field) return null;
              const value = stage[field.key];
              if (value === null || value === undefined) return null;
              
              return (
                <div key={fieldKey} className="flex items-center space-x-1">
                  <span className="font-medium">{field.label}:</span>
                  {renderField(value, field, stage, props.customRenderers)}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Milestones */}
      <div className="px-6 py-4">
        {milestones.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No milestones in this stage</p>
        ) : (
          <div className="space-y-3">
            {milestones
              .sort((a, b) => {
                const aOrder = a[milestoneSchema.orderField] || 0;
                const bOrder = b[milestoneSchema.orderField] || 0;
                return aOrder - bOrder;
              })
              .map((milestone) => {
                const milestoneId = milestone[milestoneSchema.idField];
                const milestoneTitle = milestone[milestoneSchema.titleField] || 'Untitled Milestone';
                const milestoneDescription = milestoneSchema.descriptionField
                  ? milestone[milestoneSchema.descriptionField]
                  : null;

                // Get content and metadata fields
                const contentFields = milestoneSchema.contentFields || [];
                const milestoneMetadataFields = milestoneSchema.metadataFields || [];

                return (
                  <div
                    key={milestoneId}
                    className="flex items-start space-x-3 p-3 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                  >
                    {/* Completion Indicator */}
                    {milestoneSchema.fields.find(f => f.key === 'is_completed' || f.key === 'isCompleted') && (
                      <div className="flex-shrink-0 mt-1">
                        {props.onMilestoneComplete && !props.readOnly ? (
                          <button
                            onClick={() => props.onMilestoneComplete?.(milestoneId)}
                            disabled={milestone.is_completed || milestone.isCompleted}
                            className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                              milestone.is_completed || milestone.isCompleted
                                ? 'bg-green-500 border-green-500 cursor-default'
                                : 'border-gray-300 hover:bg-gray-50 cursor-pointer'
                            }`}
                          >
                            {(milestone.is_completed || milestone.isCompleted) && (
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </button>
                        ) : (
                          <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                            milestone.is_critical || milestone.isCritical
                              ? 'border-red-500'
                              : 'border-gray-300'
                          } ${milestone.is_completed || milestone.isCompleted ? 'bg-green-500 border-green-500' : ''}`}>
                            {(milestone.is_completed || milestone.isCompleted) && (
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Milestone Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 flex items-center">
                            {milestoneTitle}
                            {/* Critical Badge */}
                            {(milestone.is_critical || milestone.isCritical) && (
                              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                Critical
                              </span>
                            )}
                          </h4>
                          
                          {milestoneDescription && (
                            <p className="mt-1 text-sm text-gray-600">{milestoneDescription}</p>
                          )}

                          {/* Content Fields */}
                          {contentFields.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {contentFields.map(fieldKey => {
                                const field = milestoneSchema.fields.find(f => f.key === fieldKey);
                                if (!field) return null;
                                const value = milestone[field.key];
                                if (value === null || value === undefined) return null;
                                
                                return (
                                  <div key={fieldKey} className="text-xs text-gray-500">
                                    <span className="font-medium">{field.label}:</span>{' '}
                                    {renderField(value, field, milestone, props.customRenderers)}
                                  </div>
                                );
                              })}
                            </div>
                          )}

                          {/* Metadata Fields */}
                          {milestoneMetadataFields.length > 0 && (
                            <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                              {milestoneMetadataFields.map(fieldKey => {
                                const field = milestoneSchema.fields.find(f => f.key === fieldKey);
                                if (!field) return null;
                                const value = milestone[field.key];
                                if (value === null || value === undefined) return null;
                                
                                return (
                                  <div key={fieldKey}>
                                    {renderField(value, field, milestone, props.customRenderers)}
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Schema-Driven Timeline Component
 */
export function SchemaDrivenTimeline(props: SchemaDrivenTimelineProps) {
  const { schema, data } = props;

  // Sort stages by order field
  const sortedStages = [...(data.stages || [])].sort((a, b) => {
    const aOrder = a[schema.stage.orderField] || 0;
    const bOrder = b[schema.stage.orderField] || 0;
    return aOrder - bOrder;
  });

  if (sortedStages.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-600">No stages found in this timeline</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {sortedStages.map((stage) => {
        const stageId = stage[schema.stage.idField];
        const milestones = stage.milestones || [];
        
        return renderStage(stage, schema, milestones, props);
      })}
    </div>
  );
}

export default SchemaDrivenTimeline;
