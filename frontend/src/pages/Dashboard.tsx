import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api, tokenStorage } from "../services/api";
import { Loader } from "../components/Loader";
import { TaxCalculatorPanel } from "../components/TaxCalculatorPanel";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";
import { AiTaxAssistantDrawer } from "../components/AiTaxAssistantDrawer";
import { RulesManagerPanel } from "../components/RulesManagerPanel";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  TrendingUp,
  LogOut,
  User as UserIcon,
  Shield,
  FileCheck,
  Scale,
  Activity,
  Calculator,
  Mail,
  Phone,
  Building,
  PlusCircle,
  CheckCircle,
  AlertCircle,
  FileText,
  UploadCloud,
  Trash2,
  Edit3,
  Crown,
  Download,
  FileSpreadsheet,
  Bot,
  Sparkles,
  Scan
} from "lucide-react";

interface Investment {
  id: string;
  employee_id: string;
  financial_year: string;
  category: string;
  amount: number;
  description: string | null;
  doc_path: string | null;
  created_at: string;
  updated_at: string;
}

interface AITRecord {
  id: string;
  employee_id: string;
  financial_year: string;
  category: string;
  amount: number;
  challan_number: string | null;
  challan_date: string | null;
  description: string | null;
  doc_path: string | null;
  created_at: string;
  updated_at: string;
}

