/**
 * Validation Utilities
 * 
 * Centralized validation functions for form inputs and business logic.
 */

// Date validation
export const isValidDate = (dateString: string): boolean => {
  if (!dateString) return false;
  const date = new Date(dateString);
  return !isNaN(date.getTime());
};

export const isFutureDate = (dateString: string): boolean => {
  if (!isValidDate(dateString)) return false;
  const date = new Date(dateString);
  const now = new Date();
  now.setHours(0, 0, 0, 0); // Compare dates only, not time
  return date > now;
};

export const isPastDate = (dateString: string): boolean => {
  if (!isValidDate(dateString)) return false;
  const date = new Date(dateString);
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return date < now;
};

export const isDateAfter = (date1: string, date2: string): boolean => {
  if (!isValidDate(date1) || !isValidDate(date2)) return false;
  return new Date(date1) > new Date(date2);
};

export const isDateBefore = (date1: string, date2: string): boolean => {
  if (!isValidDate(date1) || !isValidDate(date2)) return false;
  return new Date(date1) < new Date(date2);
};

// String validation
export const isNonEmptyString = (value: string | undefined | null): boolean => {
  return typeof value === 'string' && value.trim().length > 0;
};

export const hasMinLength = (value: string, minLength: number): boolean => {
  return isNonEmptyString(value) && value.trim().length >= minLength;
};

export const hasMaxLength = (value: string, maxLength: number): boolean => {
  return typeof value === 'string' && value.trim().length <= maxLength;
};

// Number validation
export const isInRange = (value: number, min: number, max: number): boolean => {
  return typeof value === 'number' && !isNaN(value) && value >= min && value <= max;
};

export const isPositiveNumber = (value: number): boolean => {
  return typeof value === 'number' && !isNaN(value) && value > 0;
};

// File validation
export const isValidFileType = (file: File, allowedTypes: string[]): boolean => {
  return allowedTypes.includes(file.type);
};

export const isValidFileSize = (file: File, maxSizeBytes: number): boolean => {
  return file.size <= maxSizeBytes;
};

export const ALLOWED_DOCUMENT_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

// Baseline validation
export interface BaselineValidationResult {
  isValid: boolean;
  errors: string[];
}

export const validateBaselineCreation = (data: {
  programName: string;
  institution: string;
  fieldOfStudy: string;
  startDate: string;
  expectedEndDate?: string;
  documentId?: string;
}): BaselineValidationResult => {
  const errors: string[] = [];

  // Required fields
  if (!isNonEmptyString(data.programName)) {
    errors.push('Program name is required');
  } else if (!hasMinLength(data.programName, 3)) {
    errors.push('Program name must be at least 3 characters');
  } else if (!hasMaxLength(data.programName, 200)) {
    errors.push('Program name must be less than 200 characters');
  }

  if (!isNonEmptyString(data.institution)) {
    errors.push('Institution is required');
  } else if (!hasMinLength(data.institution, 2)) {
    errors.push('Institution name must be at least 2 characters');
  }

  if (!isNonEmptyString(data.fieldOfStudy)) {
    errors.push('Field of study is required');
  } else if (!hasMinLength(data.fieldOfStudy, 2)) {
    errors.push('Field of study must be at least 2 characters');
  }

  // Date validation
  if (!isValidDate(data.startDate)) {
    errors.push('Start date is invalid');
  } else if (isFutureDate(data.startDate)) {
    errors.push('Start date cannot be in the future');
  }

  if (data.expectedEndDate) {
    if (!isValidDate(data.expectedEndDate)) {
      errors.push('Expected end date is invalid');
    } else if (!isDateAfter(data.expectedEndDate, data.startDate)) {
      errors.push('Expected end date must be after start date');
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// Timeline validation
export const validateTimelineCommit = (data: {
  title: string;
  hasMilestones: boolean;
  hasStages: boolean;
}): BaselineValidationResult => {
  const errors: string[] = [];

  if (!isNonEmptyString(data.title)) {
    errors.push('Timeline title is required');
  } else if (!hasMinLength(data.title, 3)) {
    errors.push('Timeline title must be at least 3 characters');
  }

  if (!data.hasStages) {
    errors.push('Timeline must have at least one stage');
  }

  if (!data.hasMilestones) {
    errors.push('Timeline must have at least one milestone');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// Progress tracking validation
export const validateMilestoneCompletion = (data: {
  completionDate: string;
  targetDate?: string;
}): BaselineValidationResult => {
  const errors: string[] = [];

  if (!isValidDate(data.completionDate)) {
    errors.push('Completion date is invalid');
  } else if (isFutureDate(data.completionDate)) {
    errors.push('Completion date cannot be in the future');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// Assessment validation
export const validateAssessmentResponse = (value: number): boolean => {
  return isInRange(value, 1, 5);
};

export const validateAssessmentCompletion = (
  responses: Map<string, number>,
  requiredQuestions: string[]
): BaselineValidationResult => {
  const errors: string[] = [];

  // Check all questions answered
  const unanswered = requiredQuestions.filter(q => !responses.has(q));
  if (unanswered.length > 0) {
    errors.push(`${unanswered.length} question(s) not answered`);
  }

  // Check all values in valid range
  for (const [questionId, value] of responses.entries()) {
    if (!validateAssessmentResponse(value)) {
      errors.push(`Invalid response value for question ${questionId}: ${value}`);
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// Document upload validation
export const validateDocumentUpload = (
  file: File | null,
  title: string
): BaselineValidationResult => {
  const errors: string[] = [];

  if (!file) {
    errors.push('Please select a file to upload');
  } else {
    if (!isValidFileType(file, ALLOWED_DOCUMENT_TYPES)) {
      errors.push('File must be PDF or DOCX format');
    }
    if (!isValidFileSize(file, MAX_FILE_SIZE)) {
      errors.push(`File size must be less than ${MAX_FILE_SIZE / 1024 / 1024}MB`);
    }
  }

  if (!isNonEmptyString(title)) {
    errors.push('Document title is required');
  } else if (!hasMinLength(title, 3)) {
    errors.push('Document title must be at least 3 characters');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// Email validation (for future use)
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// UUID validation
export const isValidUUID = (uuid: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};
