export type LoginParams = { email: string; password: string };
export type SignupParams = {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  organization: string;
  role: string;
};

export type AuthResult = { success: true } | { success: false; message: string };

const DEMO_USERS: { email: string; password: string }[] = [
  { email: "demo@aflanalytics.com", password: "demo123" },
  { email: "admin@aflanalytics.com", password: "admin123" },
  { email: "coach@aflanalytics.com", password: "coach123" },
  { email: "analyst@aflanalytics.com", password: "analyst123" },
];

const STORAGE_KEY = "registeredUsers";
export const RESET_DEMO_CODE = "123456";

function readUsers(): any[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function writeUsers(users: any[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
}

export async function loginWithEmail(params: LoginParams): Promise<AuthResult> {
  await delay(1500);
  const { email, password } = params;
  if (!email || !password) return { success: false, message: "Please enter both email and password" };

  const users = [...DEMO_USERS, ...readUsers()];
  const match = users.some(
    (u) => u.email.toLowerCase() === email.toLowerCase() && u.password === password,
  );

  if (!match) {
    return {
      success: false,
      message:
        "Invalid email or password. Try demo@aflanalytics.com / demo123 or use your signup credentials",
    };
  }

  return { success: true };
}

export async function signupWithEmail(params: SignupParams): Promise<AuthResult> {
  await delay(2000);
  const { firstName, lastName, email, password, organization, role } = params;

  if (!firstName || !lastName || !email || !password || !organization) {
    return { success: false, message: "Please fill all required fields" };
  }

  const existing = readUsers();
  const exists = existing.some((u) => u.email.toLowerCase() === email.toLowerCase());
  if (exists) {
    return { success: false, message: "An account with this email already exists. Please login instead." };
  }

  existing.push({ email, password, firstName, lastName, organization, role });
  writeUsers(existing);
  return { success: true };
}

export async function sendResetEmail(email: string): Promise<AuthResult> {
  await delay(1500);
  if (!email) return { success: false, message: "Please enter a valid email address" };
  return { success: true };
}

export async function verifyResetCode(code: string): Promise<AuthResult> {
  await delay(1000);
  return code === RESET_DEMO_CODE
    ? { success: true }
    : { success: false, message: "Invalid verification code. Try '123456' for demo." };
}

export async function resetPassword(newPassword: string, confirm: string): Promise<AuthResult> {
  await delay(1500);
  if (newPassword !== confirm) return { success: false, message: "Passwords do not match" };
  return { success: true };
}

function delay(ms: number) {
  return new Promise((res) => setTimeout(res, ms));
}