interface RebateSummary {
  financial_year: string;
  total_invested: number;
  total_ait: number;
  dps_total: number;
  life_insurance_total: number;
  sanchayapatra_total: number;
  stock_market_total: number;
  other_investments_total: number;
}

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"overview" | "employee" | "employers" | "salary" | "investments" | "tax_calculator" | "admin_center">("overview");
  const [salarySubTab, setSalarySubTab] = useState<"slips" | "summary" | "certificate">("slips");
  const [investSubTab, setInvestSubTab] = useState<"eligible" | "ait" | "summary">("eligible");
  const [isAiDrawerOpen, setIsAiDrawerOpen] = useState(false);
  const [isOcrLoading, setIsOcrLoading] = useState(false);

  const handleDownloadPdfReturn = async () => {
    try {
      const res = await api.get("/reports/tax-return/pdf", { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Tax_Return_Summary_2025-2026.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      alert("Failed to generate PDF Return. Please ensure your employee and salary details are set up.");
    }
  };

  const handleDownloadSalaryExcel = async () => {
    try {
      const res = await api.get("/reports/salary/excel", { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Salary_Statement_2025-2026.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      alert("Failed to export Excel report.");
    }
  };

  const handleOcrSalaryPdf = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsOcrLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post("/ocr/parse-salary-pdf", formData, {
        headers: { "Content-Type": undefined }
      });
      const parsed = res.data.data;
      if (parsed) {
        setSlipForm(prev => ({
          ...prev,
          basic_salary: parsed.basic ? String(parsed.basic) : prev.basic_salary,
          house_rent: parsed.house_rent ? String(parsed.house_rent) : prev.house_rent,
          medical_allowance: parsed.medical ? String(parsed.medical) : prev.medical_allowance,
          conveyance: parsed.conveyance ? String(parsed.conveyance) : prev.conveyance,
          festival_bonus: parsed.festival_bonus ? String(parsed.festival_bonus) : prev.festival_bonus,
          tax_deducted: parsed.tds_deducted ? String(parsed.tds_deducted) : prev.tax_deducted
        }));
        alert("⚡ OCR Scanning Successful! Salary components & TDS figures auto-populated from PDF.");
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || "OCR Parsing failed. Please ensure the document is a readable PDF.");
    } finally {
      setIsOcrLoading(false);
      e.target.value = "";
    }
  };

  // Local state for Employee profile editing
  const [isEditingEmployee, setIsEditingEmployee] = useState(false);
  const [employeeForm, setEmployeeForm] = useState({
    employer_id: "",
    designation: "",
    department: "",
    date_of_joining: "",
    nid: "",
    tax_zone: "",
    tax_circle: "",
    gender: "Male",
    is_disabled: false,
    is_freedom_fighter: false,
    location: "Dhaka/Chittagong City Corporation"
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

  // Local state for Monthly Salary slips
  const [isAddingSlip, setIsAddingSlip] = useState(false);
  const [slipForm, setSlipForm] = useState({
    month: "",
    basic_salary: "0.00",
    house_rent: "0.00",
    medical_allowance: "0.00",
    conveyance: "0.00",
    festival_bonus: "0.00",
    provident_fund: "0.00",
    employer_provident_fund: "0.00",
    other_allowances: "0.00",
    tax_deducted: "0.00"
  });
  const [slipError, setSlipError] = useState<string | null>(null);
  const [grossInput, setGrossInput] = useState("0.00");

  const formatMonthLabel = (mStr: string) => {
    if (!mStr || !mStr.includes("-")) return mStr || "--";
    const [year, month] = mStr.split("-");
    const monthNames = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ];
    const monthIdx = parseInt(month, 10) - 1;
    if (monthIdx >= 0 && monthIdx < 12) {
      return `${monthNames[monthIdx]} ${year}`;
    }
    return mStr;
  };

  const handleAutoCalculateGross = () => {
    const gross = parseFloat(grossInput) || 0;
    if (gross <= 0) return;
    const basic = (gross * 0.60).toFixed(2);
    const houseRent = (gross * 0.30).toFixed(2);
    const medical = (gross * 0.05).toFixed(2);
    const conveyance = (gross * 0.05).toFixed(2);

    setSlipForm(prev => ({
      ...prev,
      basic_salary: basic,
      house_rent: houseRent,
      medical_allowance: medical,
      conveyance: conveyance
    }));
  };


  // Local state for Certificate manual edits
  const [isEditingCert, setIsEditingCert] = useState(false);
  const [certEditForm, setCertEditForm] = useState({
    id: "",
    total_basic: "0.00",
    total_house_rent: "0.00",
    total_medical: "0.00",
    total_conveyance: "0.00",
    total_bonus: "0.00",
    total_provident_fund: "0.00",
    total_tax_deducted: "0.00",
    total_others: "0.00"
  });
  const [certUploadError, setCertUploadError] = useState<string | null>(null);

  // Local state for Investments and AIT
  const [investForm, setInvestForm] = useState({
    financial_year: "2025-2026",
    category: "DPS",
    amount: "0.00",
    description: ""
  });
  const [investError, setInvestError] = useState<string | null>(null);

  const [aitForm, setAitForm] = useState({
    financial_year: "2025-2026",
    category: "Car Registration",
    amount: "0.00",
    challan_number: "",
    challan_date: "",
    description: ""
  });
  const [aitError, setAitError] = useState<string | null>(null);

  const [editingInvestId, setEditingInvestId] = useState<string | null>(null);
  const [editingInvestForm, setEditingInvestForm] = useState({
    category: "DPS",
    amount: "0.00",
    description: ""
  });

  const [editingAitId, setEditingAitId] = useState<string | null>(null);
  const [editingAitForm, setEditingAitForm] = useState({
    category: "Car Registration",
    amount: "0.00",
    challan_number: "",
    challan_date: "",
    description: ""
  });

  // 1. Fetch current User Details
  const { data: user, isLoading: isUserLoading, isError: isUserError } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const res = await api.get("/auth/profile");
      return res.data;
    },
    retry: 1,
  });

  // 2. Fetch Employee Profile Details
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
            tax_circle: res.data.tax_circle || "",
            gender: res.data.gender || "Male",
            is_disabled: res.data.is_disabled ?? false,
            is_freedom_fighter: res.data.is_freedom_fighter ?? false,
            location: res.data.location || "Dhaka/Chittagong City Corporation"
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

  // 3. Fetch Registered Employers List
  const { data: employers, isLoading: isEmployersLoading } = useQuery({
    queryKey: ["employers"],
    queryFn: async () => {
      const res = await api.get("/employers");
      return res.data;
    },
    enabled: !!user
  });

  // 4. Fetch Monthly Salary Slips (Enabled only when employee profile exists)
  const { data: salarySlips, isLoading: isSlipsLoading } = useQuery({
    queryKey: ["salarySlips"],
    queryFn: async () => {
      const res = await api.get("/salaries/slips");
      return res.data;
    },
    enabled: !!employee
  });

  // 5. Fetch Annual Salary Summary
  const { data: salarySummary, isLoading: isSummaryLoading } = useQuery({
    queryKey: ["salarySummary"],
    queryFn: async () => {
      const res = await api.get("/salaries/summary?financial_year=2025-2026");
      return res.data;
    },
    enabled: !!employee
  });

  // 6. Fetch Uploaded Certificates
  const { data: certificates, isLoading: isCertsLoading } = useQuery({
    queryKey: ["certificates"],
    queryFn: async () => {
      const res = await api.get("/salaries/certificates");
      return res.data;
    },
    enabled: !!employee
  });

  // 7. Fetch Super Admin All Users List
  const { data: adminUsers } = useQuery({
    queryKey: ["adminUsers"],
    queryFn: async () => {
      const res = await api.get("/users/admin/all");
      return res.data;
    },
    enabled: !!user && (user.role === "SuperAdmin" || user.role === "Admin"),
    retry: false
  });


  // Fetch Investments
  const { data: investments, isLoading: isInvestmentsLoading } = useQuery({
    queryKey: ["investments"],
    queryFn: async () => {
      const res = await api.get("/investments/investments");
      return res.data as Investment[];
    },
    enabled: !!employee
  });

  // Fetch AIT records
  const { data: aitRecords, isLoading: isAitLoading } = useQuery({
    queryKey: ["aitRecords"],
    queryFn: async () => {
      const res = await api.get("/investments/ait");
      return res.data as AITRecord[];
    },
    enabled: !!employee
  });

  // Fetch Rebate Summary
  const { data: rebateSummary } = useQuery({
    queryKey: ["rebateSummary"],
    queryFn: async () => {
      const res = await api.get("/investments/summary?financial_year=2025-2026");
      return res.data as RebateSummary;
    },
    enabled: !!employee
  });

  const getRebateRate = (year: string) => {
    return year === "2024-2025" ? 0.15 : 0.10;
  };
  const activeYear = rebateSummary?.financial_year || "2025-2026";
  const rebateRate = getRebateRate(activeYear);

  // 7. Mutations
  const saveEmployeeMutation = useMutation({
    mutationFn: async (data: typeof employeeForm) => {
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

  const saveSlipMutation = useMutation({
    mutationFn: async (data: typeof slipForm) => {
      const payload = {
        month: data.month,
        basic_salary: parseFloat(data.basic_salary) || 0,
        house_rent: parseFloat(data.house_rent) || 0,
        medical_allowance: parseFloat(data.medical_allowance) || 0,
        conveyance: parseFloat(data.conveyance) || 0,
        festival_bonus: parseFloat(data.festival_bonus) || 0,
        provident_fund: parseFloat(data.provident_fund) || 0,
        employer_provident_fund: parseFloat(data.employer_provident_fund) || 0,
        other_allowances: parseFloat(data.other_allowances) || 0,
        tax_deducted: parseFloat(data.tax_deducted) || 0
      };
      const res = await api.post("/salaries/slips", payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["salarySlips"] });
      queryClient.invalidateQueries({ queryKey: ["salarySummary"] });
      setIsAddingSlip(false);
      setSlipForm({
        month: "",
        basic_salary: "0.00",
        house_rent: "0.00",
        medical_allowance: "0.00",
        conveyance: "0.00",
        festival_bonus: "0.00",
        provident_fund: "0.00",
        employer_provident_fund: "0.00",
        other_allowances: "0.00",
        tax_deducted: "0.00"
      });
      setSlipError(null);
    },
    onError: (err: any) => {
      setSlipError(err.response?.data?.detail || "Failed to save salary slip.");
    }
  });

  const deleteSlipMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/salaries/slips/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["salarySlips"] });
      queryClient.invalidateQueries({ queryKey: ["salarySummary"] });
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || "Failed to delete salary slip.");
    }
  });

  const uploadSlipPdfMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post("/salaries/upload-slip-pdf", formData, {
        headers: {
          "Content-Type": undefined
        }
      });
      return res.data;
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ["salarySlips"] });
      queryClient.invalidateQueries({ queryKey: ["salarySummary"] });
      setSlipError(null);
      alert(`✅ Monthly Payslip uploaded & parsed successfully for ${formatMonthLabel(data.month)}!\nGross Salary & TDS populated.`);
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || "Failed to upload and parse payslip PDF.";
      setSlipError(msg);
      alert(`❌ PDF Upload Failed: ${msg}`);
    }
  });


  const uploadCertMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("financial_year", "2025-2026");
      const res = await api.post("/salaries/upload-certificate", formData, {
        headers: {
          "Content-Type": undefined
        }
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["certificates"] });
      queryClient.invalidateQueries({ queryKey: ["salarySummary"] });
      setCertUploadError(null);
      alert("✅ Salary Certificate uploaded & parsed successfully!");
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || "Failed to upload salary certificate PDF.";
      setCertUploadError(msg);
      alert(`❌ Certificate Upload Failed: ${msg}`);
    }
  });

  const updateCertMutation = useMutation({
    mutationFn: async (data: typeof certEditForm) => {
      const payload = {
        total_basic: parseFloat(data.total_basic) || 0,
        total_house_rent: parseFloat(data.total_house_rent) || 0,
        total_medical: parseFloat(data.total_medical) || 0,
        total_conveyance: parseFloat(data.total_conveyance) || 0,
        total_bonus: parseFloat(data.total_bonus) || 0,
        total_provident_fund: parseFloat(data.total_provident_fund) || 0,
        total_tax_deducted: parseFloat(data.total_tax_deducted) || 0,
        total_others: parseFloat(data.total_others) || 0
      };
      const res = await api.put(`/salaries/certificates/${data.id}`, payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["certificates"] });
      setIsEditingCert(false);
    }
  });

  const deleteCertMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/salaries/certificates/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["certificates"] });
    }
  });

  // Investment mutations
  const createInvestmentMutation = useMutation({
    mutationFn: async (payload: typeof investForm) => {
      const res = await api.post("/investments/investments", {
        financial_year: payload.financial_year,
        category: payload.category,
        amount: parseFloat(payload.amount) || 0,
        description: payload.description || null
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["investments"] });
      queryClient.invalidateQueries({ queryKey: ["rebateSummary"] });
      setInvestForm({
        financial_year: "2025-2026",
        category: "DPS",
        amount: "0.00",
        description: ""
      });
      setInvestError(null);
    },
    onError: (err: any) => {
      setInvestError(err.response?.data?.detail || "Failed to save investment");
    }
  });

  const updateInvestmentMutation = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: typeof editingInvestForm }) => {
      const res = await api.put(`/investments/investments/${id}`, {
        category: payload.category,
        amount: parseFloat(payload.amount) || 0,
        description: payload.description || null
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["investments"] });
      queryClient.invalidateQueries({ queryKey: ["rebateSummary"] });
      setEditingInvestId(null);
    }
  });

  const deleteInvestmentMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/investments/investments/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["investments"] });
      queryClient.invalidateQueries({ queryKey: ["rebateSummary"] });
    }
  });

  // AIT mutations
  const createAitMutation = useMutation({
    mutationFn: async (payload: typeof aitForm) => {
      const res = await api.post("/investments/ait", {
        financial_year: payload.financial_year,
        category: payload.category,
        amount: parseFloat(payload.amount) || 0,
        challan_number: payload.challan_number || null,
        challan_date: payload.challan_date || null,
        description: payload.description || null
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["aitRecords"] });
      queryClient.invalidateQueries({ queryKey: ["rebateSummary"] });
      setAitForm({
        financial_year: "2025-2026",
        category: "Car Registration",
        amount: "0.00",
        challan_number: "",
        challan_date: "",
        description: ""
      });
      setAitError(null);
    },
    onError: (err: any) => {
      setAitError(err.response?.data?.detail || "Failed to save AIT record");
    }
  });

  const updateAitMutation = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: typeof editingAitForm }) => {
      const res = await api.put(`/investments/ait/${id}`, {
        category: payload.category,
        amount: parseFloat(payload.amount) || 0,
        challan_number: payload.challan_number || null,
        challan_date: payload.challan_date || null,
        description: payload.description || null
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["aitRecords"] });
      queryClient.invalidateQueries({ queryKey: ["rebateSummary"] });
      setEditingAitId(null);
    }
  });

  const deleteAitMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/investments/ait/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["aitRecords"] });
      queryClient.invalidateQueries({ queryKey: ["rebateSummary"] });
    }
  });

  const toggleUserStatusMutation = useMutation({
    mutationFn: async ({ userId, isActive }: { userId: string; isActive: boolean }) => {
      const res = await api.put(`/users/admin/${userId}/status`, { is_active: isActive });
      return res.data;
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ["adminUsers"] });
      alert(`✅ Account status for ${data.email} updated to ${data.is_active ? "Active (Approved)" : "Pending/Suspended"}!`);
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || "Failed to update user account status.");
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

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadCertMutation.mutate(e.target.files[0]);
    }
  };

  if (isUserLoading || isEmployeeLoading || isEmployersLoading || isSlipsLoading || isSummaryLoading || isCertsLoading) {
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
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${activeTab === "overview"
                ? "bg-emerald-500/10 text-emerald-400"
                : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
                }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard Overview
            </button>
            <button
              onClick={() => setActiveTab("employee")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${activeTab === "employee"
                ? "bg-emerald-500/10 text-emerald-400"
                : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
                }`}
            >
              <Users className="w-4 h-4" />
              Employee Info
            </button>
            <button
              onClick={() => setActiveTab("employers")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${activeTab === "employers"
                ? "bg-emerald-500/10 text-emerald-400"
                : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
                }`}
            >
              <Building className="w-4 h-4" />
              Employer Register
            </button>
            <button
              onClick={() => setActiveTab("salary")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${activeTab === "salary"
                ? "bg-emerald-500/10 text-emerald-400"
                : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
                }`}
            >
              <Briefcase className="w-4 h-4" />
              Salary & Allowances
            </button>
            <button
              onClick={() => setActiveTab("investments")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${activeTab === "investments"
                ? "bg-emerald-500/10 text-emerald-400"
                : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
                }`}
            >
              <TrendingUp className="w-4 h-4" />
              Investments & AIT
            </button>
            <button
              onClick={() => setActiveTab("tax_calculator")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${activeTab === "tax_calculator"
                ? "bg-emerald-500/10 text-emerald-400"
                : "text-gray-400 hover:bg-gray-800/40 hover:text-gray-200"
                }`}
            >
              <Calculator className="w-4 h-4" />
              Tax Calculator
            </button>

            {user.role === "SuperAdmin" && (
              <button
                onClick={() => setActiveTab("admin_center")}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all cursor-pointer ${activeTab === "admin_center"
                  ? "bg-purple-500/10 text-purple-400 border border-purple-500/20 font-bold"
                  : "text-purple-400/80 hover:bg-purple-950/30 hover:text-purple-300"
                  }`}
              >
                <Crown className="w-4 h-4 text-purple-400" />
                Super Admin Center
              </button>
            )}
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
              <p className="text-xs font-medium text-emerald-400 truncate m-0">
                {user.role === "Admin" ? "🏢 Company Admin" : user.role === "CA" ? "💼 CA Practitioner" : user.role === "SuperAdmin" ? "👑 Super Admin" : "👤 Taxpayer"}
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
              {activeTab === "salary" && "Salary Components & Certificate"}
              {activeTab === "investments" && "Investments & Tax Rebates"}
              {activeTab === "tax_calculator" && "Income Tax Calculator"}
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              {activeTab === "overview" && "Here is your tax overview for assessment year 2025-2026."}
              {activeTab === "employee" && "Setup and manage your job details and NBR tax circle connections."}
              {activeTab === "employers" && "View and register corporate employer groups."}
              {activeTab === "salary" && "Input monthly salary components, aggregate annual summaries, or verify salary certificates."}
              {activeTab === "investments" && "Log eligible investments (DPS, Insurance, Stocks) and Advance Income Tax (AIT) records."}
              {activeTab === "tax_calculator" && "Calculate dynamic tax projections, investment rebate optimization, and manage historical logs."}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsAiDrawerOpen(true)}
              className="px-3.5 py-1.5 bg-gradient-to-r from-purple-900/40 to-emerald-900/40 hover:from-purple-800/60 hover:to-emerald-800/60 border border-purple-500/30 text-purple-300 text-xs font-bold rounded-lg flex items-center gap-1.5 transition-all cursor-pointer shadow-md"
            >
              <Bot className="w-4 h-4 text-purple-400" />
              <span>AI Assistant</span>
              <Sparkles className="w-3 h-3 text-amber-400 animate-pulse" />
            </button>
            <button
              onClick={handleDownloadPdfReturn}
              className="px-3 py-1.5 bg-emerald-950/50 hover:bg-emerald-900/60 border border-emerald-800/60 text-emerald-300 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all cursor-pointer"
              title="Download NBR Tax Computation PDF"
            >
              <Download className="w-3.5 h-3.5 text-emerald-400" />
              <span>PDF Return</span>
            </button>
            <button
              onClick={handleDownloadSalaryExcel}
              className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all cursor-pointer"
              title="Export Excel Salary Log"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
              <span>Excel Log</span>
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

            {/* Visual Analytics Section (Sprint 7) */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
              <div className="glass-panel p-6 rounded-xl border border-emerald-500/20">
                <h3 className="text-base font-bold text-white mb-4 flex items-center justify-between">
                  <span>📊 Salary Components Breakdown</span>
                  <span className="text-xs font-normal text-emerald-400">Standard Allowances</span>
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: "Basic Salary", value: 60 },
                          { name: "House Rent", value: 30 },
                          { name: "Medical", value: 5 },
                          { name: "Conveyance", value: 5 }
                        ]}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={85}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        <Cell key="cell-0" fill="#059669" />
                        <Cell key="cell-1" fill="#10b981" />
                        <Cell key="cell-2" fill="#34d399" />
                        <Cell key="cell-3" fill="#6ee7b7" />
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "8px" }}
                        itemStyle={{ color: "#e2e8f0" }}
                      />
                      <Legend wrapperStyle={{ fontSize: "12px", color: "#94a3b8" }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="glass-panel p-6 rounded-xl border border-purple-500/20">
                <h3 className="text-base font-bold text-white mb-4 flex items-center justify-between">
                  <span>📈 Tax Slabs Progression (NBR Act 2023)</span>
                  <span className="text-xs font-normal text-purple-400">Rate (%)</span>
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={[
                        { slab: "First 3.5L", rate: 0 },
                        { slab: "Next 1L", rate: 5 },
                        { slab: "Next 3L", rate: 10 },
                        { slab: "Next 4L", rate: 15 },
                        { slab: "Next 5L", rate: 20 },
                        { slab: "Balance", rate: 25 }
                      ]}
                      margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="slab" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "8px" }}
                        itemStyle={{ color: "#a855f7" }}
                      />
                      <Bar dataKey="rate" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
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
                    <h4 className="font-semibold text-white text-sm">Employee Info</h4>
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                      Record your designation, department, dates, NID, and link your corporate employer company.
                    </p>
                  </div>
                  <div
                    onClick={() => setActiveTab("salary")}
                    className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all cursor-pointer"
                  >
                    <h4 className="font-semibold text-white text-sm">Salary & Allowances</h4>
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                      Track basic salary, house rent exemptions, bonuses, and upload annual salary certificates for verification.
                    </p>
                  </div>
                  <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg hover:border-emerald-500/30 transition-all opacity-70">
                    <h4 className="font-semibold text-white text-sm">Investments & Rebates</h4>
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                      Track DPS accounts, Provident Funds, Life Insurance, Sanchayapatra policies, and calculate optimal tax rebate values.
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

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-400 mb-1 text-sm">Gender</label>
                      <select
                        value={employeeForm.gender}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, gender: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors"
                      >
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Third Gender">Third Gender</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-gray-400 mb-1 text-sm">Location (Min Tax Tier)</label>
                      <select
                        value={employeeForm.location}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, location: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors"
                      >
                        <option value="Dhaka/Chittagong City Corporation">Dhaka/Chittagong City Corporation</option>
                        <option value="Other City Corporation">Other City Corporation</option>
                        <option value="Outside City Corporation">Outside City Corporation</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4 py-1">
                    <label className="flex items-center gap-2 text-gray-300 cursor-pointer text-sm">
                      <input
                        type="checkbox"
                        checked={employeeForm.is_disabled}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, is_disabled: e.target.checked })}
                        className="w-4 h-4 rounded text-emerald-500 bg-gray-950/60 border-gray-800 focus:ring-emerald-500 focus:ring-offset-0 cursor-pointer"
                      />
                      <span>Is Person with Disability (PWD)</span>
                    </label>

                    <label className="flex items-center gap-2 text-gray-300 cursor-pointer text-sm">
                      <input
                        type="checkbox"
                        checked={employeeForm.is_freedom_fighter}
                        onChange={(e) => setEmployeeForm({ ...employeeForm, is_freedom_fighter: e.target.checked })}
                        className="w-4 h-4 rounded text-emerald-500 bg-gray-950/60 border-gray-800 focus:ring-emerald-500 focus:ring-offset-0 cursor-pointer"
                      />
                      <span>Is War-wounded Freedom Fighter</span>
                    </label>
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
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">Gender</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.gender || "Male"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">Location (Min Tax Tier)</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.location || "Dhaka/Chittagong City Corporation"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs block uppercase">Special Status</span>
                    <span className="text-white font-semibold text-base block mt-0.5">
                      {employee.is_freedom_fighter ? "Freedom Fighter" : employee.is_disabled ? "Person with Disability (PWD)" : "None"}
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

            {/* Right Col: Add Employer Form */}
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

        {activeTab === "salary" && (
          <div className="flex flex-col gap-6">
            {!employee ? (
              /* Profile Warning state */
              <div className="glass-panel p-8 text-center rounded-xl max-w-lg mx-auto">
                <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-3" />
                <h3 className="text-lg font-bold text-white">Employee Profile Required</h3>
                <p className="text-gray-400 text-sm mt-2 leading-relaxed">
                  Please setup your basic job information, tax zones, and NID inside the **Employee Info** tab before entering monthly components.
                </p>
                <button
                  onClick={() => setActiveTab("employee")}
                  className="mt-5 py-2 px-5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition-colors cursor-pointer"
                >
                  Setup Employee Profile
                </button>
              </div>
            ) : (
              /* Salary Workspace panel */
              <>
                {/* Horizontal navigation menu */}
                <div className="flex gap-2 border-b border-gray-800 pb-px">
                  <button
                    onClick={() => setSalarySubTab("slips")}
                    className={`py-2.5 px-4 border-b-2 font-medium text-sm transition-all cursor-pointer ${salarySubTab === "slips"
                      ? "border-emerald-500 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-gray-300"
                      }`}
                  >
                    Monthly Salary Slips
                  </button>
                  <button
                    onClick={() => setSalarySubTab("summary")}
                    className={`py-2.5 px-4 border-b-2 font-medium text-sm transition-all cursor-pointer ${salarySubTab === "summary"
                      ? "border-emerald-500 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-gray-300"
                      }`}
                  >
                    Annual Salary Summary
                  </button>
                  <button
                    onClick={() => setSalarySubTab("certificate")}
                    className={`py-2.5 px-4 border-b-2 font-medium text-sm transition-all cursor-pointer ${salarySubTab === "certificate"
                      ? "border-emerald-500 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-gray-300"
                      }`}
                  >
                    Salary Certificate PDF
                  </button>
                </div>

                {salarySubTab === "slips" && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Monthly Slips List */}
                    <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col gap-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-gray-800/50">
                        <div>
                          <h3 className="text-lg font-bold text-white m-0">Monthly Salary Logs</h3>
                          <p className="text-xs text-gray-500 m-0 mt-0.5">Upload monthly payslips or manually log components</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <label className="py-1.5 px-3 bg-purple-950/40 hover:bg-purple-900/60 border border-purple-800/60 text-purple-300 text-xs font-semibold rounded-lg transition-colors cursor-pointer flex items-center gap-1.5 shrink-0">
                            <Scan className="w-4 h-4 text-purple-400" />
                            <span>{isOcrLoading ? "Scanning PDF..." : "⚡ Auto-Fill via OCR"}</span>
                            <input
                              type="file"
                              accept=".pdf"
                              className="hidden"
                              disabled={isOcrLoading}
                              onChange={handleOcrSalaryPdf}
                            />
                          </label>
                          <label className="py-1.5 px-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-200 text-xs font-semibold rounded-lg transition-colors cursor-pointer flex items-center gap-1.5 shrink-0">
                            <UploadCloud className="w-4 h-4 text-emerald-400" />
                            <span>{uploadSlipPdfMutation.isPending ? "Parsing PDF..." : "Upload Payslip PDF"}</span>
                            <input
                              type="file"
                              accept=".pdf"
                              className="hidden"
                              disabled={uploadSlipPdfMutation.isPending}
                              onChange={(e) => {
                                if (e.target.files && e.target.files[0]) {
                                  uploadSlipPdfMutation.mutate(e.target.files[0]);
                                  e.target.value = "";
                                }
                              }}
                            />
                          </label>
                          {!isAddingSlip && (
                            <button
                              onClick={() => setIsAddingSlip(true)}
                              className="py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-colors cursor-pointer shrink-0"
                            >
                              + Log Slip
                            </button>
                          )}
                        </div>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-xs text-left text-gray-300">
                          <thead className="text-[10px] uppercase text-gray-500 border-b border-gray-800">
                            <tr>
                              <th className="py-2.5 px-1">Month Period</th>
                              <th className="py-2.5 px-1 text-right">Basic</th>
                              <th className="py-2.5 px-1 text-right">House Rent</th>
                              <th className="py-2.5 px-1 text-right">Medical</th>
                              <th className="py-2.5 px-1 text-right">Bonus</th>
                              <th className="py-2.5 px-1 text-right">PF</th>
                              <th className="py-2.5 px-1 text-right">TDS (Tax)</th>
                              <th className="py-2.5 px-1 text-center">Actions</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-800/50">
                            {salarySlips?.length === 0 ? (
                              <tr>
                                <td colSpan={8} className="text-center py-8 text-gray-500">
                                  No monthly slips logged yet. Upload a payslip PDF or click "+ Log Slip" to start.
                                </td>
                              </tr>
                            ) : (
                              salarySlips?.map((slip: any) => (
                                <tr key={slip.id} className="hover:bg-gray-800/10">
                                  <td className="py-3 px-1 font-semibold text-white">
                                    <div className="text-sm">{formatMonthLabel(slip.month)}</div>
                                    <div className="text-[10px] text-gray-500 font-mono">{slip.month}</div>
                                  </td>
                                  <td className="py-3 px-1 text-right">৳{parseFloat(slip.basic_salary).toLocaleString()}</td>
                                  <td className="py-3 px-1 text-right">৳{parseFloat(slip.house_rent).toLocaleString()}</td>
                                  <td className="py-3 px-1 text-right">৳{parseFloat(slip.medical_allowance).toLocaleString()}</td>
                                  <td className="py-3 px-1 text-right">৳{parseFloat(slip.festival_bonus).toLocaleString()}</td>
                                  <td className="py-3 px-1 text-right">৳{parseFloat(slip.provident_fund).toLocaleString()}</td>
                                  <td className="py-3 px-1 text-right text-amber-500 font-semibold">৳{parseFloat(slip.tax_deducted).toLocaleString()}</td>
                                  <td className="py-3 px-1 text-center space-x-1">
                                    <button
                                      onClick={() => {
                                        setSlipForm({
                                          month: slip.month,
                                          basic_salary: slip.basic_salary,
                                          house_rent: slip.house_rent,
                                          medical_allowance: slip.medical_allowance,
                                          conveyance: slip.conveyance,
                                          festival_bonus: slip.festival_bonus,
                                          provident_fund: slip.provident_fund,
                                          employer_provident_fund: slip.employer_provident_fund,
                                          other_allowances: slip.other_allowances,
                                          tax_deducted: slip.tax_deducted
                                        });
                                        const grossSum = (
                                          parseFloat(slip.basic_salary || 0) +
                                          parseFloat(slip.house_rent || 0) +
                                          parseFloat(slip.medical_allowance || 0) +
                                          parseFloat(slip.conveyance || 0) +
                                          parseFloat(slip.festival_bonus || 0) +
                                          parseFloat(slip.other_allowances || 0)
                                        ).toFixed(2);
                                        setGrossInput(grossSum);
                                        setIsAddingSlip(true);
                                      }}
                                      className="p-1 hover:bg-gray-800 text-gray-400 hover:text-white rounded transition-colors cursor-pointer inline-flex"
                                      title="Edit Slip"
                                    >
                                      <Edit3 className="w-3.5 h-3.5" />
                                    </button>
                                    <button
                                      onClick={() => {
                                        if (confirm(`Are you sure you want to delete the salary slip for ${formatMonthLabel(slip.month)}?`)) {
                                          deleteSlipMutation.mutate(slip.id);
                                        }
                                      }}
                                      disabled={deleteSlipMutation.isPending}
                                      className="p-1 hover:bg-rose-500/10 text-rose-400 rounded transition-colors cursor-pointer disabled:opacity-50 inline-flex"
                                      title="Delete Slip"
                                    >
                                      <Trash2 className="w-3.5 h-3.5" />
                                    </button>
                                  </td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Add Slip Panel Form */}
                    {isAddingSlip && (
                      <div className="glass-panel p-6 rounded-xl flex flex-col gap-4">
                        <h3 className="text-lg font-bold text-white pb-3 border-b border-gray-800/50 m-0">
                          Log Monthly Component
                        </h3>

                        {slipError && (
                          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-200 text-xs flex items-center gap-2">
                            <AlertCircle className="w-4 h-4" />
                            <span>{slipError}</span>
                          </div>
                        )}

                        {/* Quick Gross Auto-Split Box */}
                        <div className="p-3 bg-emerald-950/20 border border-emerald-500/20 rounded-lg space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1">
                              <span>⚡</span> Quick Gross Salary Auto-Split
                            </span>
                            <span className="text-[10px] text-gray-400">BD 60/30/5/5 Standard</span>
                          </div>
                          <div className="flex gap-2">
                            <input
                              type="number"
                              step="0.01"
                              placeholder="Gross Salary (e.g. 82900.00)"
                              value={grossInput}
                              onChange={(e) => setGrossInput(e.target.value)}
                              className="flex-1 px-2.5 py-1.5 bg-gray-950/80 border border-gray-800 rounded text-white text-xs text-right focus:outline-none focus:border-emerald-500"
                            />
                            <button
                              type="button"
                              onClick={handleAutoCalculateGross}
                              className="py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded text-xs transition-colors cursor-pointer shrink-0"
                            >
                              Auto-Fill Breakdown
                            </button>
                          </div>
                        </div>

                        <form
                          onSubmit={(e) => {
                            e.preventDefault();
                            saveSlipMutation.mutate(slipForm);
                          }}
                          className="space-y-3 text-xs"
                        >
                          <div>
                            <div className="flex justify-between items-center mb-1">
                              <label className="block text-gray-400">Month (YYYY-MM)</label>
                              {slipForm.month && (
                                <span className="text-[10px] text-emerald-400 font-bold">
                                  {formatMonthLabel(slipForm.month)}
                                </span>
                              )}
                            </div>
                            <input
                              type="month"
                              value={slipForm.month}
                              onChange={(e) => setSlipForm({ ...slipForm, month: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors"
                              required
                            />
                            <span className="text-[10px] text-gray-500 mt-1 block">
                              Format: YYYY-MM (e.g. 2026-06 for June 2026)
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-gray-400 mb-1">Basic Salary</label>
                              <input
                                type="number"
                                step="0.01"
                                value={slipForm.basic_salary}
                                onChange={(e) => setSlipForm({ ...slipForm, basic_salary: e.target.value })}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right"
                              />
                            </div>
                            <div>
                              <label className="block text-gray-400 mb-1">House Rent</label>
                              <input
                                type="number"
                                step="0.01"
                                value={slipForm.house_rent}
                                onChange={(e) => setSlipForm({ ...slipForm, house_rent: e.target.value })}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right"
                              />
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-gray-400 mb-1">Medical Allowance</label>
                              <input
                                type="number"
                                step="0.01"
                                value={slipForm.medical_allowance}
                                onChange={(e) => setSlipForm({ ...slipForm, medical_allowance: e.target.value })}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right"
                              />
                            </div>
                            <div>
                              <label className="block text-gray-400 mb-1">Conveyance</label>
                              <input
                                type="number"
                                step="0.01"
                                value={slipForm.conveyance}
                                onChange={(e) => setSlipForm({ ...slipForm, conveyance: e.target.value })}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right"
                              />
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-gray-400 mb-1">Festival Bonus</label>
                              <input
                                type="number"
                                step="0.01"
                                value={slipForm.festival_bonus}
                                onChange={(e) => setSlipForm({ ...slipForm, festival_bonus: e.target.value })}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right"
                              />
                            </div>
                            <div>
                              <label className="block text-gray-400 mb-1">Other Allowances</label>
                              <input
                                type="number"
                                step="0.01"
                                value={slipForm.other_allowances}
                                onChange={(e) => setSlipForm({ ...slipForm, other_allowances: e.target.value })}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right"
                              />
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-gray-400 mb-1">PF (Employee)</label>
                              <input
                                type="number"
                                step="0.01"
                                value={slipForm.provident_fund}
                                onChange={(e) => setSlipForm({ ...slipForm, provident_fund: e.target.value })}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right"
                              />
                            </div>
                            <div>
                              <label className="block text-gray-400 mb-1">PF (Employer)</label>
                              <input
                                type="number"
                                step="0.01"
                                value={slipForm.employer_provident_fund}
                                onChange={(e) => setSlipForm({ ...slipForm, employer_provident_fund: e.target.value })}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right"
                              />
                            </div>
                          </div>

                          <div>
                            <label className="block text-gray-400 mb-1">Monthly Source Tax Deducted (TDS)</label>
                            <input
                              type="number"
                              step="0.01"
                              value={slipForm.tax_deducted}
                              onChange={(e) => setSlipForm({ ...slipForm, tax_deducted: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors text-right font-bold text-amber-400"
                            />
                          </div>

                          {/* Calculated Gross Preview Bar */}
                          <div className="p-2.5 bg-gray-900/60 rounded-lg flex justify-between items-center text-xs border border-gray-800">
                            <span className="text-gray-400 font-medium">Calculated Gross Salary:</span>
                            <span className="text-white font-bold text-sm">
                              ৳ {(
                                (parseFloat(slipForm.basic_salary) || 0) +
                                (parseFloat(slipForm.house_rent) || 0) +
                                (parseFloat(slipForm.medical_allowance) || 0) +
                                (parseFloat(slipForm.conveyance) || 0) +
                                (parseFloat(slipForm.festival_bonus) || 0) +
                                (parseFloat(slipForm.other_allowances) || 0)
                              ).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                          </div>

                          <div className="flex gap-2 pt-2">
                            <button
                              type="submit"
                              disabled={saveSlipMutation.isPending}
                              className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white font-semibold rounded-lg shadow transition-colors cursor-pointer"
                            >
                              {saveSlipMutation.isPending ? "Logging..." : "Log Slip"}
                            </button>
                            <button
                              type="button"
                              onClick={() => setIsAddingSlip(false)}
                              className="py-2 px-4 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold rounded-lg transition-colors cursor-pointer"
                            >
                              Cancel
                            </button>
                          </div>
                        </form>
                      </div>
                    )}
                  </div>
                )}

                {salarySubTab === "summary" && (
                  <div className="glass-panel p-6 rounded-xl max-w-3xl mx-auto flex flex-col gap-6">
                    <div className="flex justify-between items-center pb-3 border-b border-gray-800/50">
                      <div>
                        <h3 className="text-lg font-bold text-white m-0">Annual Salary Aggregation</h3>
                        <p className="text-xs text-gray-500 mt-1">
                          Calculated automatically from {salarySummary?.months_count || 0} logged months.
                        </p>
                      </div>
                      <div className="bg-emerald-950/30 border border-emerald-900/40 text-emerald-400 text-xs px-3 py-1.5 rounded-full font-bold">
                        FY {salarySummary?.financial_year || "2025-2026"}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-sm">
                      <div className="space-y-3">
                        <div className="flex justify-between pb-2 border-b border-gray-800/40">
                          <span className="text-gray-400">Total Basic Salary</span>
                          <span className="text-white font-semibold">৳{parseFloat(salarySummary?.total_basic || 0).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between pb-2 border-b border-gray-800/40">
                          <span className="text-gray-400">Total House Rent</span>
                          <span className="text-white font-semibold">৳{parseFloat(salarySummary?.total_house_rent || 0).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between pb-2 border-b border-gray-800/40">
                          <span className="text-gray-400">Total Medical Allowance</span>
                          <span className="text-white font-semibold">৳{parseFloat(salarySummary?.total_medical || 0).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between pb-2 border-b border-gray-800/40">
                          <span className="text-gray-400">Total Conveyance</span>
                          <span className="text-white font-semibold">৳{parseFloat(salarySummary?.total_conveyance || 0).toLocaleString()}</span>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div className="flex justify-between pb-2 border-b border-gray-800/40">
                          <span className="text-gray-400">Festival Bonuses</span>
                          <span className="text-white font-semibold">৳{parseFloat(salarySummary?.total_bonus || 0).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between pb-2 border-b border-gray-800/40">
                          <span className="text-gray-400">Provident Fund (Employee)</span>
                          <span className="text-white font-semibold">৳{parseFloat(salarySummary?.total_provident_fund || 0).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between pb-2 border-b border-gray-800/40">
                          <span className="text-gray-400">Provident Fund (Employer)</span>
                          <span className="text-white font-semibold">৳{parseFloat(salarySummary?.total_employer_provident_fund || 0).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between pb-2 border-b border-gray-800/40">
                          <span className="text-gray-400">Other Allowances</span>
                          <span className="text-white font-semibold">৳{parseFloat(salarySummary?.total_other_allowances || 0).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4 pt-6 border-t border-gray-800">
                      <div className="p-4 bg-emerald-500/5 border border-emerald-500/10 rounded-lg">
                        <span className="text-gray-400 text-xs block">Annual Gross Salary</span>
                        <span className="text-2xl font-bold text-emerald-400 block mt-1">
                          ৳{parseFloat(salarySummary?.gross_salary || 0).toLocaleString()}
                        </span>
                      </div>
                      <div className="p-4 bg-gray-900/60 border border-gray-800 rounded-lg">
                        <span className="text-gray-400 text-xs block">Source Tax Paid (TDS)</span>
                        <span className="text-2xl font-bold text-amber-500 block mt-1">
                          ৳{parseFloat(salarySummary?.total_tax_deducted || 0).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {salarySubTab === "certificate" && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left side: Upload area or list */}
                    <div className="lg:col-span-2 flex flex-col gap-6">
                      {certificates?.length === 0 ? (
                        /* Upload Zone */
                        <div className="glass-panel p-10 rounded-xl text-center flex flex-col items-center justify-center border-2 border-dashed border-gray-800 hover:border-emerald-500/30 transition-all">
                          <UploadCloud className="w-14 h-14 text-gray-600 mb-4" />
                          <h4 className="text-base font-bold text-white">Upload HR Salary Certificate</h4>
                          <p className="text-xs text-gray-500 mt-2 max-w-sm leading-relaxed">
                            Upload your official annual salary certificate PDF (FY 2025-26).
                            Our system will automatically extract and pre-populate your tax calculations.
                          </p>

                          {certUploadError && (
                            <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-200 text-xs">
                              {certUploadError}
                            </div>
                          )}

                          <label className="mt-6 py-2 px-5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow-md cursor-pointer transition-all">
                            Browse PDF File
                            <input
                              type="file"
                              accept="application/pdf"
                              className="hidden"
                              onChange={handleFileUpload}
                            />
                          </label>
                        </div>
                      ) : (
                        /* List Certs */
                        certificates?.map((cert: any) => (
                          <div key={cert.id} className="glass-panel p-6 rounded-xl flex flex-col gap-4">
                            <div className="flex justify-between items-start pb-3 border-b border-gray-800/50">
                              <div className="flex items-center gap-3">
                                <span className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/10">
                                  <FileText className="w-6 h-6" />
                                </span>
                                <div>
                                  <h4 className="font-bold text-white text-sm m-0">{cert.file_name}</h4>
                                  <span className="text-xs text-gray-500">FY {cert.financial_year}</span>
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <button
                                  onClick={() => {
                                    setCertEditForm({
                                      id: cert.id,
                                      total_basic: cert.total_basic,
                                      total_house_rent: cert.total_house_rent,
                                      total_medical: cert.total_medical,
                                      total_conveyance: cert.total_conveyance,
                                      total_bonus: cert.total_bonus,
                                      total_provident_fund: cert.total_provident_fund,
                                      total_tax_deducted: cert.total_tax_deducted,
                                      total_others: cert.total_others
                                    });
                                    setIsEditingCert(true);
                                  }}
                                  className="p-2 text-gray-400 hover:text-white bg-gray-900 border border-gray-800 rounded-lg cursor-pointer"
                                  title="Edit values"
                                >
                                  <Edit3 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => deleteCertMutation.mutate(cert.id)}
                                  className="p-2 text-red-400 hover:text-red-300 bg-red-950/10 border border-red-950/20 rounded-lg cursor-pointer"
                                  title="Delete document"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-2 text-xs">
                              <div>
                                <span className="text-gray-500 block uppercase">Total Basic</span>
                                <span className="text-white font-semibold mt-0.5 block">৳{parseFloat(cert.total_basic).toLocaleString()}</span>
                              </div>
                              <div>
                                <span className="text-gray-500 block uppercase">House Rent</span>
                                <span className="text-white font-semibold mt-0.5 block">৳{parseFloat(cert.total_house_rent).toLocaleString()}</span>
                              </div>
                              <div>
                                <span className="text-gray-500 block uppercase">Medical</span>
                                <span className="text-white font-semibold mt-0.5 block">৳{parseFloat(cert.total_medical).toLocaleString()}</span>
                              </div>
                              <div>
                                <span className="text-gray-500 block uppercase">Conveyance</span>
                                <span className="text-white font-semibold mt-0.5 block">৳{parseFloat(cert.total_conveyance).toLocaleString()}</span>
                              </div>
                              <div>
                                <span className="text-gray-500 block uppercase">Bonuses</span>
                                <span className="text-white font-semibold mt-0.5 block">৳{parseFloat(cert.total_bonus).toLocaleString()}</span>
                              </div>
                              <div>
                                <span className="text-gray-500 block uppercase">Provident Fund</span>
                                <span className="text-white font-semibold mt-0.5 block">৳{parseFloat(cert.total_provident_fund).toLocaleString()}</span>
                              </div>
                              <div>
                                <span className="text-gray-500 block uppercase">Source Tax (TDS)</span>
                                <span className="text-amber-500 font-semibold mt-0.5 block">৳{parseFloat(cert.total_tax_deducted).toLocaleString()}</span>
                              </div>
                              <div>
                                <span className="text-gray-500 block uppercase">Status</span>
                                <span className="bg-emerald-950/30 border border-emerald-900/40 text-emerald-400 text-[10px] px-2 py-0.5 mt-0.5 inline-block font-bold rounded-full">
                                  {cert.status}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>

                    {/* Right side: Manual correction edits */}
                    {isEditingCert && (
                      <div className="glass-panel p-6 rounded-xl flex flex-col gap-4 text-xs">
                        <h3 className="text-lg font-bold text-white pb-3 border-b border-gray-800/50 m-0">
                          Adjust Extracted Values
                        </h3>
                        <form
                          onSubmit={(e) => {
                            e.preventDefault();
                            updateCertMutation.mutate(certEditForm);
                          }}
                          className="space-y-3"
                        >
                          <div>
                            <label className="block text-gray-400 mb-0.5">Total Basic Salary</label>
                            <input
                              type="number"
                              step="0.01"
                              value={certEditForm.total_basic}
                              onChange={(e) => setCertEditForm({ ...certEditForm, total_basic: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white text-right focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-400 mb-0.5">Total House Rent</label>
                            <input
                              type="number"
                              step="0.01"
                              value={certEditForm.total_house_rent}
                              onChange={(e) => setCertEditForm({ ...certEditForm, total_house_rent: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white text-right focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-400 mb-0.5">Total Medical</label>
                            <input
                              type="number"
                              step="0.01"
                              value={certEditForm.total_medical}
                              onChange={(e) => setCertEditForm({ ...certEditForm, total_medical: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white text-right focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-400 mb-0.5">Total Conveyance</label>
                            <input
                              type="number"
                              step="0.01"
                              value={certEditForm.total_conveyance}
                              onChange={(e) => setCertEditForm({ ...certEditForm, total_conveyance: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white text-right focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-400 mb-0.5">Total Bonuses</label>
                            <input
                              type="number"
                              step="0.01"
                              value={certEditForm.total_bonus}
                              onChange={(e) => setCertEditForm({ ...certEditForm, total_bonus: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white text-right focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-400 mb-0.5">Total Provident Fund</label>
                            <input
                              type="number"
                              step="0.01"
                              value={certEditForm.total_provident_fund}
                              onChange={(e) => setCertEditForm({ ...certEditForm, total_provident_fund: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white text-right focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-400 mb-0.5">Total Source Tax (TDS)</label>
                            <input
                              type="number"
                              step="0.01"
                              value={certEditForm.total_tax_deducted}
                              onChange={(e) => setCertEditForm({ ...certEditForm, total_tax_deducted: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white text-right focus:outline-none focus:border-emerald-500"
                            />
                          </div>

                          <div className="flex gap-2 pt-2">
                            <button
                              type="submit"
                              className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg shadow cursor-pointer"
                            >
                              Save Edits
                            </button>
                            <button
                              type="button"
                              onClick={() => setIsEditingCert(false)}
                              className="py-2 px-3 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold rounded-lg cursor-pointer"
                            >
                              Cancel
                            </button>
                          </div>
                        </form>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === "investments" && (
          <div className="flex flex-col gap-6">
            {!employee ? (
              <div className="glass-panel p-8 text-center rounded-xl max-w-lg mx-auto">
                <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-3" />
                <h3 className="text-lg font-bold text-white">Employee Profile Required</h3>
                <p className="text-gray-400 text-sm mt-2 leading-relaxed">
                  Please setup your basic job information inside the **Employee Info** tab before entering investments or AIT logs.
                </p>
                <button
                  onClick={() => setActiveTab("employee")}
                  className="mt-5 py-2 px-5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition-colors cursor-pointer"
                >
                  Setup Employee Profile
                </button>
              </div>
            ) : (
              <>
                {/* Horizontal navigation menu */}
                <div className="flex gap-2 border-b border-gray-800 pb-px">
                  <button
                    onClick={() => setInvestSubTab("eligible")}
                    className={`py-2.5 px-4 border-b-2 font-medium text-sm transition-all cursor-pointer ${investSubTab === "eligible"
                      ? "border-emerald-500 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-gray-300"
                      }`}
                  >
                    Eligible Investments
                  </button>
                  <button
                    onClick={() => setInvestSubTab("ait")}
                    className={`py-2.5 px-4 border-b-2 font-medium text-sm transition-all cursor-pointer ${investSubTab === "ait"
                      ? "border-emerald-500 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-gray-300"
                      }`}
                  >
                    Advance Tax Paid (AIT)
                  </button>
                  <button
                    onClick={() => setInvestSubTab("summary")}
                    className={`py-2.5 px-4 border-b-2 font-medium text-sm transition-all cursor-pointer ${investSubTab === "summary"
                      ? "border-emerald-500 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-gray-300"
                      }`}
                  >
                    Tax Rebate Analytics
                  </button>
                </div>

                {/* Eligible Investments Panel */}
                {investSubTab === "eligible" && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left List Column */}
                    <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col gap-4">
                      <div className="flex justify-between items-center pb-3 border-b border-gray-800/50">
                        <h3 className="text-lg font-bold text-white m-0">Eligible Investment Logs</h3>
                      </div>

                      {editingInvestId ? (
                        /* Inline Edit Form */
                        <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg flex flex-col gap-3">
                          <h4 className="text-sm font-semibold text-emerald-400 m-0">Edit Investment Record</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-gray-400 text-xs mb-1">Category</label>
                              <select
                                value={editingInvestForm.category}
                                onChange={(e) => setEditingInvestForm({ ...editingInvestForm, category: e.target.value })}
                                className="w-full px-3 py-1.5 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                              >
                                <option value="DPS">DPS (Deposit Pension Scheme)</option>
                                <option value="Life Insurance">Life Insurance Premium</option>
                                <option value="Sanchayapatra">Approved Savings Certificate</option>
                                <option value="Stock Market">Stock Market / Mutual Funds</option>
                                <option value="Other">Other Eligible Rebate Assets</option>
                              </select>
                            </div>
                            <div>
                              <label className="block text-gray-400 text-xs mb-1">Amount (BDT)</label>
                              <input
                                type="number"
                                step="0.01"
                                value={editingInvestForm.amount}
                                onChange={(e) => setEditingInvestForm({ ...editingInvestForm, amount: e.target.value })}
                                className="w-full px-3 py-1.5 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 text-right"
                              />
                            </div>
                          </div>
                          <div>
                            <label className="block text-gray-400 text-xs mb-1">Description</label>
                            <input
                              type="text"
                              value={editingInvestForm.description}
                              onChange={(e) => setEditingInvestForm({ ...editingInvestForm, description: e.target.value })}
                              className="w-full px-3 py-1.5 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div className="flex gap-2 justify-end pt-2">
                            <button
                              onClick={() => updateInvestmentMutation.mutate({
                                id: editingInvestId,
                                payload: editingInvestForm
                              })}
                              className="py-1.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg cursor-pointer transition-colors"
                            >
                              Save Changes
                            </button>
                            <button
                              onClick={() => setEditingInvestId(null)}
                              className="py-1.5 px-3 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold text-xs rounded-lg cursor-pointer"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : null}

                      <div className="overflow-x-auto">
                        <table className="w-full text-xs text-left text-gray-300">
                          <thead className="text-[10px] uppercase text-gray-500 border-b border-gray-800">
                            <tr>
                              <th className="py-2.5 px-2">Financial Year</th>
                              <th className="py-2.5 px-2">Category</th>
                              <th className="py-2.5 px-2 text-right">Amount (BDT)</th>
                              <th className="py-2.5 px-2">Description</th>
                              <th className="py-2.5 px-2 text-center">Actions</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-800/40">
                            {isInvestmentsLoading ? (
                              <tr>
                                <td colSpan={5} className="py-4 text-center text-gray-500">Loading investments data...</td>
                              </tr>
                            ) : !investments || investments.length === 0 ? (
                              <tr>
                                <td colSpan={5} className="py-4 text-center text-gray-500">No investment records registered yet.</td>
                              </tr>
                            ) : (
                              investments.map((inv) => (
                                <tr key={inv.id} className="hover:bg-gray-800/10">
                                  <td className="py-3 px-2 font-medium text-white">{inv.financial_year}</td>
                                  <td className="py-3 px-2">
                                    <span className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full font-semibold">
                                      {inv.category}
                                    </span>
                                  </td>
                                  <td className="py-3 px-2 text-right font-bold text-white">
                                    {Number(inv.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                                  </td>
                                  <td className="py-3 px-2 text-gray-400">{inv.description || "—"}</td>
                                  <td className="py-3 px-2 text-center">
                                    <div className="flex justify-center gap-2">
                                      <button
                                        onClick={() => {
                                          setEditingInvestId(inv.id);
                                          setEditingInvestForm({
                                            category: inv.category,
                                            amount: String(inv.amount),
                                            description: inv.description || ""
                                          });
                                        }}
                                        className="p-1 text-gray-400 hover:text-emerald-400 transition-colors cursor-pointer"
                                      >
                                        <Edit3 className="w-3.5 h-3.5" />
                                      </button>
                                      <button
                                        onClick={() => {
                                          if (confirm("Delete this investment log?")) {
                                            deleteInvestmentMutation.mutate(inv.id);
                                          }
                                        }}
                                        className="p-1 text-gray-400 hover:text-red-400 transition-colors cursor-pointer"
                                      >
                                        <Trash2 className="w-3.5 h-3.5" />
                                      </button>
                                    </div>
                                  </td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Right Create Column */}
                    <div className="glass-panel p-6 rounded-xl flex flex-col gap-4 h-fit">
                      <h3 className="text-base font-bold text-white pb-3 border-b border-gray-800/50 m-0">Log Investment Asset</h3>

                      {investError && (
                        <div className="bg-red-950/20 border border-red-900/40 text-red-400 p-2.5 rounded-lg text-xs flex items-center gap-1.5">
                          <AlertCircle className="w-4 h-4 shrink-0" />
                          <span>{investError}</span>
                        </div>
                      )}

                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          createInvestmentMutation.mutate(investForm);
                        }}
                        className="space-y-4 text-xs"
                      >
                        <div>
                          <label className="block text-gray-400 mb-1">Financial Year</label>
                          <select
                            value={investForm.financial_year}
                            onChange={(e) => setInvestForm({ ...investForm, financial_year: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                          >
                            <option value="2025-2026">2025-2026</option>
                            <option value="2026-2027">2026-2027</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-gray-400 mb-1">Rebate Category</label>
                          <select
                            value={investForm.category}
                            onChange={(e) => setInvestForm({ ...investForm, category: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                          >
                            <option value="DPS">DPS (Deposit Pension Scheme)</option>
                            <option value="Life Insurance">Life Insurance Premium</option>
                            <option value="Sanchayapatra">Approved Savings Certificate</option>
                            <option value="Stock Market">Stock Market / Mutual Funds</option>
                            <option value="Other">Other Eligible Rebate Assets</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-gray-400 mb-1">Investment Amount (BDT)</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="0.00"
                            value={investForm.amount}
                            onChange={(e) => setInvestForm({ ...investForm, amount: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 text-right font-semibold"
                          />
                        </div>

                        <div>
                          <label className="block text-gray-400 mb-1">Description / Memo</label>
                          <input
                            type="text"
                            placeholder="e.g. Sonali Bank DPS, policy #..."
                            value={investForm.description}
                            onChange={(e) => setInvestForm({ ...investForm, description: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                          />
                        </div>

                        <button
                          type="submit"
                          disabled={createInvestmentMutation.isPending}
                          className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white font-semibold rounded-lg shadow cursor-pointer transition-colors"
                        >
                          {createInvestmentMutation.isPending ? "Logging..." : "Log Investment"}
                        </button>
                      </form>
                    </div>
                  </div>
                )}

                {/* Advance Tax Paid (AIT) Panel */}
                {investSubTab === "ait" && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left AIT List */}
                    <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col gap-4">
                      <div className="flex justify-between items-center pb-3 border-b border-gray-800/50">
                        <h3 className="text-lg font-bold text-white m-0">Advance Tax Paid (AIT) Logs</h3>
                      </div>

                      {editingAitId ? (
                        /* Inline AIT Edit Form */
                        <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-lg flex flex-col gap-3">
                          <h4 className="text-sm font-semibold text-emerald-400 m-0">Edit AIT Record</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-gray-400 text-xs mb-1">Category</label>
                              <select
                                value={editingAitForm.category}
                                onChange={(e) => setEditingAitForm({ ...editingAitForm, category: e.target.value })}
                                className="w-full px-3 py-1.5 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                              >
                                <option value="Car Registration">Car/Vehicle Fitness Renewal</option>
                                <option value="Bank Interest TDS">Bank Interest Source Tax (TDS)</option>
                                <option value="Property Transaction">Property Transaction / Deed Tax</option>
                                <option value="Other">Other Advance Income Tax Payment</option>
                              </select>
                            </div>
                            <div>
                              <label className="block text-gray-400 text-xs mb-1">Amount (BDT)</label>
                              <input
                                type="number"
                                step="0.01"
                                value={editingAitForm.amount}
                                onChange={(e) => setEditingAitForm({ ...editingAitForm, amount: e.target.value })}
                                className="w-full px-3 py-1.5 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 text-right"
                              />
                            </div>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-gray-400 text-xs mb-1">Challan / Receipt No.</label>
                              <input
                                type="text"
                                value={editingAitForm.challan_number}
                                onChange={(e) => setEditingAitForm({ ...editingAitForm, challan_number: e.target.value })}
                                className="w-full px-3 py-1.5 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                              />
                            </div>
                            <div>
                              <label className="block text-gray-400 text-xs mb-1">Challan Date</label>
                              <input
                                type="date"
                                value={editingAitForm.challan_date}
                                onChange={(e) => setEditingAitForm({ ...editingAitForm, challan_date: e.target.value })}
                                className="w-full px-3 py-1.5 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                              />
                            </div>
                          </div>
                          <div>
                            <label className="block text-gray-400 text-xs mb-1">Description</label>
                            <input
                              type="text"
                              value={editingAitForm.description}
                              onChange={(e) => setEditingAitForm({ ...editingAitForm, description: e.target.value })}
                              className="w-full px-3 py-1.5 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div className="flex gap-2 justify-end pt-2">
                            <button
                              onClick={() => updateAitMutation.mutate({
                                id: editingAitId,
                                payload: editingAitForm
                              })}
                              className="py-1.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg cursor-pointer transition-colors"
                            >
                              Save Changes
                            </button>
                            <button
                              onClick={() => setEditingAitId(null)}
                              className="py-1.5 px-3 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold text-xs rounded-lg cursor-pointer"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : null}

                      <div className="overflow-x-auto">
                        <table className="w-full text-xs text-left text-gray-300">
                          <thead className="text-[10px] uppercase text-gray-500 border-b border-gray-800">
                            <tr>
                              <th className="py-2.5 px-2">FY</th>
                              <th className="py-2.5 px-2">Category</th>
                              <th className="py-2.5 px-2 text-right">Amount (BDT)</th>
                              <th className="py-2.5 px-2">Challan / Date</th>
                              <th className="py-2.5 px-2">Description</th>
                              <th className="py-2.5 px-2 text-center">Actions</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-800/40">
                            {isAitLoading ? (
                              <tr>
                                <td colSpan={6} className="py-4 text-center text-gray-500">Loading AIT records...</td>
                              </tr>
                            ) : !aitRecords || aitRecords.length === 0 ? (
                              <tr>
                                <td colSpan={6} className="py-4 text-center text-gray-500">No Advance Tax records registered yet.</td>
                              </tr>
                            ) : (
                              aitRecords.map((ait) => (
                                <tr key={ait.id} className="hover:bg-gray-800/10">
                                  <td className="py-3 px-2 font-medium text-white">{ait.financial_year}</td>
                                  <td className="py-3 px-2">
                                    <span className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full font-semibold">
                                      {ait.category}
                                    </span>
                                  </td>
                                  <td className="py-3 px-2 text-right font-bold text-white">
                                    {Number(ait.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                                  </td>
                                  <td className="py-3 px-2 text-gray-300">
                                    {ait.challan_number ? (
                                      <div className="leading-tight">
                                        <p className="m-0 font-medium">{ait.challan_number}</p>
                                        <p className="m-0 text-[10px] text-gray-500">{ait.challan_date || "No date"}</p>
                                      </div>
                                    ) : "—"}
                                  </td>
                                  <td className="py-3 px-2 text-gray-400">{ait.description || "—"}</td>
                                  <td className="py-3 px-2 text-center">
                                    <div className="flex justify-center gap-2">
                                      <button
                                        onClick={() => {
                                          setEditingAitId(ait.id);
                                          setEditingAitForm({
                                            category: ait.category,
                                            amount: String(ait.amount),
                                            challan_number: ait.challan_number || "",
                                            challan_date: ait.challan_date || "",
                                            description: ait.description || ""
                                          });
                                        }}
                                        className="p-1 text-gray-400 hover:text-emerald-400 transition-colors cursor-pointer"
                                      >
                                        <Edit3 className="w-3.5 h-3.5" />
                                      </button>
                                      <button
                                        onClick={() => {
                                          if (confirm("Delete this AIT record?")) {
                                            deleteAitMutation.mutate(ait.id);
                                          }
                                        }}
                                        className="p-1 text-gray-400 hover:text-red-400 transition-colors cursor-pointer"
                                      >
                                        <Trash2 className="w-3.5 h-3.5" />
                                      </button>
                                    </div>
                                  </td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Right Create Column */}
                    <div className="glass-panel p-6 rounded-xl flex flex-col gap-4 h-fit">
                      <h3 className="text-base font-bold text-white pb-3 border-b border-gray-800/50 m-0">Log Advance Tax (AIT)</h3>

                      {aitError && (
                        <div className="bg-red-950/20 border border-red-900/40 text-red-400 p-2.5 rounded-lg text-xs flex items-center gap-1.5">
                          <AlertCircle className="w-4 h-4 shrink-0" />
                          <span>{aitError}</span>
                        </div>
                      )}

                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          createAitMutation.mutate(aitForm);
                        }}
                        className="space-y-4 text-xs"
                      >
                        <div>
                          <label className="block text-gray-400 mb-1">Financial Year</label>
                          <select
                            value={aitForm.financial_year}
                            onChange={(e) => setAitForm({ ...aitForm, financial_year: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                          >
                            <option value="2025-2026">2025-2026</option>
                            <option value="2026-2027">2026-2027</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-gray-400 mb-1">AIT Source Category</label>
                          <select
                            value={aitForm.category}
                            onChange={(e) => setAitForm({ ...aitForm, category: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                          >
                            <option value="Car Registration">Car/Vehicle Fitness Renewal</option>
                            <option value="Bank Interest TDS">Bank Interest Source Tax (TDS)</option>
                            <option value="Property Transaction">Property Transaction / Deed Tax</option>
                            <option value="Other">Other Advance Income Tax Payment</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-gray-400 mb-1">Amount Paid (BDT)</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="0.00"
                            value={aitForm.amount}
                            onChange={(e) => setAitForm({ ...aitForm, amount: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 text-right font-semibold"
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-gray-400 mb-1">Challan / Receipt No.</label>
                            <input
                              type="text"
                              placeholder="e.g. CH-9988..."
                              value={aitForm.challan_number}
                              onChange={(e) => setAitForm({ ...aitForm, challan_number: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-400 mb-1">Challan Date</label>
                            <input
                              type="date"
                              value={aitForm.challan_date}
                              onChange={(e) => setAitForm({ ...aitForm, challan_date: e.target.value })}
                              className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-gray-400 mb-1">Description / Memo</label>
                          <input
                            type="text"
                            placeholder="e.g. Sonali Bank, treasury challan..."
                            value={aitForm.description}
                            onChange={(e) => setAitForm({ ...aitForm, description: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                          />
                        </div>

                        <button
                          type="submit"
                          disabled={createAitMutation.isPending}
                          className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white font-semibold rounded-lg shadow cursor-pointer transition-colors"
                        >
                          {createAitMutation.isPending ? "Logging..." : "Log AIT Payment"}
                        </button>
                      </form>
                    </div>
                  </div>
                )}

                {/* Tax Rebate Analytics Panel */}
                {investSubTab === "summary" && (
                  <div className="flex flex-col gap-6">
                    {/* Metrics Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      <div className="glass-panel p-5 rounded-xl bg-gradient-to-br from-emerald-950/20 to-gray-900 border-l-4 border-emerald-500">
                        <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Total Eligible Invested</span>
                        <h2 className="text-2xl font-bold text-white mt-1.5 mb-0.5">
                          {Number(rebateSummary?.total_invested || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </h2>
                        <span className="text-xs text-gray-500">BDT in current FY</span>
                      </div>

                      <div className="glass-panel p-5 rounded-xl bg-gradient-to-br from-indigo-950/20 to-gray-900 border-l-4 border-indigo-500">
                        <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Total AIT Paid (TDS)</span>
                        <h2 className="text-2xl font-bold text-white mt-1.5 mb-0.5">
                          {Number(rebateSummary?.total_ait || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </h2>
                        <span className="text-xs text-gray-500">Adjustable against net tax liability</span>
                      </div>

                      <div className="glass-panel p-5 rounded-xl bg-gradient-to-br from-purple-950/20 to-gray-900 border-l-4 border-purple-500">
                        <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Est. Rebate Percentage</span>
                        <h2 className="text-2xl font-bold text-white mt-1.5 mb-0.5">
                          {Math.round(rebateRate * 100)}%
                        </h2>
                        <span className="text-xs text-emerald-500 font-semibold">Of eligible investments limit</span>
                      </div>

                      <div className="glass-panel p-5 rounded-xl bg-gradient-to-br from-amber-950/20 to-gray-900 border-l-4 border-amber-500">
                        <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Est. Rebate Amount</span>
                        <h2 className="text-2xl font-bold text-emerald-400 mt-1.5 mb-0.5">
                          {Number((rebateSummary?.total_invested || 0) * rebateRate).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </h2>
                        <span className="text-xs text-gray-500">Estimated rebate reduction</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      {/* Breakdown panel */}
                      <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col gap-4">
                        <h3 className="text-sm font-bold text-white pb-2 border-b border-gray-800 m-0">Investment Categories Breakdown</h3>

                        <div className="space-y-4">
                          {/* DPS bar */}
                          <div>
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-gray-300">DPS (Deposit Pension Scheme)</span>
                              <span className="font-bold text-white">
                                {Number(rebateSummary?.dps_total || 0).toLocaleString()} / 1,20,000 BDT Max Limit
                              </span>
                            </div>
                            <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden">
                              <div
                                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${Math.min(100, ((rebateSummary?.dps_total || 0) / 120000) * 100)}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Insurance bar */}
                          <div>
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-gray-300">Life Insurance Premiums</span>
                              <span className="font-bold text-white">
                                {Number(rebateSummary?.life_insurance_total || 0).toLocaleString()} BDT
                              </span>
                            </div>
                            <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden">
                              <div
                                className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${rebateSummary?.life_insurance_total ? 100 : 0}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Sanchaya bar */}
                          <div>
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-gray-300">Savings Certificates (Sanchayapatra)</span>
                              <span className="font-bold text-white">
                                {Number(rebateSummary?.sanchayapatra_total || 0).toLocaleString()} BDT
                              </span>
                            </div>
                            <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden">
                              <div
                                className="bg-purple-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${rebateSummary?.sanchayapatra_total ? 100 : 0}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Stocks bar */}
                          <div>
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-gray-300">Listed Stocks & Mutual Funds</span>
                              <span className="font-bold text-white">
                                {Number(rebateSummary?.stock_market_total || 0).toLocaleString()} BDT
                              </span>
                            </div>
                            <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden">
                              <div
                                className="bg-amber-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${rebateSummary?.stock_market_total ? 100 : 0}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Other bar */}
                          <div>
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-gray-300">Other Rebate eligible donations</span>
                              <span className="font-bold text-white">
                                {Number(rebateSummary?.other_investments_total || 0).toLocaleString()} BDT
                              </span>
                            </div>
                            <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden">
                              <div
                                className="bg-gray-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${rebateSummary?.other_investments_total ? 100 : 0}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Educational Rule Box */}
                      <div className="glass-panel p-6 rounded-xl bg-gradient-to-br from-emerald-950/10 to-gray-900 border border-emerald-900/30 flex flex-col gap-3">
                        <h3 className="text-sm font-bold text-emerald-400 m-0">NBR Tax Rebate Rules (FY {activeYear})</h3>
                        <p className="text-xs text-gray-400 leading-relaxed m-0">
                          Under the **Bangladesh Income Tax Act 2023**, a taxpayer is entitled to get a tax rebate equal to **{Math.round(rebateRate * 100)}%** of the lower of the following:
                        </p>
                        <ol className="text-xs text-gray-400 space-y-1.5 pl-4 m-0 list-decimal">
                          <li>Actual total eligible investments.</li>
                          <li>**3% of Total Taxable Income** (without rebate).</li>
                          <li>**BDT {rebateRate === 0.15 ? "10,00,000 (10 Lakh)" : "7,50,000 (7.5 Lakh)"}**.</li>
                        </ol>
                        <div className="text-[10px] text-gray-500 border-t border-gray-800/80 pt-2.5 mt-1 leading-snug">
                          * Note: DPS eligible amount is capped at a maximum of BDT 1,20,000 per financial year.
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === "tax_calculator" && (
          <TaxCalculatorPanel
            employee={employee}
            onNavigateToProfile={() => setActiveTab("employee")}
            onNavigateToInvestments={() => setActiveTab("investments")}
          />
        )}

        {activeTab === "admin_center" && (
          <div className="space-y-6">
            {/* Header Banner */}
            <div className="glass-panel p-6 rounded-xl bg-gradient-to-r from-purple-950/40 via-gray-900 to-gray-950 border border-purple-500/20 flex justify-between items-center">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5 mb-1">
                  <Crown className="w-4 h-4" /> Live SaaS Platform Control Center
                </span>
                <h1 className="text-2xl font-extrabold text-white m-0">Super Admin Dashboard</h1>
                <p className="text-xs text-gray-400 mt-1 m-0">
                  Manage registered Individual Taxpayers, Companies, CA Firms, and Act 2023 Tax Slabs Engine.
                </p>
              </div>
              <div className="hidden sm:flex items-center gap-3">
                <div className="px-4 py-2 bg-purple-900/30 border border-purple-500/30 rounded-lg text-right">
                  <span className="text-[10px] text-purple-300 block uppercase font-semibold">Active Financial Year</span>
                  <span className="text-sm font-bold text-white">FY 2025-2026</span>
                </div>
              </div>
            </div>

            {/* Metrics Overview Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass-panel p-5 rounded-xl flex items-center gap-4 border border-gray-800">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">
                  👥
                </div>
                <div>
                  <span className="text-xs text-gray-400 block font-medium">Total Registered Users</span>
                  <span className="text-xl font-extrabold text-white">{adminUsers?.length || 1}</span>
                  <span className="text-[10px] text-emerald-400 block">SaaS Active Accounts</span>
                </div>
              </div>

              <div className="glass-panel p-5 rounded-xl flex items-center gap-4 border border-gray-800">
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-bold">
                  🏢
                </div>
                <div>
                  <span className="text-xs text-gray-400 block font-medium">Active Companies</span>
                  <span className="text-xl font-extrabold text-white">{employers?.length || 0}</span>
                  <span className="text-[10px] text-amber-400 block">HR/Employer Admins</span>
                </div>
              </div>

              <div className="glass-panel p-5 rounded-xl flex items-center gap-4 border border-gray-800">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 font-bold">
                  💼
                </div>
                <div>
                  <span className="text-xs text-gray-400 block font-medium">CA Firms & Lawyers</span>
                  <span className="text-xl font-extrabold text-white">
                    {adminUsers?.filter((u: any) => u.role === "CA")?.length || 0}
                  </span>
                  <span className="text-[10px] text-blue-400 block">Tax Practitioners</span>
                </div>
              </div>

              <div className="glass-panel p-5 rounded-xl flex items-center gap-4 border border-gray-800">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 font-bold">
                  ⚖️
                </div>
                <div>
                  <span className="text-xs text-gray-400 block font-medium">Act 2023 Rules Engine</span>
                  <span className="text-xl font-extrabold text-emerald-400">ONLINE</span>
                  <span className="text-[10px] text-purple-400 block">Sec 78 & Slabs Active</span>
                </div>
              </div>
            </div>

            {/* User Management & Rules Panels Grid */}
            <div className="flex flex-col gap-6">
              {/* User Oversight Table */}
              <div className="glass-panel p-6 rounded-xl flex flex-col gap-4">
                <div className="flex justify-between items-center pb-3 border-b border-gray-800/50">
                  <h3 className="text-lg font-bold text-white m-0">System Users Oversight</h3>
                  <span className="text-xs text-purple-400 bg-purple-500/10 px-2.5 py-1 rounded-full border border-purple-500/20 font-semibold">
                    {adminUsers?.length || 0} Total Accounts
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left text-gray-300">
                    <thead className="text-[10px] uppercase text-gray-500 border-b border-gray-800">
                      <tr>
                        <th className="py-2.5 px-2">User Name</th>
                        <th className="py-2.5 px-2">Email</th>
                        <th className="py-2.5 px-2">Phone</th>
                        <th className="py-2.5 px-2">Account Role</th>
                        <th className="py-2.5 px-2 text-center">Status & Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/50">
                      {!adminUsers || adminUsers.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="text-center py-6 text-gray-500">
                            No registered users found.
                          </td>
                        </tr>
                      ) : (
                        adminUsers.map((u: any) => (
                          <tr key={u.id} className="hover:bg-gray-800/20">
                            <td className="py-3 px-2 font-semibold text-white">
                              {u.first_name} {u.last_name}
                            </td>
                            <td className="py-3 px-2 text-gray-300 font-mono text-[11px]">{u.email}</td>
                            <td className="py-3 px-2 text-gray-400">{u.phone}</td>
                            <td className="py-3 px-2">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${u.role === "Admin"
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                : u.role === "CA"
                                  ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                                  : u.role === "SuperAdmin"
                                    ? "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                                    : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                }`}>
                                {u.role === "Admin" ? "Company Admin" : u.role === "CA" ? "CA Firm" : u.role === "SuperAdmin" ? "Super Admin" : "Taxpayer"}
                              </span>
                            </td>
                            <td className="py-3 px-2 text-center">
                              {u.is_active ? (
                                <div className="flex items-center justify-center gap-2">
                                  <span className="text-emerald-400 text-[11px] font-bold">● Active</span>
                                  {u.role !== "SuperAdmin" && (
                                    <button
                                      onClick={() => toggleUserStatusMutation.mutate({ userId: u.id, isActive: false })}
                                      disabled={toggleUserStatusMutation.isPending}
                                      className="text-[10px] px-2 py-0.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded border border-gray-700 transition-colors cursor-pointer"
                                    >
                                      Suspend
                                    </button>
                                  )}
                                </div>
                              ) : (
                                <div className="flex items-center justify-center gap-2">
                                  <span className="text-amber-400 text-[11px] font-bold">● Pending Approval</span>
                                  <button
                                    onClick={() => toggleUserStatusMutation.mutate({ userId: u.id, isActive: true })}
                                    disabled={toggleUserStatusMutation.isPending}
                                    className="text-[10px] px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded shadow transition-colors cursor-pointer"
                                  >
                                    Approve Account
                                  </button>
                                </div>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* NBR Rules Engine Configurator Manager */}
              <div className="glass-panel p-6 rounded-xl flex flex-col gap-4">
                <h3 className="text-lg font-bold text-white pb-3 border-b border-gray-800/50 m-0 flex items-center gap-2">
                  🛠️ NBR Act Rules Engine Configurator (Visual Slab Builder)
                </h3>
                <div className="mt-2.5">
                  <RulesManagerPanel />
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <AiTaxAssistantDrawer
        isOpen={isAiDrawerOpen}
        onClose={() => setIsAiDrawerOpen(false)}
      />
    </div>
  );
};

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
