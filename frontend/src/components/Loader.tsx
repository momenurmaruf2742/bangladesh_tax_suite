import React from "react";

export const Loader: React.FC<{ fullPage?: boolean }> = ({ fullPage = false }) => {
  const spinner = (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full border-4 border-emerald-500/20"></div>
        <div className="absolute inset-0 rounded-full border-4 border-t-emerald-500 border-r-transparent border-b-transparent border-l-transparent animate-spin"></div>
      </div>
      <div className="text-emerald-500 font-semibold tracking-wider text-sm uppercase animate-pulse-soft">
        Tax Suite Loading...
      </div>
    </div>
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-premium-dark z-50">
        {spinner}
      </div>
    );
  }

  return <div className="flex items-center justify-center p-8">{spinner}</div>;
};
