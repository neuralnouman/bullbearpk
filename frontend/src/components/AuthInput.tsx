import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';

interface AuthInputProps {
  id: string;
  type: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
  icon?: React.ReactNode;
  rightElement?: React.ReactNode;
  disabled?: boolean;
  autoComplete?: string;
}


interface EnhancedAuthInputProps extends AuthInputProps {
  helperText?: string;
}

const AuthInput: React.FC<EnhancedAuthInputProps> = ({
  id,
  type,
  label,
  value,
  onChange,
  placeholder,
  error,
  icon,
  rightElement,
  disabled,
  autoComplete,
  helperText
}) => (
  <div>
    <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      {label}
    </label>
    <div className="relative group">
      {icon && <span className="absolute left-3 top-1/2 transform -translate-y-1/2">{icon}</span>}
      <motion.input
        id={id}
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        className={`w-full ${icon ? 'pl-10' : 'pl-4'} ${rightElement ? 'pr-12' : 'pr-4'} py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white ${
          error ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
        } transition-all duration-200 focus:shadow-lg focus:shadow-blue-100 dark:focus:shadow-blue-900`}
        placeholder={placeholder}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : helperText ? `${id}-helper` : undefined}
        disabled={disabled}
        autoComplete={autoComplete}
        whileFocus={{ scale: 1.01 }}
      />
      {rightElement && (
        <span className="absolute right-3 top-1/2 transform -translate-y-1/2">{rightElement}</span>
      )}
      {helperText && !error && (
        <div id={`${id}-helper`} className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {helperText}
        </div>
      )}
      {error && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center space-x-1 mt-1 text-red-600 dark:text-red-400 text-sm"
          id={`${id}-error`}
          aria-live="polite"
        >
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </motion.div>
      )}
    </div>
  </div>
);

export default AuthInput;
