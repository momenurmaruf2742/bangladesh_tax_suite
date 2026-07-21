import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api, tokenStorage } from "../services/api";
import { Loader } from "../components/Loader";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  TrendingUp,
  FileSpreadsheet,
  Settings,
  LogOut,
  User as UserIcon,
  Shield,
  FileCheck,
  Scale,
  Activity,
  Calculator,
  Bell,
  Mail,
  Phone
} from "lucide-react";

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Fetch current user details via React Query
  const { data: user, isLoading, isError } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const res = await api.get("/auth/profile");
      return res.data;
    },
    retry: 1,
  });

  const handleLogout = async () => {
    try {
      const refreshToken = tokenStorage.getRefreshToken();
      if (refreshToken) {
        await api.post(
          "/auth/logout",
          { refresh_token: refreshToken },
          {
            headers: {
              Authorization: `Bearer ${tokenStorage.getAccessToken()}`,
            },
          }
        );
      }
    } catch (e) {
      console.error("Error during logout call", e);
    } finally {
      tokenStorage.clearTokens();
      navigate("/login");
    }
  };

  if (isLoading) {
    return <Loader fullPage />;
  }

  if (isError || !user) {
    tokenStorage.clearTokens();
    navigate("/login");
    return null;
  }

  const userFullName = `${user.first_name} ${user.last_name}`;

  return (
    <div className="min-h-screen bg-[#090f1c] text-gray-200 flex flex-col md:flex-row">
      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 bg-gray-900/60 border-r border-gray-800/80 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo Brand */}
          <div className="p-6 border-b border-gray-800/60 flex items-center gap-3">
            <span className="text-2xl font-bold text-emerald-400 bg-emerald-500/10 w-10 h-10 flex items-center justify-center rounded-lg border border-emerald-500/20">
              ৳
            </span>
            <div>
              <h2 className="text-base font-bold text-white leading-tight m-0">Tax Suite</h2>
              <span className="text-xs text-gray-500 font-medium">Bangladesh</span>
            </div>
          </div>

          {/* Nav Items */}
          <nav className="p-4 space-y-1">
            <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 font-medium text-sm transition-all">
              <LayoutDashboard className="w-4 h-4" />
              Dashboard Overview
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 text-sm transition-all">
              <Users className="w-4 h-4" />
              Employee Info
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 text-sm transition-all">
              <Briefcase className="w-4 h-4" />
              Salary & Allowances
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 text-sm transition-all">
              <TrendingUp className="w-4 h-4" />
              Investments & Rebates
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 text-sm transition-all">
              <FileSpreadsheet className="w-4 h-4" />
              AIT Records
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 text-sm transition-all">
              <Calculator className="w-4 h-4" />
              Tax Calculator
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 text-sm transition-all">
              <Settings className="w-4 h-4" />
              Settings
            </a>
          </nav>
        </div>

        {/* User Card & Logout */}
        <div className="p-4 border-t border-gray-800/60 space-y-3">
          <div className="flex items-center gap-3 px-2">
            <div className="w-9 h-9 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold">
              {user.first_name[0]}{user.last_name[0]}
            </div>
            <div className="truncate">
              <p className="text-sm font-semibold text-white truncate m-0 leading-snug">
                {userFullName}
              </p>
              <p className="text-xs text-gray-500 truncate m-0">
                {user.role}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-red-400 hover:bg-red-950/20 hover:text-red-300 text-sm font-medium transition-all cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            Logout Session
          </button>
        </div>
      </aside>

      {/* Main Panel Content */}
      <main className="flex-1 p-6 md:p-10 flex flex-col gap-6 overflow-y-auto">
        {/* Top bar header */}
        <div className="flex justify-between items-center pb-4 border-b border-gray-800/60">
          <div>
            <h1 className="text-2xl font-bold text-white m-0 tracking-tight">
              Welcome back, {user.first_name}!
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Here is your tax overview for assessment year 2025-2026.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-gray-400 hover:text-white bg-gray-900/50 border border-gray-800 rounded-lg relative cursor-pointer">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full"></span>
            </button>
            <div className="bg-emerald-950/30 border border-emerald-900/40 text-emerald-400 text-xs px-3 py-1.5 rounded-full font-semibold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              FY 2025-26 Active
            </div>
          </div>
        </div>

        {/* Stats Grid Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="glass-panel p-6 rounded-xl relative overflow-hidden">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-gray-400 text-xs uppercase tracking-wider font-semibold">TIN Certificate</span>
                <h3 className="text-xl font-bold text-white mt-1">
                  {user.tin || "Not Registered"}
                </h3>
              </div>
              <span className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/10">
                <FileCheck className="w-5 h-5" />
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-4">
              {user.tin ? "Validated TIN with NBR system." : "Go to Settings to register your 12-digit TIN."}
            </p>
          </div>

          {/* Card 2 */}
          <div className="glass-panel p-6 rounded-xl relative overflow-hidden">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-gray-400 text-xs uppercase tracking-wider font-semibold">User Role</span>
                <h3 className="text-xl font-bold text-white mt-1">
                  {user.role} Account
                </h3>
              </div>
              <span className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/10">
                <Shield className="w-5 h-5" />
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-4">
              Permissions: full user and calculation profile editing.
            </p>
          </div>

          {/* Card 3 */}
          <div className="glass-panel p-6 rounded-xl relative overflow-hidden">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Verification</span>
                <h3 className="text-xl font-bold text-white mt-1">
                  {user.is_verified ? "Verified User" : "Pending Verify"}
                </h3>
              </div>
              <span className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/10">
                <Activity className="w-5 h-5" />
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-4">
              {user.is_verified ? "Fully authorized for automated NBR submission." : "Verification required to unlock final reporting export."}
            </p>
          </div>
        </div>

        {/* Dashboard Content Split */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-2">
          {/* Main Info Area */}
          <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col gap-4">
            <h2 className="text-lg font-bold text-white m-0">Tax Modules Overview</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-2">
              <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all">
                <h4 className="font-semibold text-white text-sm">Employee & Salary</h4>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  Record your employment agreements, scale basic pay, allowances, house rent exemptions, bonuses, and special festival perks.
                </p>
              </div>
              <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all">
                <h4 className="font-semibold text-white text-sm">Investments & Rebates</h4>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  Track DPS accounts, Provident Funds, Life Insurance, Sanchayapatra policies, and calculate optimal tax rebate values.
                </p>
              </div>
              <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all">
                <h4 className="font-semibold text-white text-sm">Tax Engine Rules</h4>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  NBR regulations for FY 2025-2026. Automated slabs, taxable boundaries, minimum tax brackets, and AIT source adjustments.
                </p>
              </div>
              <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all">
                <h4 className="font-semibold text-white text-sm">Automated Reports</h4>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  Export complete NBR-compatible computation summaries, income certificates, and PDFs for compliance auditing.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Profile Summary Panel */}
          <div className="glass-panel p-6 rounded-xl flex flex-col justify-between">
            <div>
              <h2 className="text-lg font-bold text-white m-0">Profile Summary</h2>
              <div className="space-y-4 mt-6">
                <div className="flex items-center gap-3 text-sm">
                  <UserIcon className="w-4 h-4 text-emerald-400" />
                  <div>
                    <p className="text-xs text-gray-500 m-0">Full Name</p>
                    <p className="text-white font-medium m-0">{userFullName}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Mail className="w-4 h-4 text-emerald-400" />
                  <div>
                    <p className="text-xs text-gray-500 m-0">Email</p>
                    <p className="text-white font-medium m-0">{user.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Phone className="w-4 h-4 text-emerald-400" />
                  <div>
                    <p className="text-xs text-gray-500 m-0">Phone</p>
                    <p className="text-white font-medium m-0">{user.phone}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Scale className="w-4 h-4 text-emerald-400" />
                  <div>
                    <p className="text-xs text-gray-500 m-0">Financial Year</p>
                    <p className="text-white font-medium m-0">2025-2026</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-4 border-t border-gray-800/60 text-xs text-gray-500 flex justify-between">
              <span>Status: Active</span>
              <span>Updated: Just now</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
