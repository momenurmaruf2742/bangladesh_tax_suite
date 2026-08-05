import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import {
    Save,
    Plus,
    Trash2,
    AlertCircle,
    Calendar,
    Layers,
    Percent,
    TrendingDown,
    Building
} from "lucide-react";

interface TaxRuleResponse {
    id: string;
    financial_year: string;
    exemption_rate: number;
    exemption_max: number;
    dps_max: number;
    rebate_rate: number;
    income_rebate_limit_rate: number;
    max_rebate_cap: number;
    max_eligible_invest_rate: number;
    max_eligible_invest_cap: number;
    thresholds: Record<string, number>;
    slabs: Array<[string, number | null, number]>;
    minimum_tax_location_based: boolean;
    minimum_tax: Record<string, number>;
}

export const RulesManagerPanel: React.FC = () => {
    const queryClient = useQueryClient();
    const [selectedYear, setSelectedYear] = useState<string>("");
    const [isAddingYear, setIsAddingYear] = useState(false);
    const [newYearName, setNewYearName] = useState("");
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    // Form State
    const [exemptionRate, setExemptionRate] = useState<string>("3.0");
    const [exemptionMax, setExemptionMax] = useState<string>("450000");
    const [dpsMax, setDpsMax] = useState<string>("120000");
    const [rebateRate, setRebateRate] = useState<string>("0.15");
    const [incomeRebateLimitRate, setIncomeRebateLimitRate] = useState<string>("0.03");
    const [maxRebateCap, setMaxRebateCap] = useState<string>("1000000");
    const [maxEligibleInvestRate, setMaxEligibleInvestRate] = useState<string>("0.20");
    const [maxEligibleInvestCap, setMaxEligibleInvestCap] = useState<string>("6666666.67");

    // Thresholds state
    const [thresholds, setThresholds] = useState<Array<{ key: string; val: string }>>([]);

    // Minimum Tax Tiers state
    const [minimumTaxes, setMinimumTaxes] = useState<Array<{ key: string; val: string }>>([]);
    const [minTaxLocationBased, setMinTaxLocationBased] = useState(true);

    // Slabs state: each row is [name, limit, rate (represented as decimal, e.g. 0.05 = 5%)]
    const [slabs, setSlabs] = useState<Array<{ name: string; limit: string; rate: string }>>([]);

    // 1. Fetch all configured rules
    const { data: rulesList = [], isLoading: isRulesLoading } = useQuery<TaxRuleResponse[]>({
        queryKey: ["taxRules"],
        queryFn: async () => {
            const res = await api.get("/taxes/rules");
            return res.data;
        }
    });

    // Automatically select the first available year if none is selected
    useEffect(() => {
        if (rulesList.length > 0 && !selectedYear) {
            // Find latest year if possible or default to first
            const sorted = [...rulesList].sort((a, b) => b.financial_year.localeCompare(a.financial_year));
            setSelectedYear(sorted[0].financial_year);
        }
    }, [rulesList, selectedYear]);

    // Load details of the selected rules year into form state
    const activeRule = rulesList.find((r) => r.financial_year === selectedYear);

    useEffect(() => {
        if (activeRule) {
            setExemptionRate(String(activeRule.exemption_rate));
            setExemptionMax(String(activeRule.exemption_max));
            setDpsMax(String(activeRule.dps_max));
            setRebateRate(String(activeRule.rebate_rate));
            setIncomeRebateLimitRate(String(activeRule.income_rebate_limit_rate));
            setMaxRebateCap(String(activeRule.max_rebate_cap));
            setMaxEligibleInvestRate(String(activeRule.max_eligible_invest_rate));
            setMaxEligibleInvestCap(String(activeRule.max_eligible_invest_cap));
            setMinTaxLocationBased(activeRule.minimum_tax_location_based);

            // Threshholds map to lists
            setThresholds(
                Object.entries(activeRule.thresholds).map(([key, val]) => ({
                    key,
                    val: String(val)
                }))
            );

            // Slabs map to lists
            setSlabs(
                activeRule.slabs.map(([name, limit, rate]) => ({
                    name,
                    limit: limit !== null ? String(limit) : "",
                    rate: String(rate)
                }))
            );

            // Min taxes map to lists
            setMinimumTaxes(
                Object.entries(activeRule.minimum_tax).map(([key, val]) => ({
                    key,
                    val: String(val)
                }))
            );
        }
    }, [activeRule]);

    // Mutations
    const updateRuleMutation = useMutation({
        mutationFn: async (payload: any) => {
            const res = await api.put(`/taxes/rules/${selectedYear}`, payload);
            return res.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["taxRules"] });
            triggerSuccess("Tax rules updated successfully!");
        },
        onError: (err: any) => {
            setErrorMessage(err.response?.data?.detail || "Failed to update tax rules.");
        }
    });

    const createRuleMutation = useMutation({
        mutationFn: async (payload: any) => {
            const res = await api.post("/taxes/rules", payload);
            return res.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["taxRules"] });
            setIsAddingYear(false);
            setSelectedYear(data.financial_year);
            setNewYearName("");
            triggerSuccess(`Tax rules for ${data.financial_year} created successfully.`);
        },
        onError: (err: any) => {
            setErrorMessage(err.response?.data?.detail || "Failed to create tax rules.");
        }
    });

    const deleteRuleMutation = useMutation({
        mutationFn: async (year: string) => {
            await api.delete(`/taxes/rules/${year}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["taxRules"] });
            setSelectedYear("");
            triggerSuccess("Ruleset deleted successfully.");
        },
        onError: (err: any) => {
            setErrorMessage(err.response?.data?.detail || "Failed to delete ruleset.");
        }
    });

    const triggerSuccess = (msg: string) => {
        setSuccessMessage(msg);
        setErrorMessage(null);
        setTimeout(() => setSuccessMessage(null), 4000);
    };

    const handleSave = (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedYear) return;

        // Build payload
        const payload = buildPayload();
        updateRuleMutation.mutate(payload);
    };

    const handleCreateYear = () => {
        if (!newYearName.trim()) {
            setErrorMessage("Please enter a financial year (e.g. 2026-2027)");
            return;
        }

        // Validate year format
        const yearRegex = /^\d{4}-\d{4}$/;
        if (!yearRegex.test(newYearName)) {
            setErrorMessage("Invalid format. Must be YYYY-YYYY (e.g. 2026-2027).");
            return;
        }

        const payload = {
            financial_year: newYearName,
            exemption_rate: parseFloat(exemptionRate) || 3.0,
            exemption_max: parseFloat(exemptionMax) || 0,
            dps_max: parseFloat(dpsMax) || 0,
            rebate_rate: parseFloat(rebateRate) || 0.15,
            income_rebate_limit_rate: parseFloat(incomeRebateLimitRate) || 0.03,
            max_rebate_cap: parseFloat(maxRebateCap) || 0,
            max_eligible_invest_rate: parseFloat(maxEligibleInvestRate) || 0.20,
            max_eligible_invest_cap: parseFloat(maxEligibleInvestCap) || 0,
            thresholds: Object.fromEntries(
                thresholds.map((t) => [t.key, parseFloat(t.val) || 0])
            ),
            slabs: slabs.map((s) => [
                s.name,
                s.limit !== "" ? parseFloat(s.limit) : null,
                parseFloat(s.rate) || 0
            ]),
            minimum_tax_location_based: minTaxLocationBased,
            minimum_tax: Object.fromEntries(
                minimumTaxes.map((m) => [m.key, parseFloat(m.val) || 0])
            )
        };

        createRuleMutation.mutate(payload);
    };

    const buildPayload = () => {
        return {
            exemption_rate: parseFloat(exemptionRate) || 3.0,
            exemption_max: parseFloat(exemptionMax) || 0,
            dps_max: parseFloat(dpsMax) || 0,
            rebate_rate: parseFloat(rebateRate) || 0.15,
            income_rebate_limit_rate: parseFloat(incomeRebateLimitRate) || 0.03,
            max_rebate_cap: parseFloat(maxRebateCap) || 0,
            max_eligible_invest_rate: parseFloat(maxEligibleInvestRate) || 0.20,
            max_eligible_invest_cap: parseFloat(maxEligibleInvestCap) || 0,
            thresholds: Object.fromEntries(
                thresholds.map((t) => [t.key, parseFloat(t.val) || 0])
            ),
            slabs: slabs.map((s) => [
                s.name,
                s.limit !== "" ? parseFloat(s.limit) : null,
                parseFloat(s.rate) || 0
            ]),
            minimum_tax_location_based: minTaxLocationBased,
            minimum_tax: Object.fromEntries(
                minimumTaxes.map((m) => [m.key, parseFloat(m.val) || 0])
            )
        };
    };

    const handleAddSlab = () => {
        setSlabs([...slabs, { name: "New progresive slab", limit: "", rate: "0.0" }]);
    };

    const handleRemoveSlab = (idx: number) => {
        setSlabs(slabs.filter((_, i) => i !== idx));
    };

    const handleSlabChange = (idx: number, field: "name" | "limit" | "rate", value: string) => {
        const updated = [...slabs];
        updated[idx] = { ...updated[idx], [field]: value };
        setSlabs(updated);
    };

    const handleThresholdChange = (idx: number, value: string) => {
        const updated = [...thresholds];
        updated[idx] = { ...updated[idx], val: value };
        setThresholds(updated);
    };

    const handleMinTaxChange = (idx: number, value: string) => {
        const updated = [...minimumTaxes];
        updated[idx] = { ...updated[idx], val: value };
        setMinimumTaxes(updated);
    };

    const handleDeleteRuleset = () => {
        if (!selectedYear) return;
        if (confirm(`Are you sure you want to delete all dynamic tax rules for financial year ${selectedYear}? The system will fall back to hardcoded defaults.`)) {
            deleteRuleMutation.mutate(selectedYear);
        }
    };

    if (isRulesLoading) {
        return (
            <div className="flex justify-center items-center py-10 text-gray-400">
                <span className="animate-pulse">Loading NBR Rules Engine Registry...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Settings Year Controller */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 bg-gray-900/60 border border-gray-800 rounded-xl gap-4">
                <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-purple-400" />
                    <div>
                        <label className="block text-[10px] text-gray-500 font-bold uppercase">Configure Tax Year</label>
                        <select
                            value={selectedYear}
                            onChange={(e) => {
                                setSelectedYear(e.target.value);
                                setIsAddingYear(false);
                            }}
                            className="mt-0.5 bg-gray-950 border border-gray-800 text-white rounded px-2 py-1 text-xs focus:ring-1 focus:ring-purple-500 focus:outline-none"
                        >
                            {rulesList.map((r) => (
                                <option key={r.id} value={r.financial_year}>
                                    Financial Year {r.financial_year}
                                </option>
                            ))}
                            {rulesList.length === 0 && <option value="">-- No DB Rules Seeded --</option>}
                        </select>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    {selectedYear && (
                        <button
                            onClick={handleDeleteRuleset}
                            disabled={deleteRuleMutation.isPending}
                            className="py-1.5 px-3 bg-red-950/20 hover:bg-red-950/40 text-red-400 border border-red-500/10 text-xs font-semibold rounded transition-colors cursor-pointer"
                        >
                            Delete Year
                        </button>
                    )}

                    <button
                        onClick={() => setIsAddingYear(!isAddingYear)}
                        className="py-1.5 px-3 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded transition-colors cursor-pointer"
                    >
                        {isAddingYear ? "View Current" : "Add Tax Year"}
                    </button>
                </div>
            </div>

            {/* Error and Success Notices */}
            {errorMessage && (
                <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-200 text-xs rounded-lg flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{errorMessage}</span>
                </div>
            )}

            {successMessage && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-200 text-xs rounded-lg flex items-center gap-2">
                    <Layers className="w-4 h-4 shrink-0 text-emerald-400" />
                    <span>{successMessage}</span>
                </div>
            )}

            {/* Add Year Form Panel */}
            {isAddingYear ? (
                <div className="glass-panel p-6 rounded-xl border border-purple-500/20 space-y-4">
                    <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2">
                        <span>➕ Create Dynamic Tax Rules Year</span>
                    </h3>
                    <p className="text-xs text-gray-400 m-0">
                        Initialize values for a new financial year. Fields will default prepopulate from the configuration of the year currently active on the left.
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                        <div>
                            <label className="block text-gray-400 text-xs mb-1">Financial Year Name</label>
                            <input
                                type="text"
                                placeholder="e.g. 2026-2027"
                                value={newYearName}
                                onChange={(e) => setNewYearName(e.target.value)}
                                className="w-full px-3 py-2 bg-gray-950/60 border border-gray-800 rounded text-white text-xs placeholder-gray-600 focus:outline-none focus:border-purple-500"
                            />
                        </div>
                        <div className="flex items-end">
                            <button
                                type="button"
                                onClick={handleCreateYear}
                                disabled={createRuleMutation.isPending}
                                className="w-full py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 text-white font-bold text-xs rounded shadow transition-colors cursor-pointer"
                            >
                                {createRuleMutation.isPending ? "Creating..." : "Confirm & Save Ruleset"}
                            </button>
                        </div>
                    </div>
                </div>
            ) : activeRule ? (
                /* Visual Rules Editor Form */
                <form onSubmit={handleSave} className="space-y-6">
                    {/* Section 1: Rebates & Investment caps */}
                    <div className="glass-panel p-6 rounded-xl border border-gray-850 space-y-4">
                        <h3 className="text-sm font-extrabold text-white uppercase tracking-wider flex items-center gap-2 border-b border-gray-800 pb-2">
                            <Percent className="w-4 h-4 text-emerald-400" /> Section 78 Rebate & Exemption Settings
                        </h3>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                            <div>
                                <label className="block text-gray-400 mb-1">Rebate rate (%)</label>
                                <div className="flex bg-gray-950/60 border border-gray-800 rounded overflow-hidden">
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={rebateRate}
                                        onChange={(e) => setRebateRate(e.target.value)}
                                        className="w-full px-2 py-1.5 bg-transparent text-white focus:outline-none"
                                    />
                                    <span className="bg-gray-900 border-l border-gray-850 px-2.5 flex items-center text-gray-500">rate</span>
                                </div>
                            </div>

                            <div>
                                <label className="block text-gray-400 mb-1">Max Rebate Cap (BDT)</label>
                                <input
                                    type="number"
                                    value={maxRebateCap}
                                    onChange={(e) => setMaxRebateCap(e.target.value)}
                                    className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-800 rounded text-white focus:outline-none focus:border-emerald-500"
                                />
                            </div>

                            <div>
                                <label className="block text-gray-400 mb-1">Max Invest. Rate (%)</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={maxEligibleInvestRate}
                                    onChange={(e) => setMaxEligibleInvestRate(e.target.value)}
                                    className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-800 rounded text-white focus:outline-none focus:border-emerald-500"
                                />
                            </div>

                            <div>
                                <label className="block text-gray-400 mb-1">Max Allowable Cap (BDT)</label>
                                <input
                                    type="number"
                                    value={maxEligibleInvestCap}
                                    onChange={(e) => setMaxEligibleInvestCap(e.target.value)}
                                    className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-850 rounded text-white focus:outline-none focus:border-emerald-500"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs pt-1">
                            <div>
                                <label className="block text-gray-400 mb-1">Exemption Divider</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={exemptionRate}
                                    onChange={(e) => setExemptionRate(e.target.value)}
                                    className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-800 rounded text-white focus:outline-none focus:border-emerald-500"
                                />
                                <span className="text-[10px] text-gray-500 mt-0.5 block">e.g. 3.0 means 1/3 salary exempt</span>
                            </div>

                            <div>
                                <label className="block text-gray-400 mb-1">Max Exemption Cap (BDT)</label>
                                <input
                                    type="number"
                                    value={exemptionMax}
                                    onChange={(e) => setExemptionMax(e.target.value)}
                                    className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-800 rounded text-white focus:outline-none focus:border-emerald-500"
                                />
                            </div>

                            <div>
                                <label className="block text-gray-400 mb-1">Max DPS Eligible / Year</label>
                                <input
                                    type="number"
                                    value={dpsMax}
                                    onChange={(e) => setDpsMax(e.target.value)}
                                    className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-800 rounded text-white focus:outline-none focus:border-emerald-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Section 2: General & Special Thresholds */}
                    <div className="glass-panel p-6 rounded-xl border border-gray-850 space-y-4">
                        <h3 className="text-sm font-extrabold text-white uppercase tracking-wider flex items-center gap-2 border-b border-gray-800 pb-2">
                            <TrendingDown className="w-4 h-4 text-amber-500" /> Individual Tax-Free Thresholds
                        </h3>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                            {thresholds.map((t, idx) => (
                                <div key={t.key}>
                                    <label className="block text-gray-400 mb-1">{t.key} Category Limit (BDT)</label>
                                    <input
                                        type="number"
                                        value={t.val}
                                        onChange={(e) => handleThresholdChange(idx, e.target.value)}
                                        className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-800 rounded text-white focus:outline-none focus:border-amber-500 font-semibold"
                                    />
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Section 3: Progressive Slabs Details */}
                    <div className="glass-panel p-6 rounded-xl border border-gray-850 space-y-4">
                        <div className="flex justify-between items-center border-b border-gray-800 pb-2">
                            <h3 className="text-sm font-extrabold text-white uppercase tracking-wider flex items-center gap-2 m-0">
                                <Layers className="w-4 h-4 text-purple-400" /> Progressive Tax Slab brackets
                            </h3>
                            <button
                                type="button"
                                onClick={handleAddSlab}
                                className="py-1 px-2.5 bg-purple-900/30 hover:bg-purple-600/30 text-purple-400 border border-purple-500/20 text-xs font-semibold rounded flex items-center gap-1 cursor-pointer"
                            >
                                <Plus className="w-3.5 h-3.5" /> Add Slab
                            </button>
                        </div>

                        <div className="space-y-3 pt-1">
                            <div className="hidden sm:grid sm:grid-cols-12 gap-3 text-[10px] text-gray-500 uppercase font-bold px-2">
                                <div className="col-span-5">Slab Description / Name</div>
                                <div className="col-span-4">Bracket Limit Amount (BDT)</div>
                                <div className="col-span-2">Tax Rate Decimal</div>
                                <div className="col-span-1 text-center">Delete</div>
                            </div>

                            {slabs.map((slab, idx) => (
                                <div key={idx} className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-center bg-gray-950/30 p-2 rounded border border-gray-900">
                                    <div className="col-span-5">
                                        <input
                                            type="text"
                                            placeholder="e.g. Next 3,00,000 BDT or Balance"
                                            value={slab.name}
                                            onChange={(e) => handleSlabChange(idx, "name", e.target.value)}
                                            className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-850 rounded text-white text-xs focus:outline-none"
                                        />
                                    </div>

                                    <div className="col-span-4 flex items-center gap-2">
                                        <input
                                            type="number"
                                            placeholder="e.g. 300000"
                                            value={slab.limit}
                                            disabled={slab.limit === "" && idx === slabs.length - 1 && slab.name.toLowerCase().includes("balance")}
                                            onChange={(e) => handleSlabChange(idx, "limit", e.target.value)}
                                            className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-850 rounded text-white text-xs focus:outline-none disabled:bg-gray-900/50 disabled:text-gray-500"
                                        />
                                        {idx === slabs.length - 1 && (
                                            <label className="text-[10px] text-purple-400 font-semibold shrink-0 cursor-pointer flex items-center gap-1 select-none">
                                                <input
                                                    type="checkbox"
                                                    checked={slab.limit === ""}
                                                    onChange={(e) => handleSlabChange(idx, "limit", e.target.checked ? "" : "500000")}
                                                    className="rounded bg-gray-950 border-gray-850 cursor-pointer"
                                                />
                                                <span>No Limit</span>
                                            </label>
                                        )}
                                    </div>

                                    <div className="col-span-2">
                                        <div className="flex bg-gray-950/60 border border-gray-850 rounded overflow-hidden">
                                            <input
                                                type="number"
                                                step="0.01"
                                                placeholder="e.g. 0.10"
                                                value={slab.rate}
                                                onChange={(e) => handleSlabChange(idx, "rate", e.target.value)}
                                                className="w-full px-2 py-1.5 bg-transparent text-white text-xs focus:outline-none"
                                            />
                                            <span className="bg-gray-900 px-2 py-1.5 text-[10px] text-gray-500 font-semibold">{Math.round((parseFloat(slab.rate) || 0) * 100)}%</span>
                                        </div>
                                    </div>

                                    <div className="col-span-1 text-center">
                                        <button
                                            type="button"
                                            onClick={() => handleRemoveSlab(idx)}
                                            disabled={slabs.length <= 2}
                                            className="p-1 px-2.5 bg-red-950/20 hover:bg-red-950/30 text-rose-500 border border-rose-500/10 rounded transition-colors disabled:opacity-40 cursor-pointer"
                                        >
                                            <Trash2 className="w-3.5 h-3.5" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Section 4: Minimum Taxes */}
                    <div className="glass-panel p-6 rounded-xl border border-gray-850 space-y-4">
                        <h3 className="text-sm font-extrabold text-white uppercase tracking-wider flex items-center gap-2 border-b border-gray-800 pb-2">
                            <Building className="w-4 h-4 text-blue-400" /> Minimum Tax Rates (Geographic Tiers)
                        </h3>

                        <div className="flex items-center gap-2.5 text-xs py-1">
                            <input
                                type="checkbox"
                                id="minTaxLoc"
                                checked={minTaxLocationBased}
                                onChange={(e) => setMinTaxLocationBased(e.target.checked)}
                                className="w-4 h-4 rounded text-blue-500 bg-gray-950/60 border-gray-850 focus:ring-offset-0 focus:ring-blue-500 cursor-pointer"
                            />
                            <label htmlFor="minTaxLoc" className="text-gray-300 font-medium cursor-pointer">
                                Apply location-specific minimum tax (Act 2023 Rules)
                            </label>
                        </div>

                        {minTaxLocationBased && (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs pt-1">
                                {minimumTaxes.map((m, idx) => (
                                    <div key={m.key}>
                                        <label className="block text-gray-400 mb-1">{m.key} Tier Fee (BDT)</label>
                                        <input
                                            type="number"
                                            value={m.val}
                                            onChange={(e) => handleMinTaxChange(idx, e.target.value)}
                                            className="w-full px-2.5 py-1.5 bg-gray-950/60 border border-gray-800 rounded text-white focus:outline-none focus:border-blue-500 font-semibold"
                                        />
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Submit Action Buttons */}
                    <div className="flex gap-4">
                        <button
                            type="submit"
                            disabled={updateRuleMutation.isPending}
                            className="py-2.5 px-6 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 text-white font-extrabold text-xs uppercase tracking-wider rounded-lg shadow-lg flex items-center gap-2 transition-colors cursor-pointer"
                        >
                            <Save className="w-4 h-4" /> {updateRuleMutation.isPending ? "Saving..." : "Save Calculation Rules"}
                        </button>
                    </div>
                </form>
            ) : (
                <div className="p-6 bg-yellow-500/10 border border-yellow-500/20 text-yellow-300 text-xs rounded-xl flex items-center gap-2">
                    <AlertCircle className="w-4.5 h-4.5 shrink-0" />
                    <span>No rules found or configured for the selected tax year. Click "Add Tax Year" above to start configuring.</span>
                </div>
            )}
        </div>
    );
};
