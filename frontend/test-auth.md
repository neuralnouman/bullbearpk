# Authentication Pages Test Plan

## Overview
This document outlines the testing procedures for the BullBearPK login and registration pages.

## Backend Status ✅
- **Registration Endpoint**: `POST /api/auth/register` - Working
- **Login Endpoint**: `POST /api/auth/login` - Working
- **Server**: Running on `http://localhost:5000`

## Frontend Test Instructions

### 1. Access the Application
1. Open your browser and navigate to `http://localhost:5173` (or the port shown in your terminal)
2. You should see the landing page with navigation options

### 2. Test Registration Page

#### Navigate to Registration
1. Click on "Sign Up" or "Create Account" link
2. Or navigate directly to `http://localhost:5173/register`

#### Test Registration Form Fields

**✅ Required Fields Validation:**
- **Name**: Try submitting without name → Should show "Name is required"
- **Email**: Try invalid email → Should show "Please enter a valid email address"
- **Password**: Try short password → Should show "Password must be at least 6 characters"
- **Confirm Password**: Try mismatched passwords → Should show "Passwords do not match"
- **Investment Goal**: Try submitting without goal → Should show "Investment goal is required"

**✅ Password Strength Indicator:**
- Enter weak password (e.g., "123") → Should show red "Weak" indicator
- Enter medium password (e.g., "password123") → Should show yellow "Medium" indicator
- Enter strong password (e.g., "Password123!") → Should show green "Strong" indicator

**✅ Password Visibility Toggle:**
- Click eye icon next to password fields → Should toggle password visibility
- Both password and confirm password should have separate toggles

**✅ Risk Tolerance Dropdown:**
- Select different options (Low, Moderate, High) → Should work correctly

**✅ Preferred Sectors (Optional):**
- Try selecting multiple sectors → Should allow multiple selections
- Try deselecting → Should work correctly

#### Test Successful Registration
1. Fill in all required fields with valid data:
   - **Name**: "Test User"
   - **Email**: "test@example.com"
   - **Password**: "Password123!"
   - **Confirm Password**: "Password123!"
   - **Risk Tolerance**: "Moderate"
   - **Investment Goal**: "Wealth Growth"
   - **Preferred Sectors**: Select "Technology"

2. Click "Create Account" button
3. Should see loading spinner with "Creating account..."
4. Should redirect to dashboard on success
5. Should show success toast: "Account created successfully! Welcome to BullBearPK!"

### 3. Test Login Page

#### Navigate to Login
1. Click on "Sign In" or "Login" link
2. Or navigate directly to `http://localhost:5173/login`

#### Test Login Form Fields

**✅ Required Fields Validation:**
- **Email**: Try submitting without email → Should show "Email is required"
- **Email**: Try invalid email → Should show "Please enter a valid email address"
- **Password**: Try submitting without password → Should show "Password is required"
- **Password**: Try short password → Should show "Password must be at least 6 characters"

**✅ Password Visibility Toggle:**
- Click eye icon next to password field → Should toggle password visibility

#### Test Successful Login
1. Use the credentials from registration:
   - **Email**: "test@example.com"
   - **Password**: "Password123!"

2. Click "Sign In" button
3. Should see loading spinner with "Signing in..."
4. Should redirect to dashboard on success
5. Should show success toast: "Welcome back!"

#### Test Failed Login
1. Try incorrect password:
   - **Email**: "test@example.com"
   - **Password**: "wrongpassword"
2. Should show error toast with appropriate message

### 4. Test Navigation Between Pages

**✅ Login to Register:**
1. On login page, click "Sign up here" link
2. Should navigate to registration page

**✅ Register to Login:**
1. On registration page, click "Sign in here" link
2. Should navigate to login page

### 5. Test Form Behavior

**✅ Loading States:**
- During form submission, buttons should show loading spinner
- Form fields should be disabled during submission
- Should prevent multiple submissions

**✅ Error Handling:**
- Invalid credentials should show appropriate error messages
- Network errors should show user-friendly messages
- Form should remain functional after errors

**✅ Accessibility:**
- All form fields should have proper labels
- Error messages should be announced to screen readers
- Keyboard navigation should work properly
- Focus management should be logical

### 6. Test Responsive Design

**✅ Mobile View:**
- Forms should be properly sized on mobile devices
- Touch targets should be appropriately sized
- Text should be readable on small screens

**✅ Desktop View:**
- Forms should be centered and properly sized
- Animations should be smooth
- Hover effects should work correctly

### 7. Test Dark Mode

**✅ Dark Mode Toggle:**
- If dark mode is available, test both light and dark themes
- All text should be readable in both modes
- Form elements should have proper contrast

## Expected Test Results

### ✅ Successful Registration Flow
1. User fills out registration form
2. Form validates all fields
3. Backend creates user account
4. User is redirected to dashboard
5. User data is stored in auth store

### ✅ Successful Login Flow
1. User enters valid credentials
2. Backend authenticates user
3. User is redirected to dashboard
4. User session is established

### ✅ Error Handling
1. Invalid form data shows appropriate errors
2. Network errors show user-friendly messages
3. Form remains functional after errors

### ✅ Security Features
1. Passwords are not visible by default
2. Password strength is validated
3. Form data is properly sanitized

## Test Data

### Valid Registration Data
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "Password123!",
  "confirmPassword": "Password123!",
  "riskTolerance": "moderate",
  "investmentGoal": "Wealth Growth",
  "preferredSectors": ["technology", "finance"]
}
```

### Valid Login Data
```json
{
  "email": "test@example.com",
  "password": "Password123!"
}
```

## Common Issues to Check

1. **CORS Issues**: If you see CORS errors, check that the backend is running and configured correctly
2. **Network Errors**: If API calls fail, check that the backend server is running on port 5000
3. **Form Validation**: If validation doesn't work, check that the AuthInput component is properly configured
4. **State Management**: If login state doesn't persist, check that the auth store is properly configured

## Next Steps After Testing

1. **Fix any issues** found during testing
2. **Test edge cases** like very long inputs, special characters, etc.
3. **Test with different browsers** (Chrome, Firefox, Safari, Edge)
4. **Test with different devices** (desktop, tablet, mobile)
5. **Test accessibility** with screen readers and keyboard navigation 