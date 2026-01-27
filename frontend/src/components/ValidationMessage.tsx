/**
 * Validation Message Component
 * 
 * Displays validation errors and warnings.
 */

import React from 'react';

interface ValidationMessageProps {
  errors?: string[];
  warnings?: string[];
  className?: string;
}

export const ValidationMessage: React.FC<ValidationMessageProps> = ({
  errors = [],
  warnings = [],
  className = '',
}) => {
  if (errors.length === 0 && warnings.length === 0) {
    return null;
  }

  return (
    <div className={className}>
      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">
                {errors.length === 1 ? 'Error' : `${errors.length} Errors`}
              </h3>
              {errors.length === 1 ? (
                <p className="mt-1 text-sm text-red-700">{errors[0]}</p>
              ) : (
                <ul className="mt-2 text-sm text-red-700 list-disc list-inside space-y-1">
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-4 ${errors.length > 0 ? 'mt-4' : ''}`}>
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-yellow-800">
                {warnings.length === 1 ? 'Warning' : `${warnings.length} Warnings`}
              </h3>
              {warnings.length === 1 ? (
                <p className="mt-1 text-sm text-yellow-700">{warnings[0]}</p>
              ) : (
                <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside space-y-1">
                  {warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidationMessage;
