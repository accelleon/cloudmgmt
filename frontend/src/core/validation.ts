export const password_rules = [
  (val: string) =>
    (val && val.length >= 8) || 'Password must be at least 8 characters',
  // Must contain one lowercase, one uppercase, one digit, and one special character
  (val: string) =>
    (val && /[a-z]/.test(val)) || 'Password must contain a lowercase letter',
  (val: string) =>
    (val && /[A-Z]/.test(val)) || 'Password must contain an uppercase letter',
  (val: string) =>
    (val && /[0-9]/.test(val)) || 'Password must contain a number',
  (val: string) =>
    (val && /[@$!%*?&]/.test(val)) ||
    'Password must contain a special character (@$!%*?&)',
];

export const name_rules = [
  // Must be between 3 and 20 characters
  (val: string) =>
    (val && val.length >= 3 && val.length <= 20) ||
    'Name must be between 3 and 20 characters',
  // Only a-z, 0-9, and _.- allowed
  (val: string) =>
    (val && /^[a-z0-9_.-]+$/.test(val)) ||
    'Name must only contain a-z, 0-9, _, ., or -',
];
