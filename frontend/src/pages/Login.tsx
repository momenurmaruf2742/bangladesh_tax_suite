import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, Link } from "react-router-dom";
import { zodResolver } from "@hookform/resolvers/zod";
import * as zod from "zod";
import { api, tokenStorage } from "../services/api";
import { Lock, Mail, AlertCircle, Loader2 } from "lucide-react";

// Form validation schema
const loginSchema = zod.object({
  username: zod.string().min(1, "Email or phone number is required"),
  password: zod.string().min(6, "Password must be at least 6 characters"),
});

type LoginFormFields = zod.infer<typeof loginSchema>;

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormFields>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormFields) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post("/auth/login", data);
      const { access_token, refresh_token } = response.data;
      tokenStorage.setTokens(access_token, refresh_token);
      navigate("/");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Authentication failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#090f1c] px-4 relative overflow-hidden">
      {/* Decorative background glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-950/20 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-900/10 blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-md glass-panel p-8 rounded-2xl shadow-2xl relative z-10">
        {/* Header/Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-emerald-500/10 rounded-xl mb-4 border border-emerald-500/20">
            <span className="text-2xl font-bold text-emerald-400">৳</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white m-0">
            Bangladesh Tax Suite
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            Enterprise Tax Management & Calculation
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-200 text-sm flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Username Input */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5" htmlFor="username">
              Email or Phone Number
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                <Mail className="w-5 h-5" />
              </span>
              <input
                id="username"
                type="text"
                autoComplete="username"
                {...register("username")}
                placeholder="email@example.com or +88017..."
                className="w-full pl-10 pr-4 py-2.5 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
              />
            </div>
            {errors.username && (
              <p className="text-red-400 text-xs mt-1">{errors.username.message}</p>
            )}
          </div>

          {/* Password Input */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-sm font-medium text-gray-300" htmlFor="password">
                Password
              </label>
              <a href="#" className="text-xs text-emerald-400 hover:text-emerald-300 transition-colors">
                Forgot password?
              </a>
            </div>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 pointer-events-none">
                <Lock className="w-5 h-5" />
              </span>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                {...register("password")}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
              />
            </div>
            {errors.password && (
              <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>
            )}
          </div>

          {/* Login Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 disabled:cursor-not-allowed text-white font-semibold rounded-lg shadow-lg hover:shadow-emerald-900/20 active:translate-y-[1px] transition-all flex items-center justify-center gap-2 mt-2 cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-400">
          Don't have an account?{" "}
          <Link to="/register" className="text-emerald-400 hover:text-emerald-300 font-semibold transition-colors">
            Sign up now
          </Link>
        </div>
      </div>
    </div>
  );
};
