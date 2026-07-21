import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api, tokenStorage } from "../services/api";
import { Loader } from "../components/Loader";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  TrendingUp,
  FileSpreadsheet,
  LogOut,
  User as UserIcon,
  Shield,
  FileCheck,
  Scale,
  Activity,
  Calculator,
  Bell,
  Mail,
  Phone,
  Building,
  PlusCircle,
  CheckCircle,
  AlertCircle
} from "lucide-react";

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"overview" | "employee" | "employers">("overview");

  // Local state for Employee profile editing
  const [isEditingEmployee, setIsEditingEmployee] = useState(false);
  const [employeeForm, setEmployeeForm] = useState({
    employer_id: "",
    designation: "",
    department: "",
    date_of_joining: "",
    nid: "",
    tax_zone: "",
    tax_circle: ""
  });
  const [employeeError, setEmployeeError] = useState<string | null>(null);

  // Local state for Employer creation
  const [employerForm, setEmployerForm] = useState({
    name: "",
    address: "",
    bin: "",
    contact_email: "",
    contact_phone: ""
  });
  const [employerError, setEmployerError] = useState<string | null>(null);
  const [employerSuccess, setEmployerSuccess] = useState(false);

  // 1. Fetch current User Details
  const { data: user, isLoading: isUserLoading, isError: isUserError } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const res = await api.get("/auth/profile");
      return res.data;
    },
    retry: 1,
  });

  const { data: employee, isLoading: isEmployeeLoading } = useQuery({
    queryKey: ["employeeProfile"],
    queryFn: async () => {
      try {
        const res = await api.get("/employees/profile");
        // Pre-fill edit form
        if (res.data) {
          setEmployeeForm({
            employer_id: res.data.employer_id || "",
            designation: res.data.designation || "",
            department: res.data.department || "",
            date_of_joining: res.data.date_of_joining || "",
            nid: res.data.nid || "",
            tax_zone: res.data.tax_zone || "",
            tax_circle: res.data.tax_circle || ""
          });
        }
        return res.data;
      } catch (err: any) {
        if (err.response?.status === 404) {
          return null; // Return null if profile does not exist yet
        }
        throw err;
      }
    },
    enabled: !!user,
    retry: false
  });

  const { data: employers, isLoading: isEmployersLoading } = useQuery({
    queryKey: ["employers"],
    queryFn: async () => {
      const res = await api.get("/employers");
      return res.data;
    },
    enabled: !!user
  });

  // 4. Mutation to Save Employee Profile
  const saveEmployeeMutation = useMutation({
    mutationFn: async (data: typeof employeeForm) => {
      // Clean up empty optional values before sending
      const payload = {
        ...data,
        employer_id: data.employer_id ? data.employer_id : null,
        date_of_joining: data.date_of_joining ? data.date_of_joining : null,
        nid: data.nid ? data.nid : null,
        tax_zone: data.tax_zone ? data.tax_zone : null,
        tax_circle: data.tax_circle ? data.tax_circle : null
      };
      const res = await api.post("/employees/profile", payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employeeProfile"] });
      setIsEditingEmployee(false);
      setEmployeeError(null);
    },
    onError: (err: any) => {
      setEmployeeError(err.response?.data?.detail || "Failed to save profile. Please check inputs.");
    }
  });

  // 5. Mutation to Create Employer
  const createEmployerMutation = useMutation({
    mutationFn: async (data: typeof employerForm) => {
      const payload = {
        ...data,
        bin: data.bin ? data.bin : null,
        contact_email: data.contact_email ? data.contact_email : null,
        contact_phone: data.contact_phone ? data.contact_phone : null
      };
      const res = await api.post("/employers/", payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employers"] });
      setEmployerForm({ name: "", address: "", bin: "", contact_email: "", contact_phone: "" });
      setEmployerSuccess(true);
      setEmployerError(null);
      setTimeout(() => setEmployerSuccess(false), 3000);
    },
    onError: (err: any) => {
      setEmployerError(err.response?.data?.detail || "Failed to create employer. Make sure BIN is unique.");
    }
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

  if (isUserLoading || isEmployeeLoading || isEmployersLoading) {
    return <Loader fullPage />;
  }

  if (isUserError || !user) {
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
            <button
              onClick={() => setActiveTab("overview")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${
                activeTab === "overview"
                  ? "bg-emerald-500/10 text-emerald-400"
                  : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard Overview
            </button>
            <button
              onClick={() => setActiveTab("employee")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${
                activeTab === "employee"
                  ? "bg-emerald-500/10 text-emerald-400"
                  : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
              }`}
            >
              <Users className="w-4 h-4" />
              Employee Info
            </button>
            <button
              onClick={() => setActiveTab("employers")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${
                activeTab === "employers"
                  ? "bg-emerald-500/10 text-emerald-400"
                  : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
              }`}
            >
              <Building className="w-4 h-4" />
              Employer Register
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-500 text-sm cursor-not-allowed opacity-60">
              <Briefcase className="w-4 h-4" />
              Salary & Allowances
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-500 text-sm cursor-not-allowed opacity-60">
              <TrendingUp className="w-4 h-4" />
              Investments & Rebates
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-500 text-sm cursor-not-allowed opacity-60">
              <FileSpreadsheet className="w-4 h-4" />
              AIT Records
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-500 text-sm cursor-not-allowed opacity-60">
              <Calculator className="w-4 h-4" />
              Tax Calculator
            </button>
          </nav>
        </div>

        {/* User Card & Logout */}
        <div className="p-4 border-t border-gray-800/60 space-y-3">
          <div className="flex items-center gap-3 px-2">
            <div className="w-9 h-9 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold shrink-0">
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
              {activeTab === "overview" && `Welcome back, ${user.first_name}!`}
              {activeTab === "employee" && "Employee Profile Management"}
              {activeTab === "employers" && "Employer Directories"}
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              {activeTab === "overview" && "Here is your tax overview for assessment year 2025-2026."}
              {activeTab === "employee" && "Setup and manage your job details and NBR tax circle connections."}
              {activeTab === "employers" && "View and register corporate employer groups."}
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

        {/* Tab content rendering */}
        {activeTab === "overview" && (
          <>
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
                  <div
                    onClick={() => setActiveTab("employee")}
                    className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all cursor-pointer"
                  >
                    <h4 className="font-semibold text-white text-sm">Employee & Salary</h4>
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                      Record your employment agreements, scale basic pay, allowances, house rent exemptions, bonuses, and special festival perks.
                    </p>
                  </div>
                  <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all opacity-70">
                    <h4 className="font-semibold text-white text-sm">Investments & Rebates</h4>
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                      Track DPS accounts, Provident Funds, Life Insurance, Sanchayapatra policies, and calculate optimal tax rebate values.
                    </p>
                  </div>
                  <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all opacity-70">
                    <h4 className="font-semibold text-white text-sm">Tax Engine Rules</h4>
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                      NBR regulations for FY 2025-2026. Automated slabs, taxable boundaries, minimum tax brackets, and AIT source adjustments.
                    </p>
                  </div>
                  <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all opacity-70">
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
          </>
        )}

        {activeTab === "employee" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Col: Profile info or Editor */}
            <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col gap-4">
              <div className="flex justify-between items-center pb-3 border-b border-gray-800/50">
                <h3 className="text-lg font-bold text-white m-0">
                  {isEditingEmployee || !employee ? "Edit Profile details" : "Employment Profile Info"}
                </h3>
                {employee && !isEditingEmployee && (
                  <button
                    onClick={() => setIsEditingEmployee(true)}
                    className="py-1.5 px-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/20 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
                  >
                    Edit details
                  </button>
                )}
              </div>

              {employeeError && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-200 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{employeeError}</span>
                </div>
              )}

              {isEditingEmployee || !employee ? (
                /* Form Editor */
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    saveEmployeeMutation.mutate(employeeForm);
                  }}
                  className="space-y-4 text-sm mt-2"
                >
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-400 mb-1">Designation</label>
                      <input
                        type="text"
                        placeholder="e.g. Lead Developer"
                        value={employeeForm.designation}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, designation: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-gray-400 mb-1">Department</label>
                      <input
                        type="text"
                        placeholder="e.g. Technology"
                        value={employeeForm.department}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, department: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-400 mb-1">Date of Joining</label>
                      <input
                        type="date"
                        value={employeeForm.date_of_joining}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, date_of_joining: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-400 mb-1">NID (National ID)</label>
                      <input
                        type="text"
                        placeholder="10 or 17-digit ID"
                        value={employeeForm.nid}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, nid: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-400 mb-1">Bangladesh Tax Zone</label>
                      <input
                        type="text"
                        placeholder="e.g. Tax Zone 15, Dhaka"
                        value={employeeForm.tax_zone}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, tax_zone: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-400 mb-1">Bangladesh Tax Circle</label>
                      <input
                        type="text"
                        placeholder="e.g. Circle 302"
                        value={employeeForm.tax_circle}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, tax_circle: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-400 mb-1">Link Corporate Employer</label>
                    <select
                      value={employeeForm.employer_id}
                      onChange={(e) => setEmployeeForm({ ...employeeForm, employer_id: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors"
                    >
                      <option value="">-- No Linked Company --</option>
                      {employers?.map((emp: any) => (
                        <option key={emp.id} value={emp.id}>
                          {emp.name} {emp.bin ? `(BIN: ${emp.bin})` : ""}
                        </option>
                      ))}
                    </select>
                    <p className="text-gray-500 text-xs mt-1">
                      If your employer company is not listed, you can register it in the "Employer Register" tab first.
                    </p>
                  </div>

                  <div className="flex gap-3 pt-2">
                    <button
                      type="submit"
                      disabled={saveEmployeeMutation.isPending}
                      className="py-2 px-5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white font-semibold rounded-lg shadow-md transition-colors cursor-pointer"
                    >
                      {saveEmployeeMutation.isPending ? "Saving..." : "Save details"}
                    </button>
                    {employee && (
                      <button
                        type="button"
                        onClick={() => setIsEditingEmployee(false)}
                        className="py-2 px-5 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold rounded-lg transition-colors cursor-pointer"
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </form>
              ) : (
                /* Profile Display Panel */
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 py-2 text-sm">
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">Designation</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.designation || "--"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">Department</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.department || "--"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">Date of Joining</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.date_of_joining || "--"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">National ID (NID)</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.nid || "--"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">Tax Zone</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.tax_zone || "--"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">Tax Circle</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.tax_circle || "--"}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Right Col: Employer details if linked */}
            <div className="glass-panel p-6 rounded-xl flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold text-white pb-3 border-b border-gray-800/50 m-0">
                  Linked Employer Group
                </h3>
                {employee?.employer ? (
                  <div className="space-y-4 mt-6 text-sm">
                    <div className="flex items-center gap-3">
                      <Building className="w-5 h-5 text-emerald-400 shrink-0" />
                      <div>
                        <p className="text-xs text-gray-500 m-0">Company Name</p>
                        <p className="text-white font-semibold m-0">{employee.employer.name}</p>
                      </div>
                    </div>
                    {employee.employer.bin && (
                      <div className="flex items-center gap-3">
                        <FileCheck className="w-5 h-5 text-emerald-400 shrink-0" />
                        <div>
                          <p className="text-xs text-gray-500 m-0">Corporate BIN</p>
                          <p className="text-white font-semibold m-0">{employee.employer.bin}</p>
                        </div>
                      </div>
                    )}
                    {employee.employer.address && (
                      <div className="flex items-center gap-3">
                        <MapPinIcon className="w-5 h-5 text-emerald-400 shrink-0" />
                        <div>
                          <p className="text-xs text-gray-500 m-0">Corporate Address</p>
                          <p className="text-white font-semibold m-0">{employee.employer.address}</p>
                        </div>
                      </div>
                    )}
                    {employee.employer.contact_email && (
                      <div className="flex items-center gap-3">
                        <Mail className="w-5 h-5 text-emerald-400 shrink-0" />
                        <div>
                          <p className="text-xs text-gray-500 m-0">HR Email</p>
                          <p className="text-white font-semibold m-0">{employee.employer.contact_email}</p>
                        </div>
                      </div>
                    )}
                    {employee.employer.contact_phone && (
                      <div className="flex items-center gap-3">
                        <Phone className="w-5 h-5 text-emerald-400 shrink-0" />
                        <div>
                          <p className="text-xs text-gray-500 m-0">HR Hotlines</p>
                          <p className="text-white font-semibold m-0">{employee.employer.contact_phone}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-10">
                    <Building className="w-12 h-12 text-gray-700 mx-auto mb-3" />
                    <p className="text-gray-400 text-sm">No company linked.</p>
                    <p className="text-xs text-gray-600 mt-1 max-w-[200px] mx-auto">
                      Edit details to link your profile to a company.
                    </p>
                  </div>
                )}
              </div>
              <div className="mt-6 pt-4 border-t border-gray-800/60 text-xs text-gray-500">
                System: Automated NBR slabs link
              </div>
            </div>
          </div>
        )}

        {activeTab === "employers" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Col: List of Employers */}
            <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col gap-4">
              <h3 className="text-lg font-bold text-white pb-3 border-b border-gray-800/50 m-0">
                Registered Corporate Employer list
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-gray-300">
                  <thead className="text-xs uppercase text-gray-500 border-b border-gray-800">
                    <tr>
                      <th className="py-3 px-2">Company Name</th>
                      <th className="py-3 px-2">BIN</th>
                      <th className="py-3 px-2">Contact Details</th>
                      <th className="py-3 px-2">Location</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/60">
                    {employers?.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="text-center py-8 text-gray-500">
                          No employers registered. Register one using the panel on the right.
                        </td>
                      </tr>
                    ) : (
                      employers?.map((emp: any) => (
                        <tr key={emp.id} className="hover:bg-gray-800/20 transition-all">
                          <td className="py-3.5 px-2 font-semibold text-white">{emp.name}</td>
                          <td className="py-3.5 px-2">{emp.bin || "--"}</td>
                          <td className="py-3.5 px-2 text-xs">
                            <div>{emp.contact_email || ""}</div>
                            <div className="text-gray-500">{emp.contact_phone || ""}</div>
                          </td>
                          <td className="py-3.5 px-2 text-xs text-gray-400">{emp.address || "--"}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Right Col: Add Employer Form (Available to all for testing, with roles guarded on server) */}
            <div className="glass-panel p-6 rounded-xl flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold text-white pb-3 border-b border-gray-800/50 m-0 flex items-center gap-2">
                  <PlusCircle className="w-5 h-5 text-emerald-400" />
                  Register Corporate Group
                </h3>

                {employerSuccess && (
                  <div className="mt-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-200 text-xs flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 shrink-0" />
                    <span>Company registered successfully!</span>
                  </div>
                )}

                {employerError && (
                  <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-200 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{employerError}</span>
                  </div>
                )}

                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    createEmployerMutation.mutate(employerForm);
                  }}
                  className="space-y-4 mt-6 text-sm"
                >
                  <div>
                    <label className="block text-gray-400 mb-1">Company Name</label>
                    <input
                      type="text"
                      placeholder="e.g. Brain Station 23"
                      value={employerForm.name}
                      onChange={(e) => setEmployerForm({ ...employerForm, name: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-gray-400 mb-1">BIN (Business Tax ID)</label>
                    <input
                      type="text"
                      placeholder="e.g. 000123456-0101"
                      value={employerForm.bin}
                      onChange={(e) => setEmployerForm({ ...employerForm, bin: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-400 mb-1">HR Email</label>
                    <input
                      type="email"
                      placeholder="hr@company.com"
                      value={employerForm.contact_email}
                      onChange={(e) => setEmployerForm({ ...employerForm, contact_email: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-400 mb-1">Contact Phone</label>
                    <input
                      type="text"
                      placeholder="+8801..."
                      value={employerForm.contact_phone}
                      onChange={(e) => setEmployerForm({ ...employerForm, contact_phone: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-400 mb-1">HQ Address</label>
                    <textarea
                      placeholder="Street, City, Bangladesh"
                      value={employerForm.address}
                      onChange={(e) => setEmployerForm({ ...employerForm, address: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors h-20 resize-none"
                    ></textarea>
                  </div>

                  <button
                    type="submit"
                    disabled={createEmployerMutation.isPending}
                    className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white font-semibold rounded-lg shadow-md transition-colors cursor-pointer"
                  >
                    {createEmployerMutation.isPending ? "Registering..." : "Register Group"}
                  </button>
                </form>
              </div>
              <div className="mt-8 pt-4 border-t border-gray-800/60 text-xs text-gray-500">
                Authorized role restrictions check on submit
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

// Quick icons helper to handle missing imports
const MapPinIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);
