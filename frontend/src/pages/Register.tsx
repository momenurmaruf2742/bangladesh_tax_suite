import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, Link } from "react-router-dom";
import { zodResolver } from "@hookform/resolvers/zod";
import * as zod from "zod";
import { api } from "../services/api";
import { User, Mail, Phone, FileText, Lock, AlertCircle, CheckCircle, Loader2, Building2, Briefcase, UserCheck } from "lucide-react";

// Form validation schema
const registerSchema = zod
  .object({
    role: zod.string().min(1, "Please select an account type"),
    company_name: zod.string().optional(),
    first_name: zod.string().min(1, "First name is required"),
    last_name: zod.string().min(1, "Last name is required"),
    email: zod.string().email("Invalid email address"),
    phone: zod
      .string()
      .min(11, "Phone number must be at least 11 digits")
      .regex(/^(\+88)?01[3-9]\d{8}$/, "Invalid Bangladeshi phone number format (e.g. 01712345678)"),
    tin: zod
      .string()
      .optional()
      .refine(
        (val) => !val || /^\d{12}$/.test(val),
        "TIN must be exactly 12 digits"
      ),
    password: zod.string().min(6, "Password must be at least 6 characters"),
    confirm_password: zod.string().min(6, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type RegisterFormFields = zod.infer<typeof registerSchema>;

export const Register: React.FC = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState<"Employee" | "Admin" | "CA">("Employee");

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<RegisterFormFields>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: "Employee",
    }
  });

  const onSubmit = async (data: RegisterFormFields) => {
    setLoading(true);
    setError(null);
    try {
      const { confirm_password, ...payload } = data;
      await api.post("/auth/register", payload);
      setSuccess(true);
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Registration failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRoleSelect = (role: "Employee" | "Admin" | "CA") => {
    setSelectedRole(role);
    setValue("role", role);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#090f1c] px-4 py-12 relative overflow-hidden">
      {/* Decorative background glows */}
      <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-950/20 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-900/10 blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-xl glass-panel p-8 rounded-2xl shadow-2xl relative z-10">
        {/* Header/Logo */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center p-3 bg-emerald-500/10 rounded-xl mb-3 border border-emerald-500/20">
            <span className="text-2xl font-bold text-emerald-400">৳</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white m-0">
            Create Tax Account
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            Choose your account type to join Bangladesh Tax Suite
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-200 text-sm flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-200 text-sm flex items-start gap-3">
            <CheckCircle className="w-5 h-5 shrink-0 mt-0.5 animate-bounce" />
            <span>Registration successful! Redirecting to login...</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Account Type Role Selection Cards */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Select Account Type
            </label>
            <input type="hidden" {...register("role")} value={selectedRole} />
            <div className="grid grid-cols-3 gap-2.5">
              <button
                type="button"
                onClick={() => handleRoleSelect("Employee")}
                className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col items-center text-center ${
                  selectedRole === "Employee"
                    ? "bg-emerald-950/40 border-emerald-500 text-emerald-300 ring-1 ring-emerald-500"
                    : "bg-gray-900/40 border-gray-800 text-gray-400 hover:border-gray-700"
                }`}
              >
                <UserCheck className="w-5 h-5 mb-1 text-emerald-400" />
                <span className="text-xs font-bold text-white block">Individual</span>
                <span className="text-[10px] text-gray-500 block leading-tight">Taxpayer / Employee</span>
              </button>

              <button
                type="button"
                onClick={() => handleRoleSelect("Admin")}
                className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col items-center text-center ${
                  selectedRole === "Admin"
                    ? "bg-emerald-950/40 border-emerald-500 text-emerald-300 ring-1 ring-emerald-500"
                    : "bg-gray-900/40 border-gray-800 text-gray-400 hover:border-gray-700"
                }`}
              >
                <Building2 className="w-5 h-5 mb-1 text-amber-400" />
                <span className="text-xs font-bold text-white block">Company</span>
                <span className="text-[10px] text-gray-500 block leading-tight">HR & Payroll Admin</span>
              </button>

              <button
                type="button"
                onClick={() => handleRoleSelect("CA")}
                className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col items-center text-center ${
                  selectedRole === "CA"
                    ? "bg-emerald-950/40 border-emerald-500 text-emerald-300 ring-1 ring-emerald-500"
                    : "bg-gray-900/40 border-gray-800 text-gray-400 hover:border-gray-700"
                }`}
              >
                <Briefcase className="w-5 h-5 mb-1 text-blue-400" />
                <span className="text-xs font-bold text-white block">CA Firm</span>
                <span className="text-[10px] text-gray-500 block leading-tight">Tax Practitioner</span>
              </button>
            </div>
          </div>

          {/* Conditional Company Name for Employer Admin */}
          {selectedRole === "Admin" && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="company_name">
                Company Name / Business Title
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                  <Building2 className="w-4 h-4" />
                </span>
                <input
                  id="company_name"
                  type="text"
                  {...register("company_name")}
                  placeholder="Acme Technologies BD Ltd."
                  className="w-full pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
                />
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* First Name */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="first_name">
                First Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                  <User className="w-4 h-4" />
                </span>
                <input
                  id="first_name"
                  type="text"
                  {...register("first_name")}
                  placeholder="Momenur"
                  className="w-full pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
                />
              </div>
              {errors.first_name && (
                <p className="text-red-400 text-xs mt-1">{errors.first_name.message}</p>
              )}
            </div>

            {/* Last Name */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="last_name">
                Last Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                  <User className="w-4 h-4" />
                </span>
                <input
                  id="last_name"
                  type="text"
                  {...register("last_name")}
                  placeholder="Islam"
                  className="w-full pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
                />
              </div>
              {errors.last_name && (
                <p className="text-red-400 text-xs mt-1">{errors.last_name.message}</p>
              )}
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="email">
              Email Address
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                <Mail className="w-4 h-4" />
              </span>
              <input
                id="email"
                type="email"
                {...register("email")}
                placeholder="momenur@example.com"
                className="w-full pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
              />
            </div>
            {errors.email && (
              <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>
            )}
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="phone">
              Phone Number (e.g. 01712345678)
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                <Phone className="w-4 h-4" />
              </span>
              <input
                id="phone"
                type="text"
                {...register("phone")}
                placeholder="01712345678"
                className="w-full pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
              />
            </div>
            {errors.phone && (
              <p className="text-red-400 text-xs mt-1">{errors.phone.message}</p>
            )}
          </div>

          {/* TIN */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="tin">
              TIN (12-Digit tax ID - Optional)
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                <FileText className="w-4 h-4" />
              </span>
              <input
                id="tin"
                type="text"
                {...register("tin")}
                placeholder="123456789012"
                className="w-full pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
              />
            </div>
            {errors.tin && (
              <p className="text-red-400 text-xs mt-1">{errors.tin.message}</p>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="password">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  id="password"
                  type="password"
                  {...register("password")}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
                />
              </div>
              {errors.password && (
                <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="confirm_password">
                Confirm Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  id="confirm_password"
                  type="password"
                  {...register("confirm_password")}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
                />
              </div>
              {errors.confirm_password && (
                <p className="text-red-400 text-xs mt-1">{errors.confirm_password.message}</p>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 disabled:cursor-not-allowed text-white font-semibold rounded-lg shadow-lg hover:shadow-emerald-900/20 active:translate-y-[1px] transition-all flex items-center justify-center gap-2 mt-4 cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Creating account...
              </>
            ) : (
              "Sign Up"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-gray-400">
          Already have an account?{" "}
          <Link to="/login" className="text-emerald-400 hover:text-emerald-300 font-semibold transition-colors">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
