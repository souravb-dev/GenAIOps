module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended'
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true
    }
  },
  plugins: ['react-refresh'],
  settings: {
    react: {
      version: 'detect'
    }
  },
  rules: {
    'react-refresh/only-export-components': 'off', // Disable Fast Refresh warnings
    // Disable some rules that might cause issues without full TypeScript ESLint
    'no-unused-vars': 'off',
    'no-undef': 'off',
    'no-useless-catch': 'warn' // Make useless catch a warning instead of error
  },
} 