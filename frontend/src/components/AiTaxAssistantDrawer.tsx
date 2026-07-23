import React, { useState } from "react";
import { Bot, Send, X, Sparkles, BookOpen, CheckCircle2, Loader2 } from "lucide-react";
import { api } from "../services/api";

interface Message {
  id: string;
  sender: "user" | "ai";
  text: string;
  key_points?: string[];
  reference_laws?: string[];
}

export const AiTaxAssistantDrawer: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose
}) => {
  const [inputPrompt, setInputPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "ai",
      text: "Hello! I am your AI Tax Assistant grounded in the Bangladesh Income Tax Act 2023. Ask me anything about tax-free limits, DPS rebates, salary exemptions, or AIT credits!",
      key_points: [
        "Ask: What is the DPS rebate limit?",
        "Ask: What is the general tax free threshold?",
        "Ask: How are salary allowances exempted?"
      ],
      reference_laws: ["Income Tax Act 2023", "Finance Act 2024"]
    }
  ]);

  if (!isOpen) return null;

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputPrompt.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: inputPrompt
    };

    setMessages((prev) => [...prev, userMsg]);
    const promptToSend = inputPrompt;
    setInputPrompt("");
    setLoading(true);

    try {
      const res = await api.post("/ai/tax-chat", { prompt: promptToSend });
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: res.data.reply,
        key_points: res.data.key_points,
        reference_laws: res.data.reference_laws
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: "Sorry, I encountered an issue connecting to the Tax AI service. Please try asking again."
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[450px] bg-[#0d1527] border-l border-emerald-500/20 shadow-2xl z-50 flex flex-col justify-between">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 bg-gradient-to-r from-emerald-950/60 via-gray-900 to-gray-950 flex justify-between items-center">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-1.5 m-0">
              AI Tax Assistant <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            </h3>
            <span className="text-[10px] text-emerald-400 font-medium">Income Tax Act 2023 Rules Engine</span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[88%] p-3.5 rounded-2xl text-xs space-y-2 ${
                msg.sender === "user"
                  ? "bg-emerald-600 text-white rounded-br-none font-medium"
                  : "bg-gray-900/90 text-gray-200 border border-gray-800 rounded-bl-none shadow-md"
              }`}
            >
              <p className="m-0 leading-relaxed">{msg.text}</p>

              {msg.key_points && msg.key_points.length > 0 && (
                <div className="border-t border-gray-800/80 pt-2 space-y-1">
                  <span className="text-[10px] font-bold text-emerald-400 block uppercase">Key Highlights:</span>
                  {msg.key_points.map((kp, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 text-[11px] text-gray-300">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{kp}</span>
                    </div>
                  ))}
                </div>
              )}

              {msg.reference_laws && msg.reference_laws.length > 0 && (
                <div className="flex flex-wrap gap-1 pt-1">
                  {msg.reference_laws.map((law, idx) => (
                    <span
                      key={idx}
                      className="text-[9px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-900/40 font-mono"
                    >
                      <BookOpen className="w-2.5 h-2.5 inline mr-1" />
                      {law}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-900/90 p-3 rounded-2xl border border-gray-800 text-xs text-gray-400 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
              <span>Searching Tax Act 2023 regulations...</span>
            </div>
          </div>
        )}
      </div>

      {/* Quick Prompts & Input Area */}
      <div className="p-3 border-t border-gray-800/80 bg-gray-950/80 space-y-2">
        <div className="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar text-[10px]">
          <button
            onClick={() => { setInputPrompt("What is the DPS rebate limit?"); }}
            className="px-2.5 py-1 rounded-full bg-gray-900 hover:bg-gray-800 text-emerald-300 border border-gray-800 shrink-0 transition-colors cursor-pointer"
          >
            💡 DPS Cap
          </button>
          <button
            onClick={() => { setInputPrompt("What is the tax free threshold?"); }}
            className="px-2.5 py-1 rounded-full bg-gray-900 hover:bg-gray-800 text-emerald-300 border border-gray-800 shrink-0 transition-colors cursor-pointer"
          >
            🏛️ Tax-Free Limits
          </button>
          <button
            onClick={() => { setInputPrompt("How are salary allowances exempted?"); }}
            className="px-2.5 py-1 rounded-full bg-gray-900 hover:bg-gray-800 text-emerald-300 border border-gray-800 shrink-0 transition-colors cursor-pointer"
          >
            💵 Salary Exemption
          </button>
        </div>

        <form onSubmit={handleSend} className="flex gap-2">
          <input
            type="text"
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            placeholder="Ask about Bangladesh Tax Act 2023..."
            className="flex-1 bg-gray-900 border border-gray-800 rounded-xl px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition-all"
          />
          <button
            type="submit"
            disabled={loading || !inputPrompt.trim()}
            className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold flex items-center justify-center transition-all cursor-pointer shadow-lg shadow-emerald-950"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
