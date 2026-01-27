/**
 * Confirmation Dialog Component
 * 
 * Modal dialog for confirming destructive or important actions.
 */

import React from 'react';

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmVariant?: 'danger' | 'warning' | 'primary';
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'primary',
  onConfirm,
  onCancel,
  loading = false,
}) => {
  if (!isOpen) return null;

  const getConfirmButtonClass = () => {
    const baseClass = 'px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    switch (confirmVariant) {
      case 'danger':
        return `${baseClass} bg-red-600 text-white hover:bg-red-700 focus:ring-red-500`;
      case 'warning':
        return `${baseClass} bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500`;
      default:
        return `${baseClass} bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500`;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full" onClick={(e) => e.stopPropagation()}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
        </div>
        
        <div className="px-6 py-4">
          <p className="text-gray-700">{message}</p>
        </div>
        
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-end space-x-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {cancelText}
          </button>
          
          <button
            onClick={onConfirm}
            disabled={loading}
            className={getConfirmButtonClass()}
          >
            {loading ? 'Processing...' : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
