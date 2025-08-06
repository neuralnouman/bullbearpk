import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  User,
  CheckCircle,
  Loader2,
  ArrowRight,
  Shield,
  Zap,
  TrendingUp
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import AuthInput from '../components/AuthInput';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuthStore();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    riskTolerance: 'moderate',
    investmentGoal: '',
    preferredSectors: [] as string[],
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase, and number';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.investmentGoal.trim()) {
      newErrors.investmentGoal = 'Investment goal is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        riskTolerance: formData.riskTolerance as 'low' | 'moderate' | 'high',
        investmentGoal: formData.investmentGoal,
        preferredSectors: formData.preferredSectors,
      });
      toast.success('Account created successfully! Welcome to BullBearPK!');
      navigate('/dashboard');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed. Please try again.';
      toast.error(errorMessage);
    }
  };

  const handleInputChange = (field: string, value: string | string[]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const getPasswordStrength = () => {
    if (!formData.password) return { strength: 0, color: 'gray', text: '' };
    
    let score = 0;
    if (formData.password.length >= 6) score++;
    if (formData.password.length >= 8) score++;
    if (/(?=.*[a-z])/.test(formData.password)) score++;
    if (/(?=.*[A-Z])/.test(formData.password)) score++;
    if (/(?=.*\d)/.test(formData.password)) score++;
    if (/(?=.*[!@#$%^&*])/.test(formData.password)) score++;

    return {
      strength: score,
      color: score <= 2 ? 'red' : score <= 4 ? 'yellow' : 'green',
      text: score <= 2 ? 'Weak' : score <= 4 ? 'Medium' : 'Strong'
    };
  };

  const passwordStrength = getPasswordStrength();

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            className="w-16 h-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <TrendingUp className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Join BullBearPK
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Start your investment journey with AI-powered insights
          </p>
        </motion.div>

        {/* Registration Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* Name Field */}
            <AuthInput
              id="name"
              type="text"
              label="Full Name"
              value={formData.name}
              onChange={val => handleInputChange('name', val)}
              placeholder="Enter your full name"
              error={errors.name}
              icon={<User className="w-5 h-5 text-gray-400" />}
              disabled={isLoading}
              autoComplete="name"
            />

            {/* Email Field */}
            <AuthInput
              id="email"
              type="email"
              label="Email Address"
              value={formData.email}
              onChange={val => handleInputChange('email', val)}
              placeholder="Enter your email"
              error={errors.email}
              icon={<Mail className="w-5 h-5 text-gray-400" />}
              disabled={isLoading}
              autoComplete="email"
            />

            {/* Password Field */}
            <AuthInput
              id="password"
              type={showPassword ? 'text' : 'password'}
              label="Password"
              value={formData.password}
              onChange={val => handleInputChange('password', val)}
              placeholder="Create a strong password"
              error={errors.password}
              icon={<Lock className="w-5 h-5 text-gray-400" />}
              rightElement={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none"
                  disabled={isLoading}
                  tabIndex={-1}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              }
              disabled={isLoading}
              autoComplete="new-password"
            />
            {/* Password Strength Meter */}
            {formData.password && (
              <div className="mt-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500 dark:text-gray-400">Password strength:</span>
                  <span className={`font-medium ${
                    passwordStrength.color === 'red' ? 'text-red-600' :
                    passwordStrength.color === 'yellow' ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {passwordStrength.text}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1 mt-1">
                  <div 
                    className={`h-1 rounded-full transition-all duration-300 ${
                      passwordStrength.color === 'red' ? 'bg-red-500' :
                      passwordStrength.color === 'yellow' ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${(passwordStrength.strength / 6) * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* Confirm Password Field */}
            <AuthInput
              id="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              label="Confirm Password"
              value={formData.confirmPassword}
              onChange={val => handleInputChange('confirmPassword', val)}
              placeholder="Confirm your password"
              error={errors.confirmPassword}
              icon={<Lock className="w-5 h-5 text-gray-400" />}
              rightElement={
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none"
                  disabled={isLoading}
                  tabIndex={-1}
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              }
              disabled={isLoading}
              autoComplete="new-password"
            />
            {/* Passwords Match Indicator */}
            {formData.confirmPassword && formData.password === formData.confirmPassword && !errors.confirmPassword && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center space-x-1 mt-1 text-green-600 dark:text-green-400 text-sm"
              >
                <CheckCircle className="w-4 h-4" />
                <span>Passwords match</span>
              </motion.div>
            )}

            {/* Risk Tolerance */}
            <div>
              <label htmlFor="riskTolerance" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Risk Tolerance
              </label>
              <select
                id="riskTolerance"
                value={formData.riskTolerance}
                onChange={e => handleInputChange('riskTolerance', e.target.value)}
                className="w-full py-3 px-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white border-gray-300 dark:border-gray-600"
                disabled={isLoading}
              >
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
              </select>
            </div>

            {/* Investment Goal */}
            <AuthInput
              id="investmentGoal"
              type="text"
              label="Investment Goal"
              value={formData.investmentGoal}
              onChange={val => handleInputChange('investmentGoal', val)}
              placeholder="E.g. Retirement, Wealth Growth, Education, etc."
              error={errors.investmentGoal}
              icon={<TrendingUp className="w-5 h-5 text-gray-400" />}
              disabled={isLoading}
            />

            {/* Preferred Sectors */}
            <div>
              <label htmlFor="preferredSectors" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Preferred Sectors (optional)
              </label>
              <select
                id="preferredSectors"
                multiple
                value={formData.preferredSectors}
                onChange={e => {
                  const options = Array.from(e.target.selectedOptions, option => option.value);
                  handleInputChange('preferredSectors', options);
                }}
                className="w-full py-3 px-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white border-gray-300 dark:border-gray-600"
                disabled={isLoading}
              >
                <option value="technology">Technology</option>
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="energy">Energy</option>
                <option value="consumer">Consumer</option>
                <option value="industrial">Industrial</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:from-green-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Creating account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center">
            <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
            <span className="px-4 text-sm text-gray-500 dark:text-gray-400">or</span>
            <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
          </div>

          {/* Login Link */}
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium transition-colors"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <Zap className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">AI-Powered</h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">Smart analysis</p>
          </div>
          <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <Shield className="w-6 h-6 text-green-600 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">Secure</h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">Bank-level security</p>
          </div>
          <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <TrendingUp className="w-6 h-6 text-blue-600 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">Growth</h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">Maximize returns</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default RegisterPage; 