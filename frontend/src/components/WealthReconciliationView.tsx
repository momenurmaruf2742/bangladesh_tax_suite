import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import {
  Scale,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Wallet,
  Building,
  Car,
  Gem,
  Coins,
  FileCheck,
  Plus,
  Trash2,
  ShieldCheck,
  TrendingDown,
  Receipt,
  Home,
  Zap,
  ShoppingBag,
  Plane,
  PartyPopper,
  GraduationCap
} from "lucide-react";

interface WealthReconciliationViewProps {
  employee: any;
  onNavigateToSalary?: () => void;
  onNavigateToTaxCalculator?: () => void;
}

interface AssetItem {
  id: string;
  statement_id: string;
  asset_category: string;
  description: string;
  acquisition_type: string;
  cost_value: number;
  particulars: Record<string, any>;
}

export const WealthReconciliationView: React.FC<WealthReconciliationViewProps> = ({
  employee
}) => {
  const queryClient = useQueryClient();
  const [financialYear, setFinancialYear] = useState("2025-2026");
  const [activeStep, setActiveStep] = useState<"lifestyle" | "sources" | "assets" | "audit">("lifestyle");
  const [successToast, setSuccessToast] = useState<string | null>(null);

  // Asset Item modal / form state
  const [isAssetModalOpen, setIsAssetModalOpen] = useState(false);
  const [newAssetCategory, setNewAssetCategory] = useState("motor_vehicles");
  const [newAssetDesc, setNewAssetDesc] = useState("");
  const [newAssetAcquisition, setNewAssetAcquisition] = useState("Purchase");
  const [newAssetCost, setNewAssetCost] = useState("0.00");
  const [newAssetSpec1, setNewAssetSpec1] = useState(""); // CC or Gram
  const [newAssetSpec2, setNewAssetSpec2] = useState(""); // Reg No or Bhori

  const showToast = (msg: string) => {
    setSuccessToast(msg);
    setTimeout(() => setSuccessToast(null), 4000);
  };

  // 1. Fetch IT-10BB Lifestyle Expenses
  const { data: lifestyleData, refetch: refetchLifestyle } = useQuery({
    queryKey: ["lifestyleExpenses", financialYear],
    queryFn: async () => {
      const res = await api.get(`/taxes/it10bb?financial_year=${financialYear}`);
      return res.data;
    },
    enabled: !!employee
  });

  // 2. Fetch IT-10B Statement
  const { data: statementData, refetch: refetchStatement } = useQuery({
    queryKey: ["it10bStatement", financialYear],
    queryFn: async () => {
      const res = await api.get(`/taxes/it10b?financial_year=${financialYear}`);
      return res.data;
    },
    enabled: !!employee
  });

  // Lifestyle Expense local form state
  const [lifestyleForm, setLifestyleForm] = useState({
    fooding_clothing_essentials: "0.00",
    housing_expense: "0.00",
    transport_expense: "0.00",
    utility_expense: "0.00",
    education_expenses: "0.00",
    travel_vacation_expenses: "0.00",
    festival_special_expenses: "0.00",
    interest_paid_borrowing: "0.00",
    other_expenses: "0.00",
    auto_synced_tds: true
  });

  // Statement local form state
  const [statementForm, setStatementForm] = useState({
    taxable_income: "0.00",
    tax_exempted_income: "0.00",
    gifts_and_other_receipts: "0.00",
    net_wealth_previous_year: "0.00",
    other_outflow_losses: "0.00",
    business_assets: "0.00",
    non_agricultural_property: "0.00",
    agricultural_property: "0.00",
    financial_assets_dps: "0.00",
    financial_assets_others: "0.00",
    motor_vehicles_value: "0.00",
    ornaments_gold_value: "0.00",
    furniture_electronics_value: "0.00",
    cash_in_hand: "0.00",
    bank_balances: "0.00",
    other_deposits: "0.00",
    institutional_liabilities: "0.00",
    non_institutional_liabilities: "0.00"
  });

  // Sync state once server query resolves
  React.useEffect(() => {
    if (lifestyleData) {
      setLifestyleForm({
        fooding_clothing_essentials: String(lifestyleData.fooding_clothing_essentials || "0.00"),
        housing_expense: String(lifestyleData.housing_expense || "0.00"),
        transport_expense: String(lifestyleData.transport_expense || "0.00"),
        utility_expense: String(lifestyleData.utility_expense || "0.00"),
        education_expenses: String(lifestyleData.education_expenses || "0.00"),
        travel_vacation_expenses: String(lifestyleData.travel_vacation_expenses || "0.00"),
        festival_special_expenses: String(lifestyleData.festival_special_expenses || "0.00"),
        interest_paid_borrowing: String(lifestyleData.interest_paid_borrowing || "0.00"),
        other_expenses: String(lifestyleData.other_expenses || "0.00"),
        auto_synced_tds: lifestyleData.auto_synced_tds ?? true
      });
    }
  }, [lifestyleData]);

  React.useEffect(() => {
    if (statementData) {
      setStatementForm({
        taxable_income: String(statementData.taxable_income || "0.00"),
        tax_exempted_income: String(statementData.tax_exempted_income || "0.00"),
        gifts_and_other_receipts: String(statementData.gifts_and_other_receipts || "0.00"),
        net_wealth_previous_year: String(statementData.net_wealth_previous_year || "0.00"),
        other_outflow_losses: String(statementData.other_outflow_losses || "0.00"),
        business_assets: String(statementData.business_assets || "0.00"),
        non_agricultural_property: String(statementData.non_agricultural_property || "0.00"),
        agricultural_property: String(statementData.agricultural_property || "0.00"),
        financial_assets_dps: String(statementData.financial_assets_dps || "0.00"),
        financial_assets_others: String(statementData.financial_assets_others || "0.00"),
        motor_vehicles_value: String(statementData.motor_vehicles_value || "0.00"),
        ornaments_gold_value: String(statementData.ornaments_gold_value || "0.00"),
        furniture_electronics_value: String(statementData.furniture_electronics_value || "0.00"),
        cash_in_hand: String(statementData.cash_in_hand || "0.00"),
        bank_balances: String(statementData.bank_balances || "0.00"),
        other_deposits: String(statementData.other_deposits || "0.00"),
        institutional_liabilities: String(statementData.institutional_liabilities || "0.00"),
        non_institutional_liabilities: String(statementData.non_institutional_liabilities || "0.00")
      });
    }
  }, [statementData]);

  // Mutations
  const saveLifestyleMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        financial_year: financialYear,
        fooding_clothing_essentials: parseFloat(lifestyleForm.fooding_clothing_essentials) || 0,
        housing_expense: parseFloat(lifestyleForm.housing_expense) || 0,
        transport_expense: parseFloat(lifestyleForm.transport_expense) || 0,
        utility_expense: parseFloat(lifestyleForm.utility_expense) || 0,
        education_expenses: parseFloat(lifestyleForm.education_expenses) || 0,
        travel_vacation_expenses: parseFloat(lifestyleForm.travel_vacation_expenses) || 0,
        festival_special_expenses: parseFloat(lifestyleForm.festival_special_expenses) || 0,
        interest_paid_borrowing: parseFloat(lifestyleForm.interest_paid_borrowing) || 0,
        other_expenses: parseFloat(lifestyleForm.other_expenses) || 0,
        auto_synced_tds: lifestyleForm.auto_synced_tds
      };
      const res = await api.post("/taxes/it10bb", payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lifestyleExpenses", financialYear] });
      queryClient.invalidateQueries({ queryKey: ["it10bStatement", financialYear] });
      showToast("✅ Form IT-10BB Lifestyle Expenses successfully saved and synced!");
    }
  });

  const saveStatementMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        financial_year: financialYear,
        taxable_income: parseFloat(statementForm.taxable_income) || 0,
        tax_exempted_income: parseFloat(statementForm.tax_exempted_income) || 0,
        gifts_and_other_receipts: parseFloat(statementForm.gifts_and_other_receipts) || 0,
        net_wealth_previous_year: parseFloat(statementForm.net_wealth_previous_year) || 0,
        other_outflow_losses: parseFloat(statementForm.other_outflow_losses) || 0,
        business_assets: parseFloat(statementForm.business_assets) || 0,
        non_agricultural_property: parseFloat(statementForm.non_agricultural_property) || 0,
        agricultural_property: parseFloat(statementForm.agricultural_property) || 0,
        financial_assets_dps: parseFloat(statementForm.financial_assets_dps) || 0,
        financial_assets_others: parseFloat(statementForm.financial_assets_others) || 0,
        motor_vehicles_value: parseFloat(statementForm.motor_vehicles_value) || 0,
        ornaments_gold_value: parseFloat(statementForm.ornaments_gold_value) || 0,
        furniture_electronics_value: parseFloat(statementForm.furniture_electronics_value) || 0,
        cash_in_hand: parseFloat(statementForm.cash_in_hand) || 0,
        bank_balances: parseFloat(statementForm.bank_balances) || 0,
        other_deposits: parseFloat(statementForm.other_deposits) || 0,
        institutional_liabilities: parseFloat(statementForm.institutional_liabilities) || 0,
        non_institutional_liabilities: parseFloat(statementForm.non_institutional_liabilities) || 0
      };
      const res = await api.post("/taxes/it10b", payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["it10bStatement", financialYear] });
      showToast("✅ Form IT-10B Statement of Assets & Liabilities saved!");
    }
  });

  const autoBalanceMutation = useMutation({
    mutationFn: async () => {
      // First save current values to make sure server calculates against latest inputs
      await saveStatementMutation.mutateAsync();
      const res = await api.post(`/taxes/it10b/auto-balance-cash?financial_year=${financialYear}`);
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["it10bStatement", financialYear] });
      setStatementForm((prev) => ({
        ...prev,
        cash_in_hand: String(data.adjusted_cash_in_hand)
      }));
      showToast(`🎯 Auto-balanced into Cash in Hand! Difference reconciled to ৳0.00.`);
    }
  });

  const addAssetItemMutation = useMutation({
    mutationFn: async () => {
      if (!statementData?.id) {
        // Save statement first to generate ID
        const saved = await saveStatementMutation.mutateAsync();
        return await api.post(`/taxes/it10b/${saved.id}/assets`, {
          asset_category: newAssetCategory,
          description: newAssetDesc,
          acquisition_type: newAssetAcquisition,
          cost_value: parseFloat(newAssetCost) || 0,
          particulars: {
            spec_1: newAssetSpec1,
            spec_2: newAssetSpec2
          }
        });
      }
      return await api.post(`/taxes/it10b/${statementData.id}/assets`, {
        asset_category: newAssetCategory,
        description: newAssetDesc,
        acquisition_type: newAssetAcquisition,
        cost_value: parseFloat(newAssetCost) || 0,
        particulars: {
          spec_1: newAssetSpec1,
          spec_2: newAssetSpec2
        }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["it10bStatement", financialYear] });
      setIsAssetModalOpen(false);
      setNewAssetDesc("");
      setNewAssetCost("0.00");
      setNewAssetSpec1("");
      setNewAssetSpec2("");
      showToast("🎁 Asset item registered successfully!");
    }
  });

  const deleteAssetItemMutation = useMutation({
    mutationFn: async (itemId: string) => {
      await api.delete(`/taxes/it10b/assets/${itemId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["it10bStatement", financialYear] });
      showToast("Asset item deleted.");
    }
  });

  // Computed values from current statementData
  const totalFundInflow = Number(statementData?.total_fund_inflow || 0);
  const totalFundOutflow = Number(statementData?.total_fund_outflow || 0);
  const difference = Number(statementData?.difference || 0);
  const isBalanced = statementData?.is_balanced || difference === 0;
  const netWealthClosing = Number(statementData?.net_wealth_closing || 0);
  const changeInNetWealth = Number(statementData?.change_in_net_wealth || 0);
  const totalLifestyleExpense = Number(lifestyleData?.total_lifestyle_expense || 0);
  const syncedTds = Number(lifestyleData?.tax_deducted_source_advance || 0);

  const formatBdt = (val: number) => {
    return `৳${val.toLocaleString("en-BD", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <div className="space-y-6 pb-28">
      {/* Toast Alert */}
      {successToast && (
        <div className="fixed top-5 right-5 z-50 bg-emerald-950/90 border border-emerald-500 text-emerald-300 px-5 py-3 rounded-xl shadow-2xl backdrop-blur-md flex items-center gap-3 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span className="text-sm font-semibold">{successToast}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-gray-900 to-cyan-950/30 border border-emerald-500/20 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
              <Scale className="w-3.5 h-3.5" /> NBR Section 163 & Rule 10B Compliance
            </span>
            <span className="text-xs text-gray-400">
              Assessment Year: <strong className="text-white">2026-2027</strong>
            </span>
          </div>
          <h1 className="text-2xl font-black text-white m-0 tracking-tight">
            IT-10B Assets & IT-10BB Lifestyle Reconciliation Engine
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl leading-relaxed">
            Statutory double-entry verification engine: ensures your source of funds, lifestyle expenses, and closing wealth balance to a difference of exactly <span className="text-emerald-400 font-bold">৳0.00</span>.
          </p>
        </div>

        <div className="flex items-center gap-3 self-stretch md:self-auto">
          <select
            value={financialYear}
            onChange={(e) => setFinancialYear(e.target.value)}
            className="bg-gray-950/80 border border-gray-800 text-white rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:border-emerald-500"
          >
            <option value="2025-2026">FY 2025-2026 (AY 2026-2027)</option>
            <option value="2024-2025">FY 2024-2025 (AY 2025-2026)</option>
          </select>
          <button
            onClick={() => {
              refetchLifestyle();
              refetchStatement();
              showToast("Refreshed statement data.");
            }}
            className="p-2.5 bg-gray-900 hover:bg-gray-800 text-gray-400 hover:text-white rounded-xl border border-gray-800 transition-all cursor-pointer"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Step Tabs Navigation */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 p-1.5 bg-gray-950/60 rounded-xl border border-gray-800">
        <button
          onClick={() => setActiveStep("lifestyle")}
          className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
            activeStep === "lifestyle"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-950"
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/60"
          }`}
        >
          <ShoppingBag className="w-4 h-4" />
          <span>1. IT-10BB Lifestyle</span>
        </button>

        <button
          onClick={() => setActiveStep("sources")}
          className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
            activeStep === "sources"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-950"
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/60"
          }`}
        >
          <Wallet className="w-4 h-4" />
          <span>2. Sources of Fund</span>
        </button>

        <button
          onClick={() => setActiveStep("assets")}
          className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
            activeStep === "assets"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-950"
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/60"
          }`}
        >
          <Building className="w-4 h-4" />
          <span>3. IT-10B Assets & Debt</span>
        </button>

        <button
          onClick={() => setActiveStep("audit")}
          className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
            activeStep === "audit"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-950"
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/60"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>4. Reconciliation Audit</span>
        </button>
      </div>

      {/* TAB 1: IT-10BB LIFESTYLE EXPENSES */}
      {activeStep === "lifestyle" && (
        <div className="glass-panel p-6 rounded-2xl border border-gray-800 space-y-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 pb-4 border-b border-gray-800/80">
            <div>
              <h2 className="text-lg font-bold text-white m-0 flex items-center gap-2">
                <Receipt className="w-5 h-5 text-emerald-400" />
                NBR Form IT-10BB: 9-Line Lifestyle Expenditure Statement
              </h2>
              <p className="text-xs text-gray-400 mt-1 m-0">
                Mandatory itemization of personal and family expenditures for the income year.
              </p>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-right">
              <span className="text-[10px] text-emerald-400 block uppercase font-bold">Total Lifestyle Outflow</span>
              <span className="text-base font-extrabold text-white font-mono">{formatBdt(totalLifestyleExpense)}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Line 1 */}
            <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <ShoppingBag className="w-3.5 h-3.5 text-cyan-400" />
                Line 1: Fooding, Clothing & Essentials
              </label>
              <input
                type="number"
                value={lifestyleForm.fooding_clothing_essentials}
                onChange={(e) => setLifestyleForm({ ...lifestyleForm, fooding_clothing_essentials: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">Personal, family grocery, clothing expenses</span>
            </div>

            {/* Line 2 */}
            <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <Home className="w-3.5 h-3.5 text-cyan-400" />
                Line 2: Housing Accommodation Expense
              </label>
              <input
                type="number"
                value={lifestyleForm.housing_expense}
                onChange={(e) => setLifestyleForm({ ...lifestyleForm, housing_expense: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">House rent or residential maintenance</span>
            </div>

            {/* Line 3 */}
            <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <Car className="w-3.5 h-3.5 text-cyan-400" />
                Line 3: Personal Transport Expense
              </label>
              <input
                type="number"
                value={lifestyleForm.transport_expense}
                onChange={(e) => setLifestyleForm({ ...lifestyleForm, transport_expense: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">Fuel, driver, maintenance, commuting costs</span>
            </div>

            {/* Line 4 */}
            <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                Line 4: Utilities (Electricity, Gas, Water, Net)
              </label>
              <input
                type="number"
                value={lifestyleForm.utility_expense}
                onChange={(e) => setLifestyleForm({ ...lifestyleForm, utility_expense: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">DESCO, WASA, Titas Gas, Internet & Phone</span>
            </div>

            {/* Line 5 */}
            <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <GraduationCap className="w-3.5 h-3.5 text-cyan-400" />
                Line 5: Children / Personal Education
              </label>
              <input
                type="number"
                value={lifestyleForm.education_expenses}
                onChange={(e) => setLifestyleForm({ ...lifestyleForm, education_expenses: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">Tuition, books, university fees</span>
            </div>

            {/* Line 6 */}
            <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <Plane className="w-3.5 h-3.5 text-cyan-400" />
                Line 6: Travel, Vacation & Holidays
              </label>
              <input
                type="number"
                value={lifestyleForm.travel_vacation_expenses}
                onChange={(e) => setLifestyleForm({ ...lifestyleForm, travel_vacation_expenses: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">Local and foreign leisure trips</span>
            </div>

            {/* Line 7 */}
            <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <PartyPopper className="w-3.5 h-3.5 text-cyan-400" />
                Line 7: Festival & Special Occasions
              </label>
              <input
                type="number"
                value={lifestyleForm.festival_special_expenses}
                onChange={(e) => setLifestyleForm({ ...lifestyleForm, festival_special_expenses: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">Eid, Puja, weddings, festive gifts</span>
            </div>

            {/* Line 8 (TDS & Advance Tax - AUTO SYNCED) */}
            <div className="space-y-1.5 p-3.5 bg-emerald-950/20 rounded-xl border border-emerald-500/40 relative">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                  <Coins className="w-3.5 h-3.5 text-emerald-400" />
                  Line 8: Tax Deducted (TDS) & Advance
                </label>
                <span className="text-[9px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-bold uppercase">
                  Auto-Ledger Synced
                </span>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={syncedTds.toFixed(2)}
                  className="w-full bg-gray-900/90 border border-emerald-500/40 text-emerald-400 rounded-lg px-3 py-2 text-xs font-mono font-bold cursor-not-allowed"
                />
              </div>
              <span className="text-[10px] text-emerald-400/80 block">
                Directly calculated from 12 monthly salary TDS challans + AIT receipts.
              </span>
            </div>

            {/* Line 9 */}
            <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <TrendingDown className="w-3.5 h-3.5 text-cyan-400" />
                Line 9: Interest Paid on Borrowings
              </label>
              <input
                type="number"
                value={lifestyleForm.interest_paid_borrowing}
                onChange={(e) => setLifestyleForm({ ...lifestyleForm, interest_paid_borrowing: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">Personal loan interest charges</span>
            </div>
          </div>

          <div className="flex justify-end pt-3">
            <button
              onClick={() => saveLifestyleMutation.mutate()}
              disabled={saveLifestyleMutation.isPending}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg flex items-center gap-2 cursor-pointer"
            >
              <FileCheck className="w-4 h-4" />
              <span>{saveLifestyleMutation.isPending ? "Saving Form..." : "Save IT-10BB Lifestyle & Continue"}</span>
            </button>
          </div>
        </div>
      )}

      {/* TAB 2: SOURCES OF FUND */}
      {activeStep === "sources" && (
        <div className="glass-panel p-6 rounded-2xl border border-gray-800 space-y-6">
          <div className="flex justify-between items-center pb-4 border-b border-gray-800/80">
            <div>
              <h2 className="text-lg font-bold text-white m-0 flex items-center gap-2">
                <Wallet className="w-5 h-5 text-emerald-400" />
                Sources of Fund (Inflow) & Opening Net Wealth
              </h2>
              <p className="text-xs text-gray-400 mt-1 m-0">
                Total fund receipts from employment, business, gifts, plus previous year net wealth.
              </p>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-right">
              <span className="text-[10px] text-cyan-400 block uppercase font-bold">Total Inflow</span>
              <span className="text-base font-extrabold text-white font-mono">{formatBdt(totalFundInflow)}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-1.5 p-4 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 block">Taxable Income</label>
              <input
                type="number"
                value={statementForm.taxable_income}
                onChange={(e) => setStatementForm({ ...statementForm, taxable_income: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">e.g. ৳6,71,533 (Taxable Salary + Other)</span>
            </div>

            <div className="space-y-1.5 p-4 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 block">Tax Exempted Income</label>
              <input
                type="number"
                value={statementForm.tax_exempted_income}
                onChange={(e) => setStatementForm({ ...statementForm, tax_exempted_income: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">e.g. ৳3,35,767 (1/3 salary exemption)</span>
            </div>

            <div className="space-y-1.5 p-4 bg-gray-950/40 rounded-xl border border-gray-800/60">
              <label className="text-xs font-semibold text-gray-300 block">Gifts & Inheritances</label>
              <input
                type="number"
                value={statementForm.gifts_and_other_receipts}
                onChange={(e) => setStatementForm({ ...statementForm, gifts_and_other_receipts: e.target.value })}
                className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-gray-500 block">Cash gifts, loans, capital gains</span>
            </div>

            <div className="space-y-1.5 p-4 bg-emerald-950/20 rounded-xl border border-emerald-500/30">
              <label className="text-xs font-bold text-emerald-300 block">Previous Year Net Wealth</label>
              <input
                type="number"
                value={statementForm.net_wealth_previous_year}
                onChange={(e) => setStatementForm({ ...statementForm, net_wealth_previous_year: e.target.value })}
                className="w-full bg-gray-900 border border-emerald-500/40 text-emerald-300 rounded-lg px-3 py-2 text-xs font-mono font-bold focus:border-emerald-500 focus:outline-none"
                placeholder="0.00"
              />
              <span className="text-[10px] text-emerald-400/80 block">Opening Net Wealth: e.g. ৳1,27,758</span>
            </div>
          </div>

          <div className="flex justify-end pt-3">
            <button
              onClick={() => saveStatementMutation.mutate()}
              disabled={saveStatementMutation.isPending}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg flex items-center gap-2 cursor-pointer"
            >
              <FileCheck className="w-4 h-4" />
              <span>{saveStatementMutation.isPending ? "Saving..." : "Save Sources & Proceed"}</span>
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: ASSETS & LIABILITIES (IT-10B) */}
      {activeStep === "assets" && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-gray-800 space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 pb-4 border-b border-gray-800/80">
              <div>
                <h2 className="text-lg font-bold text-white m-0 flex items-center gap-2">
                  <Building className="w-5 h-5 text-emerald-400" />
                  Form IT-10B: Assets, Properties & Liquid Reserves
                </h2>
                <p className="text-xs text-gray-400 mt-1 m-0">
                  Valuation of properties, vehicles, gold, bank accounts, and debts.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setIsAssetModalOpen(true)}
                  className="px-3.5 py-2 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white text-xs font-bold rounded-xl flex items-center gap-1.5 transition-all shadow-md cursor-pointer"
                >
                  <Plus className="w-4 h-4" />
                  <span>Register Non-Valued Gift / Vehicle</span>
                </button>
              </div>
            </div>

            {/* Assets Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
                <label className="text-xs font-semibold text-gray-300">Non-Agricultural Property</label>
                <input
                  type="number"
                  value={statementForm.non_agricultural_property}
                  onChange={(e) => setStatementForm({ ...statementForm, non_agricultural_property: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-gray-500 block">Flats, commercial land, apartment cost</span>
              </div>

              <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
                <label className="text-xs font-semibold text-gray-300">Agricultural Property</label>
                <input
                  type="number"
                  value={statementForm.agricultural_property}
                  onChange={(e) => setStatementForm({ ...statementForm, agricultural_property: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-gray-500 block">Farmland, rural plots</span>
              </div>

              <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
                <label className="text-xs font-semibold text-gray-300">Financial Assets (DPS / Stocks)</label>
                <input
                  type="number"
                  value={statementForm.financial_assets_dps}
                  onChange={(e) => setStatementForm({ ...statementForm, financial_assets_dps: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-gray-500 block">Bank DPS, Sanchayapatra, shares cost</span>
              </div>

              <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
                <label className="text-xs font-semibold text-gray-300">Motor Vehicles Book Cost</label>
                <input
                  type="number"
                  value={statementForm.motor_vehicles_value}
                  onChange={(e) => setStatementForm({ ...statementForm, motor_vehicles_value: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-gray-500 block">Cost of vehicles (0.00 if gift/inherited)</span>
              </div>

              <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
                <label className="text-xs font-semibold text-gray-300">Gold & Ornaments Cost</label>
                <input
                  type="number"
                  value={statementForm.ornaments_gold_value}
                  onChange={(e) => setStatementForm({ ...statementForm, ornaments_gold_value: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-gray-500 block">Purchase value (0.00 if gift/wedding)</span>
              </div>

              <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
                <label className="text-xs font-semibold text-gray-300">Furniture & Electronics</label>
                <input
                  type="number"
                  value={statementForm.furniture_electronics_value}
                  onChange={(e) => setStatementForm({ ...statementForm, furniture_electronics_value: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-gray-500 block">Laptop, AC, TV, home appliances</span>
              </div>

              <div className="space-y-1.5 p-3.5 bg-gray-950/40 rounded-xl border border-gray-800/60">
                <label className="text-xs font-semibold text-gray-300">Bank Accounts Balance</label>
                <input
                  type="number"
                  value={statementForm.bank_balances}
                  onChange={(e) => setStatementForm({ ...statementForm, bank_balances: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700/80 text-white rounded-lg px-3 py-2 text-xs font-mono focus:border-emerald-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-gray-500 block">Closing balance across all banks at June 30</span>
              </div>

              {/* Cash in Hand */}
              <div className="space-y-1.5 p-3.5 bg-emerald-950/20 rounded-xl border border-emerald-500/40">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold text-emerald-300">Cash in Hand (Liquid)</label>
                  <span className="text-[9px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-bold uppercase">
                    Auto-Adjustable
                  </span>
                </div>
                <input
                  type="number"
                  value={statementForm.cash_in_hand}
                  onChange={(e) => setStatementForm({ ...statementForm, cash_in_hand: e.target.value })}
                  className="w-full bg-gray-900 border border-emerald-500/40 text-emerald-300 rounded-lg px-3 py-2 text-xs font-mono font-bold focus:border-emerald-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-emerald-400/80 block">Liquid physical cash at year end</span>
              </div>

              {/* Liabilities */}
              <div className="space-y-1.5 p-3.5 bg-red-950/20 rounded-xl border border-red-500/30">
                <label className="text-xs font-bold text-red-300">Total Liabilities (Loans / Debts)</label>
                <input
                  type="number"
                  value={statementForm.institutional_liabilities}
                  onChange={(e) => setStatementForm({ ...statementForm, institutional_liabilities: e.target.value })}
                  className="w-full bg-gray-900 border border-red-500/40 text-red-300 rounded-lg px-3 py-2 text-xs font-mono font-bold focus:border-red-500 focus:outline-none"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-red-400/80 block">Bank loans, credit card balances, personal debt</span>
              </div>
            </div>

            <div className="flex justify-end pt-3">
              <button
                onClick={() => saveStatementMutation.mutate()}
                disabled={saveStatementMutation.isPending}
                className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg flex items-center gap-2 cursor-pointer"
              >
                <FileCheck className="w-4 h-4" />
                <span>{saveStatementMutation.isPending ? "Saving..." : "Update Assets & Balance Sheet"}</span>
              </button>
            </div>
          </div>

          {/* Registered Detailed Asset Line Items (Section 3.4 of audit) */}
          <div className="glass-panel p-6 rounded-2xl border border-gray-800 space-y-4">
            <h3 className="text-base font-bold text-white m-0 flex items-center gap-2">
              <Gem className="w-4 h-4 text-amber-400" />
              Detailed Asset Items (Vehicles & Non-Valued Gifts Registry)
            </h3>
            <p className="text-xs text-gray-400 m-0">
              Tracks assets acquired via <span className="text-amber-400 font-semibold">Gift or Inheritance</span> with <code className="text-white bg-gray-800 px-1 rounded">Cost = ৳0.00</code> while preserving vehicle CC and gold gram weight.
            </p>

            {statementData?.asset_items && statementData.asset_items.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left text-gray-300">
                  <thead className="text-[10px] uppercase text-gray-500 border-b border-gray-800">
                    <tr>
                      <th className="py-2.5 px-3">Category</th>
                      <th className="py-2.5 px-3">Description</th>
                      <th className="py-2.5 px-3">Acquisition Type</th>
                      <th className="py-2.5 px-3">Particulars (Engine CC / Gold)</th>
                      <th className="py-2.5 px-3 text-right">Cost Value</th>
                      <th className="py-2.5 px-3 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/40">
                    {statementData.asset_items.map((item: AssetItem) => (
                      <tr key={item.id} className="hover:bg-gray-800/10">
                        <td className="py-3 px-3 font-medium text-white capitalize">{item.asset_category.replace("_", " ")}</td>
                        <td className="py-3 px-3 text-gray-200">{item.description}</td>
                        <td className="py-3 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            item.acquisition_type === "Gift"
                              ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                              : item.acquisition_type === "Inheritance"
                              ? "bg-purple-500/10 text-purple-400 border border-purple-500/30"
                              : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                          }`}>
                            {item.acquisition_type}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-gray-400 font-mono text-[11px]">
                          {item.particulars
                            ? Object.entries(item.particulars)
                                .map(([k, v]) => `${k}: ${v}`)
                                .join(", ")
                            : "—"}
                        </td>
                        <td className="py-3 px-3 text-right font-mono font-bold text-white">
                          {formatBdt(Number(item.cost_value || 0))}
                        </td>
                        <td className="py-3 px-3 text-center">
                          <button
                            onClick={() => deleteAssetItemMutation.mutate(item.id)}
                            className="p-1 text-gray-400 hover:text-red-400 transition-colors cursor-pointer"
                            title="Delete Item"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-6 text-center text-xs text-gray-500 bg-gray-950/40 rounded-xl border border-dashed border-gray-800">
                No individual gift or vehicle items logged yet. Click "Register Non-Valued Gift / Vehicle" above to add one.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: RECONCILIATION AUDIT & FORMULA BALANCE */}
      {activeStep === "audit" && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-gray-800 space-y-6">
            <div className="flex justify-between items-center pb-4 border-b border-gray-800/80">
              <div>
                <h2 className="text-lg font-bold text-white m-0 flex items-center gap-2">
                  <Scale className="w-5 h-5 text-emerald-400" />
                  Statutory Double-Entry Parity Sheet (Rule 10B)
                </h2>
                <p className="text-xs text-gray-400 mt-1 m-0">
                  NBR e-Return verification: Difference must be <strong className="text-emerald-400">৳0.00</strong> to submit online without audit flags.
                </p>
              </div>

              <div className={`px-4 py-2 rounded-xl border flex items-center gap-2 ${
                isBalanced
                  ? "bg-emerald-950/50 border-emerald-500 text-emerald-300 shadow-lg shadow-emerald-950"
                  : "bg-red-950/50 border-red-500 text-red-300 shadow-lg shadow-red-950 animate-pulse"
              }`}>
                {isBalanced ? (
                  <>
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    <div>
                      <span className="text-[10px] uppercase font-bold block leading-none">Status</span>
                      <span className="text-sm font-extrabold">100% Balanced</span>
                    </div>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    <div>
                      <span className="text-[10px] uppercase font-bold block leading-none">Unbalanced Gap</span>
                      <span className="text-sm font-extrabold font-mono">{formatBdt(difference)}</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Reconciliation Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-gray-950/60 border border-gray-800 flex flex-col gap-1">
                <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Total Fund Inflow</span>
                <span className="text-xl font-black text-white font-mono">{formatBdt(totalFundInflow)}</span>
                <span className="text-[10px] text-gray-500">Taxable + Exempted + Gifts</span>
              </div>

              <div className="p-4 rounded-xl bg-gray-950/60 border border-gray-800 flex flex-col gap-1">
                <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Net Wealth Closing</span>
                <span className="text-xl font-black text-cyan-400 font-mono">{formatBdt(netWealthClosing)}</span>
                <span className="text-[10px] text-gray-500">Gross Assets - Liabilities</span>
              </div>

              <div className="p-4 rounded-xl bg-gray-950/60 border border-gray-800 flex flex-col gap-1">
                <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Change in Wealth (ΔW)</span>
                <span className="text-xl font-black text-purple-400 font-mono">{formatBdt(changeInNetWealth)}</span>
                <span className="text-[10px] text-gray-500">Closing - Opening Net Wealth</span>
              </div>

              <div className="p-4 rounded-xl bg-gray-950/60 border border-gray-800 flex flex-col gap-1">
                <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Total Fund Outflow</span>
                <span className="text-xl font-black text-white font-mono">{formatBdt(totalFundOutflow)}</span>
                <span className="text-[10px] text-gray-500">Δ Wealth + Lifestyle Expenses</span>
              </div>
            </div>

            {/* Verification Formula Box */}
            <div className="p-5 rounded-xl bg-gradient-to-r from-gray-950 via-gray-900 to-gray-950 border border-gray-800/80 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 m-0">
                NBR Statutory Equation Verification
              </h3>
              <div className="text-xs text-gray-300 font-mono space-y-1.5 bg-black/40 p-3 rounded-lg border border-gray-800">
                <div>
                  <span className="text-gray-500">Equation:</span> Difference = Total Fund Inflow - (Change in Net Wealth + Lifestyle Outflow)
                </div>
                <div>
                  <span className="text-gray-500">Values:  </span> {formatBdt(totalFundInflow)} - ({formatBdt(changeInNetWealth)} + {formatBdt(totalLifestyleExpense)})
                </div>
                <div className="pt-1.5 border-t border-gray-800 font-bold">
                  <span className="text-gray-500">Result:  </span>{" "}
                  <span className={isBalanced ? "text-emerald-400" : "text-red-400"}>
                    Difference = {formatBdt(difference)} {isBalanced ? "✓ (Balanced)" : "✗ (Action Required)"}
                  </span>
                </div>
              </div>

              {!isBalanced && (
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3 bg-amber-950/20 border border-amber-500/30 rounded-xl">
                  <div className="text-xs text-amber-300 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
                    <span>The statement has an unexplained residual gap of <strong>{formatBdt(difference)}</strong>.</span>
                  </div>
                  <button
                    onClick={() => autoBalanceMutation.mutate()}
                    disabled={autoBalanceMutation.isPending}
                    className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-lg text-xs transition-all shadow-md flex items-center gap-1.5 cursor-pointer shrink-0"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{autoBalanceMutation.isPending ? "Balancing..." : "Auto-Balance into Cash in Hand"}</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* STICKY BOTTOM RECONCILIATION BADGE BAR (PHASE 2 REQUIREMENT) */}
      <div className="fixed bottom-0 left-0 right-0 z-40 bg-gray-950/90 border-t border-emerald-500/30 backdrop-blur-xl px-4 md:px-10 py-3.5 shadow-2xl">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Counters */}
          <div className="flex items-center gap-4 md:gap-8 text-xs">
            <div>
              <span className="text-[10px] text-gray-400 block uppercase font-semibold">Source of Fund</span>
              <span className="font-mono font-bold text-white text-sm">{formatBdt(totalFundInflow)}</span>
            </div>

            <div className="text-gray-600 font-bold">vs</div>

            <div>
              <span className="text-[10px] text-gray-400 block uppercase font-semibold">Total Fund Outflow</span>
              <span className="font-mono font-bold text-white text-sm">{formatBdt(totalFundOutflow)}</span>
            </div>

            <div className="text-gray-600 font-bold">=</div>

            {/* Difference Glow Badge */}
            <div className="flex items-center gap-2">
              <div>
                <span className="text-[10px] text-gray-400 block uppercase font-semibold">Difference</span>
                <span
                  className={`font-mono font-black text-sm px-2.5 py-0.5 rounded-full inline-block ${
                    isBalanced
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.35)]"
                      : "bg-red-500/20 text-red-400 border border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.35)] animate-pulse"
                  }`}
                >
                  {formatBdt(difference)}
                </span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
            {!isBalanced && (
              <button
                onClick={() => autoBalanceMutation.mutate()}
                disabled={autoBalanceMutation.isPending}
                className="px-4 py-2 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white font-bold rounded-xl text-xs transition-all shadow-md flex items-center gap-1.5 cursor-pointer"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Auto-balance Cash in Hand</span>
              </button>
            )}

            <button
              onClick={() => saveStatementMutation.mutate()}
              disabled={saveStatementMutation.isPending}
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition-all shadow-md flex items-center gap-1.5 cursor-pointer"
            >
              <FileCheck className="w-4 h-4" />
              <span>Save IT-10B Statement</span>
            </button>
          </div>
        </div>
      </div>

      {/* Asset Item Creation Modal */}
      {isAssetModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl max-w-md w-full border border-gray-700 space-y-4">
            <div className="flex justify-between items-center pb-2 border-b border-gray-800">
              <h3 className="text-base font-bold text-white m-0">Register Detailed Asset Item</h3>
              <button
                onClick={() => setIsAssetModalOpen(false)}
                className="text-gray-400 hover:text-white text-lg font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">Asset Category</label>
                <select
                  value={newAssetCategory}
                  onChange={(e) => setNewAssetCategory(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-xs"
                >
                  <option value="motor_vehicles">Motor Vehicle (Car / Motorcycle)</option>
                  <option value="ornaments_gold">Gold / Silver / Ornaments</option>
                  <option value="non_agricultural_property">Non-Agricultural Property</option>
                  <option value="furniture_electronics">Furniture / Electronics</option>
                  <option value="other_deposits">Other Assets / Deposits</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">Description / Registration Name</label>
                <input
                  type="text"
                  value={newAssetDesc}
                  onChange={(e) => setNewAssetDesc(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-xs"
                  placeholder="e.g. Dhaka Metro LA 67-6774 Motorcycle 155 CC"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">Acquisition Type</label>
                <select
                  value={newAssetAcquisition}
                  onChange={(e) => setNewAssetAcquisition(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-xs"
                >
                  <option value="Purchase">Purchase (ক্রয়)</option>
                  <option value="Gift">Gift (উপহার - Cost Allowed ৳0.00)</option>
                  <option value="Inheritance">Inheritance (উত্তরাধিকার - Cost Allowed ৳0.00)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">Financial Cost Value (BDT)</label>
                <input
                  type="number"
                  value={newAssetCost}
                  onChange={(e) => setNewAssetCost(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-xs font-mono"
                  placeholder="0.00"
                />
                <span className="text-[10px] text-gray-500">For Gift/Inheritance, value can be 0.00</span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">Specification 1</label>
                  <input
                    type="text"
                    value={newAssetSpec1}
                    onChange={(e) => setNewAssetSpec1(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-xs"
                    placeholder="e.g. 155 CC or 4.75 Gram"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">Specification 2</label>
                  <input
                    type="text"
                    value={newAssetSpec2}
                    onChange={(e) => setNewAssetSpec2(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-xs"
                    placeholder="e.g. Reg No or 2.2 Bhori"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-gray-800">
              <button
                onClick={() => setIsAssetModalOpen(false)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs font-bold cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => addAssetItemMutation.mutate()}
                disabled={addAssetItemMutation.isPending || !newAssetDesc.trim()}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                {addAssetItemMutation.isPending ? "Adding..." : "Add Asset Item"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
