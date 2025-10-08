//
//  DashboardView.swift
//  Arbitra
//
//  Main dashboard with portfolio overview
//

import SwiftUI
import Charts

struct DashboardView: View {
    @EnvironmentObject var portfolioState: PortfolioState
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Portfolio Summary Cards
                HStack(spacing: 16) {
                    PortfolioCard(
                        title: "Total Value",
                        value: portfolioState.portfolio?.totalValue ?? 0,
                        format: .currency,
                        icon: "dollarsign.circle.fill",
                        color: .blue
                    )
                    
                    PortfolioCard(
                        title: "Daily P/L",
                        value: portfolioState.portfolio?.dailyPnL ?? 0,
                        format: .currency,
                        changePercent: portfolioState.portfolio?.dailyPnLPct,
                        icon: "chart.line.uptrend.xyaxis",
                        color: (portfolioState.portfolio?.dailyPnL ?? 0) >= 0 ? .green : .red
                    )
                    
                    PortfolioCard(
                        title: "Total P/L",
                        value: portfolioState.portfolio?.totalPnL ?? 0,
                        format: .currency,
                        changePercent: portfolioState.portfolio?.totalPnLPct,
                        icon: "chart.bar.fill",
                        color: (portfolioState.portfolio?.totalPnL ?? 0) >= 0 ? .green : .red
                    )
                    
                    PortfolioCard(
                        title: "Cash",
                        value: portfolioState.portfolio?.cash ?? 0,
                        format: .currency,
                        icon: "banknote.fill",
                        color: .purple
                    )
                }
                
                // Performance Chart
                PerformanceChartView(data: portfolioState.performanceHistory)
                    .frame(height: 300)
                
                // Allocation Breakdown
                AllocationBreakdownView(portfolio: portfolioState.portfolio)
                
                // Active Positions List
                if let positions = portfolioState.portfolio?.positions, !positions.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Active Positions (\(positions.count))")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        ForEach(positions) { position in
                            PositionRowView(position: position)
                        }
                    }
                    .padding()
                    .background(Color(.windowBackgroundColor))
                    .cornerRadius(12)
                }
                
                // Recent Trades
                if !portfolioState.recentTrades.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Recent Trades")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        ForEach(portfolioState.recentTrades.prefix(5)) { trade in
                            RecentTradeRowView(trade: trade)
                        }
                    }
                    .padding()
                    .background(Color(.windowBackgroundColor))
                    .cornerRadius(12)
                }
            }
            .padding()
        }
        .navigationTitle("Dashboard")
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct PortfolioCard: View {
    let title: String
    let value: Decimal
    let format: ValueFormat
    var changePercent: Decimal? = nil
    var icon: String
    var color: Color
    
    enum ValueFormat {
        case currency
        case percent
        case number
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundColor(color)
                
                Spacer()
                
                if let change = changePercent {
                    Text(String(format: "%+.2f%%", Double(truncating: change as NSNumber)))
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(change >= 0 ? .green : .red)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background((change >= 0 ? Color.green : Color.red).opacity(0.1))
                        .cornerRadius(6)
                }
            }
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(formattedValue)
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
        .shadow(color: color.opacity(0.1), radius: 5, x: 0, y: 2)
    }
    
    private var formattedValue: String {
        switch format {
        case .currency:
            return String(format: "$%.2f", Double(truncating: value as NSNumber))
        case .percent:
            return String(format: "%.2f%%", Double(truncating: value as NSNumber))
        case .number:
            return String(format: "%.2f", Double(truncating: value as NSNumber))
        }
    }
}

struct PerformanceChartView: View {
    let data: [PortfolioState.PerformanceDataPoint]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Portfolio Performance")
                .font(.title2)
                .fontWeight(.bold)
            
            if data.isEmpty {
                Text("No performance data available")
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                Chart(data) { point in
                    LineMark(
                        x: .value("Date", point.date),
                        y: .value("Value", Double(truncating: point.portfolioValue as NSNumber))
                    )
                    .foregroundStyle(Color.blue.gradient)
                    
                    AreaMark(
                        x: .value("Date", point.date),
                        y: .value("Value", Double(truncating: point.portfolioValue as NSNumber))
                    )
                    .foregroundStyle(Color.blue.opacity(0.1).gradient)
                }
                .chartXAxis {
                    AxisMarks(values: .automatic) { _ in
                        AxisGridLine()
                        AxisTick()
                        AxisValueLabel(format: .dateTime.month().day())
                    }
                }
                .chartYAxis {
                    AxisMarks(position: .leading)
                }
            }
        }
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
    }
}

