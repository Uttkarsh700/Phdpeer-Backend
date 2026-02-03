/**
 * Timeline Schema Types
 * 
 * Schema-driven types for rendering timelines dynamically.
 * Backend provides schema that defines structure and field mappings.
 */

/**
 * Field type definitions for rendering
 */
export type FieldType = 
  | 'text'
  | 'number'
  | 'date'
  | 'boolean'
  | 'status'
  | 'badge'
  | 'progress';

/**
 * Field configuration from backend schema
 */
export interface FieldConfig {
  /** Field key in the data object */
  key: string;
  /** Display label */
  label: string;
  /** Field type for rendering */
  type: FieldType;
  /** Optional formatter function name or pattern */
  format?: string;
  /** Optional CSS class for styling */
  className?: string;
  /** Whether field is required */
  required?: boolean;
  /** Optional default value */
  defaultValue?: any;
}

/**
 * Stage schema configuration
 */
export interface StageSchema {
  /** Entity type identifier */
  entityType: 'stage';
  /** Fields to render for stages */
  fields: FieldConfig[];
  /** Field to use as primary identifier */
  idField: string;
  /** Field to use for ordering */
  orderField: string;
  /** Field to use as title/heading */
  titleField: string;
  /** Optional field to use as description */
  descriptionField?: string;
  /** Fields to display in header section */
  headerFields?: string[];
  /** Fields to display in metadata section */
  metadataFields?: string[];
}

/**
 * Milestone schema configuration
 */
export interface MilestoneSchema {
  /** Entity type identifier */
  entityType: 'milestone';
  /** Fields to render for milestones */
  fields: FieldConfig[];
  /** Field to use as primary identifier */
  idField: string;
  /** Field to use for ordering */
  orderField: string;
  /** Field to use as title/heading */
  titleField: string;
  /** Optional field to use as description */
  descriptionField?: string;
  /** Fields to display in main content */
  contentFields?: string[];
  /** Fields to display in metadata section */
  metadataFields?: string[];
}

/**
 * Complete timeline schema from backend
 */
export interface TimelineSchema {
  /** Schema version */
  version: string;
  /** Stage schema configuration */
  stage: StageSchema;
  /** Milestone schema configuration */
  milestone: MilestoneSchema;
  /** Optional custom renderer configurations */
  renderers?: {
    stage?: {
      headerComponent?: string;
      contentComponent?: string;
    };
    milestone?: {
      cardComponent?: string;
      badgeComponent?: string;
    };
  };
}

/**
 * Timeline data structure (generic, schema-driven)
 */
export interface TimelineData {
  /** Timeline metadata */
  timeline: Record<string, any>;
  /** Stages array (structure defined by schema) */
  stages: Array<{
    /** Stage data (fields defined by schema) */
    [key: string]: any;
    /** Nested milestones */
    milestones?: Array<Record<string, any>>;
  }>;
  /** Optional metadata */
  metadata?: Record<string, any>;
}
