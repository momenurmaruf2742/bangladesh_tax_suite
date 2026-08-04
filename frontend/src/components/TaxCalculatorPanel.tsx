import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import {
  Calculator,
  AlertCircle,
  Trash2,
  Save,
  Info,
  History,
  Coins,
  FileText
} from "lucide-react";

interface TaxCalculatorPanelProps {
  employee: any;
  onNavigateToProfile: () => void;
  onNavigateToInvestments: () => void;
}

export const TaxCalculatorPanel: React.FC<TaxCalculatorPanelProps> = ({
  employee,
  onNavigateToProfile,
  onNavigateToInvestments
}) => {
  const queryClient = useQueryClient();
  const [financialYear, setFinancialYear] = useState("2025-2026");
  const [otherIncome, setOtherIncome] = useState("0.00");
  const [localError, setLocalError] = useState<string | null>(null);
  const [calcResult, setCalcResult] = useState<any | null>(null);

  // 1. Fetch saved calculations history
  const { data: history = [], isLoading: isHistoryLoading } = useQuery({
    queryKey: ["taxHistory"],
    queryFn: async () => {
      const res = await api.get("/taxes/history");
      return res.data;
    },
    enabled: !!employee
  });

  // 2. Calculate Projection Mutation
  const calculateMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post("/taxes/calculate", {
        financial_year: financialYear,
        other_income: parseFloat(otherIncome) || 0
      });
      return res.data;
    },
    onSuccess: (data) => {
      setCalcResult(data);
      setLocalError(null);
    },
    onError: (err: any) => {
      setLocalError(err.response?.data?.detail || "Failed to calculate tax projection.");
    }
  });

  // 3. Calculate and Save Mutation
  const saveMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post("/taxes/calculate-save", {
        financial_year: financialYear,
        other_income: parseFloat(otherIncome) || 0
      });
      return res.data;
    },
    onSuccess: (data) => {
      setCalcResult(data);
      setLocalError(null);
      queryClient.invalidateQueries({ queryKey: ["taxHistory"] });
    },
    onError: (err: any) => {
      setLocalError(err.response?.data?.detail || "Failed to save tax calculation.");
    }
  });

  // 4. Delete Saved Mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/taxes/history/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["taxHistory"] });
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || "Failed to delete saved calculation.");
    }
  });

  // If no employee profile is configured, show setup warning
  if (!employee) {
    return (
      <div className="glass-panel p-8 rounded-xl max-w-2xl mx-auto text-center space-y-6 my-8">
        <div className="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center mx-auto">
          <AlertCircle className="w-8 h-8 text-amber-500" />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-white">Employee Profile Setup Required</h2>
          <p className="text-gray-400 text-sm max-w-md mx-auto">
            The tax engine requires parameters like gender, disabled status, freedom fighter status, and city corporation location from your employee profile to determine tax slabs, rebate limits, and local minimum tax rates.
          </p>
        </div>
        <button
          onClick={onNavigateToProfile}
          className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg shadow-md transition-colors cursor-pointer"
        >
          Configure Employee Profile
        </button>
      </div>
    );
  }

  const formatCurrency = (val: number | string | undefined) => {
    if (val === undefined || val === null) return "0.00";
    return Number(val).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    calculateMutation.mutate();
  };

  const handleSave = () => {
    saveMutation.mutate();
  };

  const handleViewReturn = async (id: string) => {
    try {
      const res = await api.get(`/taxes/history/${id}/return/html`);
      const blob = new Blob([res.data], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
    } catch (err) {
      alert("Failed to load tax return form.");
    }
  };

  return (
    <div className="space-y-8">
      {localError && (
        <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{localError}</span>
        </div>
      )}

      {/* Main Grid: Form and Projection View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Form Controls & Settings */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass-panel p-6 rounded-xl space-y-6">
            <div className="flex items-center gap-2 pb-3 border-b border-gray-800/60">
              <Calculator className="w-5 h-5 text-emerald-400" />
              <h3 className="text-lg font-bold text-white m-0">Tax Inputs</h3>
            </div>

            <form onSubmit={handleCalculate} className="space-y-4">
              <div>
                <label className="block text-gray-400 text-xs uppercase font-semibold mb-1.5">
                  Financial Year
                </label>
                <select
                  value={financialYear}
                  onChange={(e) => setFinancialYear(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors"
                >
                  <option value="2025-2026">2025-2026</option>
                  <option value="2026-2027">2026-2027</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-400 text-xs uppercase font-semibold mb-1.5">
                  Other Taxable Income (BDT)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={otherIncome}
                  onChange={(e) => setOtherIncome(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors"
                  placeholder="e.g. 50000.00"
                />
                <span className="text-[10px] text-gray-500 mt-1 block">
                  Interest, rental yield, dividends or capital gains.
                </span>
              </div>

              <div className="pt-2 flex gap-3">
                <button
                  type="submit"
                  disabled={calculateMutation.isPending}
                  className="flex-1 py-2 px-4 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-900 text-white font-semibold rounded-lg shadow transition-colors cursor-pointer text-center text-sm"
                >
                  {calculateMutation.isPending ? "Calculating..." : "Preview Project"}
                </button>
                <button
                  type="button"
                  onClick={handleSave}
                  disabled={saveMutation.isPending}
                  className="flex items-center justify-center gap-1.5 py-2 px-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white font-semibold rounded-lg shadow transition-colors cursor-pointer text-sm"
                >
                  <Save className="w-4 h-4" />
                  {saveMutation.isPending ? "Saving..." : "Save Run"}
                </button>
              </div>
            </form>
          </div>

          {/* Profile context indicator card */}
          <div className="glass-panel p-6 rounded-xl space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-gray-800/40">
              <Info className="w-4 h-4 text-emerald-400" />
              <h4 className="text-sm font-bold text-white m-0">Profile Rules Applied</h4>
            </div>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Gender Bracket:</span>
                <span className="text-gray-300 font-medium">{employee.gender || "Male"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Local Corporation:</span>
                <span className="text-gray-300 font-medium truncate max-w-[150px]" title={employee.location}>
                  {employee.location || "Dhaka/Chittagong"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Disability status:</span>
                <span className={`font-semibold ${employee.is_disabled ? "text-emerald-400" : "text-gray-500"}`}>
                  {employee.is_disabled ? "Active" : "None"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Freedom Fighter:</span>
                <span className={`font-semibold ${employee.is_freedom_fighter ? "text-emerald-400" : "text-gray-500"}`}>
                  {employee.is_freedom_fighter ? "Active" : "None"}
                </span>
              </div>
            </div>
            <p className="text-[10px] text-gray-500 pt-2 border-t border-gray-850 m-0 leading-normal">
              * Brackets and minimum tax options are derived directly from the employee profile. Need updates? Adjust under the Employee Info tab.
            </p>
          </div>
        </div>

        {/* Right Column: Projection breakdown or placeholder */}
        <div className="lg:col-span-8 space-y-6">
          {!calcResult ? (
            <div className="glass-panel p-16 rounded-xl text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto">
                <Calculator className="w-8 h-8 text-emerald-500 animate-pulse" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-bold text-white">No Calculation Previewed</h3>
                <p className="text-gray-400 text-sm max-w-sm mx-auto">
                  Select your parameters and click "Preview Project" or "Save Run" to view detailed slab calculations, rebates, and final payable amounts.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-panel p-4 rounded-xl">
                  <span className="text-gray-500 text-xs block font-medium">Total Taxable Income</span>
                  <span className="text-xl font-bold text-white block mt-1">
                    ৳ {formatCurrency(calcResult.summary.total_taxable_income)}
                  </span>
                  <span className="text-[10px] text-gray-400 mt-1 block">
                    Salary (Exempted: ৳{formatCurrency(calcResult.summary.exempted_salary)})
                  </span>
                </div>
                <div className="glass-panel p-4 rounded-xl">
                  <span className="text-gray-500 text-xs block font-medium">Tax Rebate Allowed</span>
                  <span className="text-xl font-bold text-emerald-400 block mt-1">
                    ৳ {formatCurrency(calcResult.summary.investment_rebate)}
                  </span>
                  <span className="text-[10px] text-gray-400 mt-1 block">
                    {financialYear === "2024-2025" ? 15 : 10}% of ৳{formatCurrency(calcResult.summary.eligible_investment)} eligible (Total: ৳{formatCurrency(calcResult.summary.total_invested)})
                  </span>
                </div>
                <div className="glass-panel p-4 rounded-xl">
                  <span className="text-gray-500 text-xs block font-medium">Final Net Tax</span>
                  <span className="text-xl font-bold text-white block mt-1">
                    ৳ {formatCurrency(calcResult.summary.net_tax)}
                  </span>
                  <span className="text-[10px] text-gray-400 mt-1 block">
                    Gross: ৳{formatCurrency(calcResult.summary.gross_tax)} (Min Tax: ৳{formatCurrency(calcResult.summary.minimum_tax)})
                  </span>
                </div>
              </div>

              {/* Refund / Payable banner */}
              <div
                className={`p-5 rounded-xl border flex items-center justify-between gap-4 ${calcResult.summary.final_payable < 0
                    ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                    : calcResult.summary.final_payable > 0
                      ? "bg-rose-500/10 border-rose-500/20 text-rose-400"
                      : "bg-gray-800/40 border-gray-800/60 text-gray-300"
                  }`}
              >
                <div>
                  <h4 className="font-bold text-base m-0 text-white">
                    {calcResult.summary.final_payable < 0
                      ? "Tax Refund Expected"
                      : calcResult.summary.final_payable > 0
                        ? "Tax Payable Outstanding"
                        : "Balanced Tax Status"}
                  </h4>
                  <p className="text-xs text-gray-400 m-0 mt-0.5">
                    Adjusted with Monthly TDS (৳{formatCurrency(calcResult.summary.tds_salary)}) & Advance Tax paid (৳{formatCurrency(calcResult.summary.ait_paid)})
                  </p>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-xs text-gray-500 block uppercase font-bold">Amount Due</span>
                  <span className="text-2xl font-extrabold block">
                    ৳ {formatCurrency(Math.abs(calcResult.summary.final_payable))}
                  </span>
                </div>
              </div>

              {/* Rebate Advisor banner */}
              {(() => {
                const totalTaxable = Number(calcResult.summary.total_taxable_income) || 0;
                const currentInvested = Number(calcResult.summary.total_invested) || 0;
                const isOldYear = financialYear === "2024-2025";
                const rebateRate = isOldYear ? 0.15 : 0.10;
                const investCap = isOldYear ? 6666666.67 : 7500000.00;
                const rebateCap = isOldYear ? 1000000 : 750000;

                const maxInvestLimit = Math.min(totalTaxable * 0.20, investCap);
                const currentRebate = Number(calcResult.summary.investment_rebate) || 0;
                const maxRebateCap = Math.min(totalTaxable * 0.03, rebateCap);
                const remainingRebateCap = Math.max(0, maxRebateCap - currentRebate);
                const remainingToInvest = Math.max(0, maxInvestLimit - currentInvested);

                if (remainingToInvest > 100 && remainingRebateCap > 1 && totalTaxable > 0) {
                  const possibleExtraRebate = Math.min(remainingToInvest * rebateRate, remainingRebateCap);
                  return (
                    <div className="glass-panel p-5 rounded-xl border border-emerald-500/20 bg-gradient-to-r from-emerald-950/10 to-gray-950 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                      <div className="space-y-1">
                        <h4 className="text-sm font-bold text-emerald-400 m-0 flex items-center gap-1.5">
                          <span>💡</span> Smart Tax Rebate Advisor
                        </h4>
                        <p className="text-xs text-gray-400 leading-normal m-0 max-w-xl">
                          You haven't maxed out your eligible tax-free investment limit yet. If you invest an additional <span className="text-white font-bold">৳{formatCurrency(remainingToInvest)}</span> in eligible schemes (e.g. DPS, Mutual Funds, Sanchayapatra) before June 30th, you will save an additional <span className="text-emerald-400 font-bold">৳{formatCurrency(possibleExtraRebate)}</span> in taxes!
                        </p>
                      </div>
                      <button
                        onClick={onNavigateToInvestments}
                        className="py-1.5 px-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 font-semibold rounded-lg text-xs transition-colors cursor-pointer border border-emerald-500/30 shrink-0 self-end sm:self-center"
                      >
                        Add Investments
                      </button>
                    </div>
                  );
                }
                return null;
              })()}

              {/* Slabs Breakdown Table */}
              <div className="glass-panel p-6 rounded-xl space-y-4">
                <h4 className="text-sm font-bold text-white m-0 flex items-center gap-2">
                  <Coins className="w-4 h-4 text-emerald-400" />
                  Slab-by-Slab Breakdown (Act 2023)
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-gray-800/60 text-gray-500 font-semibold">
                        <th className="py-2.5">Slab Description</th>
                        <th className="py-2.5 text-center">Tax Rate</th>
                        <th className="py-2.5 text-right">Taxable Amount</th>
                        <th className="py-2.5 text-right">Tax Liability</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/40 text-gray-300">
                      {calcResult.slabs.map((s: any, idx: number) => (
                        <tr key={idx} className="hover:bg-gray-800/20">
                          <td className="py-3 font-medium">{s.slab_name}</td>
                          <td className="py-3 text-center">
                            <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">
                              {(s.tax_rate * 100).toFixed(0)}%
                            </span>
                          </td>
                          <td className="py-3 text-right font-mono">৳{formatCurrency(s.taxable_amount)}</td>
                          <td className="py-3 text-right font-mono text-emerald-400">৳{formatCurrency(s.tax_amount)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* History section */}
      {employee && (
        <div className="glass-panel p-6 rounded-xl space-y-6">
          <div className="flex items-center gap-2 pb-3 border-b border-gray-800/60">
            <History className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-bold text-white m-0">Calculation Runs History</h3>
          </div>

          {isHistoryLoading ? (
            <p className="text-gray-500 text-xs">Loading history...</p>
          ) : history.length === 0 ? (
            <p className="text-gray-500 text-xs m-0">No calculation runs saved yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-gray-800/60 text-gray-500 font-semibold">
                    <th className="py-2.5">Date Saved</th>
                    <th className="py-2.5">Financial Year</th>
                    <th className="py-2.5 text-right">Taxable Income</th>
                    <th className="py-2.5 text-right">Investment Rebate</th>
                    <th className="py-2.5 text-right">Net Tax</th>
                    <th className="py-2.5 text-right">Final Payable</th>
                    <th className="py-2.5 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/40 text-gray-300">
                  {history.map((h: any) => (
                    <tr key={h.id} className="hover:bg-gray-800/20">
                      <td className="py-3">
                        {new Date(h.created_at).toLocaleDateString("en-US", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit"
                        })}
                      </td>
                      <td className="py-3 font-semibold">{h.financial_year}</td>
                      <td className="py-3 text-right font-mono">৳{formatCurrency(h.total_taxable_income)}</td>
                      <td className="py-3 text-right font-mono text-emerald-400">৳{formatCurrency(h.investment_rebate)}</td>
                      <td className="py-3 text-right font-mono">৳{formatCurrency(h.net_tax)}</td>
                      <td className="py-3 text-right font-mono font-bold">
                        <span
                          className={
                            h.final_payable < 0
                              ? "text-emerald-400"
                              : h.final_payable > 0
                                ? "text-rose-400"
                                : "text-gray-300"
                          }
                        >
                          ৳{formatCurrency(h.final_payable)}
                        </span>
                      </td>
                      <td className="py-3 text-center">
                        <button
                          onClick={() => handleViewReturn(h.id)}
                          className="p-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded transition-colors cursor-pointer mr-2"
                          title="View NBR Return Form"
                        >
                          <FileText className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm("Are you sure you want to delete this calculation run?")) {
                              deleteMutation.mutate(h.id);
                            }
                          }}
                          disabled={deleteMutation.isPending}
                          className="p-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded transition-colors cursor-pointer disabled:opacity-50"
                          title="Delete run"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