struct AllocationBreakdownView: View {
    let portfolio: Portfolio?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Asset Allocation")
                .font(.title2)
                .fontWeight(.bold)
            
            if let portfolio = portfolio {
                let tierAllocations = calculateTierAllocations(portfolio: portfolio)
                
                HStack(spacing: 20) {
                    ForEach(AssetTier.allCases, id: \.self) { tier in
                        VStack(spacing: 8) {
                            Text(tier.displayName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            Text(String(format: "%.1f%%", tierAllocations[tier] ?? 0))
                                .font(.title3)
                                .fontWeight(.bold)
                                .foregroundColor(tierColor(tier))
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(tierColor(tier).opacity(0.1))
                        .cornerRadius(8)
                    }
                }
            }
        }
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
    }
    
    private func calculateTierAllocations(portfolio: Portfolio) -> [AssetTier: Double] {
        var allocations: [AssetTier: Double] = [:]
        let totalValue = Double(truncating: portfolio.totalValue as NSNumber)
        
        for tier in AssetTier.allCases {
            let tierValue = portfolio.positions
                .filter { $0.tier == tier }
                .reduce(0.0) { $0 + Double(truncating: $1.currentValue as NSNumber) }
            
            allocations[tier] = totalValue > 0 ? (tierValue / totalValue) * 100 : 0
        }
        
        return allocations
    }
    
    private func tierColor(_ tier: AssetTier) -> Color {
        switch tier {
        case .foundation: return .blue
        case .growth: return .purple
        case .opportunity: return .orange
        }
    }
}

struct PositionRowView: View {
    let position: Position
    
    var body: some View {
        HStack {
            // Symbol and tier badge
            VStack(alignment: .leading, spacing: 4) {
                Text(position.symbol)
                    .font(.headline)
                    .fontWeight(.bold)
                
                HStack(spacing: 4) {
                    Image(systemName: "tag.fill")
                        .font(.caption2)
                    Text(position.tier.displayName)
                        .font(.caption)
                }
                .foregroundColor(tierColor(position.tier))
            }
            
            Spacer()
            
            // Quantity and price
            VStack(alignment: .trailing, spacing: 4) {
                Text("\(formatDecimal(position.quantity)) @ $\(formatDecimal(position.currentPrice))")
                    .font(.subheadline)
                
                Text("Value: $\(formatDecimal(position.currentValue))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // P/L
            VStack(alignment: .trailing, spacing: 4) {
                Text("$\(formatDecimal(position.unrealizedPnL))")
                    .font(.headline)
                    .foregroundColor(position.unrealizedPnL >= 0 ? .green : .red)
                
                Text(String(format: "%+.2f%%", Double(truncating: position.unrealizedPnLPct as NSNumber)))
                    .font(.caption)
                    .foregroundColor(position.unrealizedPnL >= 0 ? .green : .red)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(8)
    }
    
    private func tierColor(_ tier: AssetTier) -> Color {
        switch tier {
        case .foundation: return .blue
        case .growth: return .purple
        case .opportunity: return .orange
        }
    }
    
    private func formatDecimal(_ value: Decimal) -> String {
        String(format: "%.2f", Double(truncating: value as NSNumber))
    }
}

struct RecentTradeRowView: View {
    let trade: Trade
    
    var body: some View {
        HStack {
            // Action badge
            Text(trade.action.rawValue)
                .font(.caption)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(trade.action == .buy ? Color.green : Color.red)
                .cornerRadius(6)
            
            // Symbol
            Text(trade.symbol)
                .font(.headline)
            
            Spacer()
            
            // Price
            Text("$\(formatDecimal(trade.entryPrice))")
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            // P/L (if closed)
            if let pnl = trade.pnl, let pnlPct = trade.pnlPct {
                VStack(alignment: .trailing, spacing: 2) {
                    Text("$\(formatDecimal(pnl))")
                        .font(.subheadline)
                        .foregroundColor(pnl >= 0 ? .green : .red)
                    
                    Text(String(format: "%+.2f%%", Double(truncating: pnlPct as NSNumber)))
                        .font(.caption)
                        .foregroundColor(pnl >= 0 ? .green : .red)
                }
            }
            
            // Time
            Text(formatDate(trade.entryTime))
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(8)
    }
    
    private func formatDecimal(_ value: Decimal) -> String {
        String(format: "%.2f", Double(truncating: value as NSNumber))
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}
