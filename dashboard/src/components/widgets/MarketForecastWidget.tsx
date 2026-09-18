"use client"

export function MarketForecastWidget() {
  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Market Price Forecast</h3>
        <span className="text-xs text-blue-400 cursor-pointer hover:underline">View All</span>
      </div>
      <div className="flex-1 p-4 relative">
        <div className="w-full h-full border border-dashed border-white/10 flex items-center justify-center text-white/30 text-sm">
          Line Chart
        </div>
      </div>
    </div>
  )
}
