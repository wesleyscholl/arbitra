//
//  PerformanceView.swift
//  Arbitra
//
//  Comprehensive performance analytics and metrics
//

import SwiftUI
import Charts

struct PerformanceView: View {
    @EnvironmentObject var portfolioState: PortfolioState
    @State private var selectedTimeframe = Timeframe.month
    @State private var selectedMetric = MetricType.portfolioValue
    
    enum Timeframe: String, CaseIterable {
        case day = "1D"
        case week = "1W"
        case month = "1M"
        case quarter = "3M"
        case year = "1Y"
        case all = "All"
        
        var systemImage: String {
            switch self {
            case .day: return "calendar.badge.clock"
            case .week: return "calendar.badge.plus"
            case .month: return "calendar"
            case .quarter: return "calendar.circle"
            case .year: return "calendar.circle.fill"
            case .all: return "calendar.badge.checkmark"
            }
        }
    }
    
    enum MetricType: String, CaseIterable {
        case portfolioValue = "Portfolio Value"
        case pnl = "P/L"
        case winRate = "Win Rate"
        case sharpeRatio = "Sharpe Ratio"
        
        var systemImage: String {
            switch self {
            case .portfolioValue: return "chart.line.uptrend.xyaxis"
            case .pnl: return "dollarsign.circle.fill"
            case .winRate: return "target"
            case .sharpeRatio: return "chart.bar.xaxis"
            }
        }
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Timeframe selector
                Picker("Timeframe", selection: $selectedTimeframe) {
                    ForEach(Timeframe.allCases, id: \.self) { timeframe in
                        Text(timeframe.rawValue).tag(timeframe)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)
                
                // Key metrics
                KeyMetricsView(metrics: portfolioState.performanceMetrics)
                
                // Main chart
                VStack(alignment: .leading, spacing: 12) {
                    // Metric selector
                    Menu {
                        ForEach(MetricType.allCases, id: \.self) { metric in
                            Button {
                                selectedMetric = metric
                            } label: {
                                Label(metric.rawValue, systemImage: metric.systemImage)
                                if selectedMetric == metric {
                                    Image(systemName: "checkmark")
                                }
                            }
                        }
                    } label: {
                        Label(selectedMetric.rawValue, systemImage: selectedMetric.systemImage)
                            .font(.title3)
                            .fontWeight(.semibold)
                    }
                    
                    // Chart
                    PerformanceChart(
                        data: filteredPerformanceData,
                        metric: selectedMetric
                    )
                    .frame(height: 350)
                }
                .padding()
                .background(Color(.windowBackgroundColor))
                .cornerRadius(12)
                
                // Trade statistics
                TradeStatisticsView(metrics: portfolioState.performanceMetrics)
                
                // Risk metrics
                RiskMetricsView(metrics: portfolioState.performanceMetrics)
                
                // Asset tier breakdown
                AssetTierPerformanceView(portfolio: portfolioState.portfolio)
            }
            .padding()
        }
        .navigationTitle("Performance")
    }
    
    var filteredPerformanceData: [PortfolioState.PerformanceDataPoint] {
        let calendar = Calendar.current
        let now = Date()
        
        return portfolioState.performanceHistory.filter { point in
            switch selectedTimeframe {
            case .all:
                return true
            case .day:
                return calendar.isDateInToday(point.date)
            case .week:
                return calendar.isDate(point.date, equalTo: now, toGranularity: .weekOfYear)
            case .month:
                return calendar.isDate(point.date, equalTo: now, toGranularity: .month)
            case .quarter:
                guard let threeMonthsAgo = calendar.date(byAdding: .month, value: -3, to: now) else { return false }
                return point.date >= threeMonthsAgo
            case .year:
                return calendar.isDate(point.date, equalTo: now, toGranularity: .year)
            }
        }
    }
}

struct KeyMetricsView: View {
    let metrics: PerformanceMetrics?
    
    var body: some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible()),
            GridItem(.flexible())
        ], spacing: 16) {
            MetricCard(
                title: "Win Rate",
                value: String(format: "%.1f%%", metrics?.winRate ?? 0),
                icon: "target",
                color: .green
            )
            
            MetricCard(
                title: "Sharpe Ratio",
                value: String(format: "%.2f", metrics?.sharpeRatio ?? 0),
                icon: "chart.bar.xaxis",
                color: .blue
            )
            
            MetricCard(
                title: "Max Drawdown",
                value: String(format: "%.1f%%", metrics?.maxDrawdown ?? 0),
                icon: "arrow.down.right.circle",
                color: .red
            )
            
            MetricCard(
                title: "Avg Win",
                value: "$\(formatDecimal(metrics?.avgWin ?? 0))",
                icon: "arrow.up.circle.fill",
                color: .green
            )
            
            MetricCard(
                title: "Avg Loss",
                value: "$\(formatDecimal(metrics?.avgLoss ?? 0))",
                icon: "arrow.down.circle.fill",
                color: .red
            )
            
            MetricCard(
                title: "Profit Factor",
                value: String(format: "%.2f", metrics?.profitFactor ?? 0),
                icon: "divide.circle",
                color: .purple
            )
        }
    }
    
    private func formatDecimal(_ value: Decimal) -> String {
        String(format: "%.2f", Double(truncating: value as NSNumber))
    }
}

struct MetricCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}

struct PerformanceChart: View {
    let data: [PortfolioState.PerformanceDataPoint]
    let metric: PerformanceView.MetricType
    
    var body: some View {
        if data.isEmpty {
            VStack {
                Image(systemName: "chart.xyaxis.line")
                    .font(.system(size: 60))
                    .foregroundColor(.secondary)
                Text("No performance data")
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else {
            Chart(data) { point in
                LineMark(
                    x: .value("Date", point.date),
                    y: .value("Value", metricValue(point))
                )
                .foregroundStyle(metricColor.gradient)
                .interpolationMethod(.catmullRom)
                
                AreaMark(
                    x: .value("Date", point.date),
                    y: .value("Value", metricValue(point))
                )
                .foregroundStyle(metricColor.opacity(0.1).gradient)
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
    
    private func metricValue(_ point: PortfolioState.PerformanceDataPoint) -> Double {
        switch metric {
        case .portfolioValue:
            return Double(truncating: point.portfolioValue as NSNumber)
        case .pnl:
            return Double(truncating: point.totalPnL as NSNumber)
        case .winRate:
            return point.winRate
        case .sharpeRatio:
            return point.sharpeRatio
        }
    }
    
    private var metricColor: Color {
        switch metric {
        case .portfolioValue: return .blue
        case .pnl: return .green
        case .winRate: return .purple
        case .sharpeRatio: return .orange
        }
    }
}

struct TradeStatisticsView: View {
    let metrics: PerformanceMetrics?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Trade Statistics")
                .font(.title2)
                .fontWeight(.bold)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                StatRow(label: "Total Trades", value: "\(metrics?.totalTrades ?? 0)")
                StatRow(label: "Winning Trades", value: "\(metrics?.winningTrades ?? 0)", color: .green)
                StatRow(label: "Losing Trades", value: "\(metrics?.losingTrades ?? 0)", color: .red)
                StatRow(label: "Win Rate", value: String(format: "%.1f%%", metrics?.winRate ?? 0))
                StatRow(label: "Average Win", value: "$\(formatDecimal(metrics?.avgWin ?? 0))", color: .green)
                StatRow(label: "Average Loss", value: "$\(formatDecimal(metrics?.avgLoss ?? 0))", color: .red)
                StatRow(label: "Largest Win", value: "$\(formatDecimal(metrics?.largestWin ?? 0))", color: .green)
                StatRow(label: "Largest Loss", value: "$\(formatDecimal(metrics?.largestLoss ?? 0))", color: .red)
            }
        }
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
    }
    
    private func formatDecimal(_ value: Decimal) -> String {
        String(format: "%.2f", Double(truncating: value as NSNumber))
    }
}

struct RiskMetricsView: View {
    let metrics: PerformanceMetrics?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Risk Metrics")
                .font(.title2)
                .fontWeight(.bold)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                StatRow(label: "Sharpe Ratio", value: String(format: "%.2f", metrics?.sharpeRatio ?? 0))
                StatRow(label: "Max Drawdown", value: String(format: "%.1f%%", metrics?.maxDrawdown ?? 0), color: .red)
                StatRow(label: "Profit Factor", value: String(format: "%.2f", metrics?.profitFactor ?? 0))
                StatRow(label: "Risk/Reward Ratio", value: String(format: "%.2f", metrics?.riskRewardRatio ?? 0))
            }
        }
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
    }
}

struct AssetTierPerformanceView: View {
    let portfolio: Portfolio?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Asset Tier Performance")
                .font(.title2)
                .fontWeight(.bold)
            
            ForEach(AssetTier.allCases, id: \.self) { tier in
                TierPerformanceRow(tier: tier, portfolio: portfolio)
            }
        }
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
    }
}

struct TierPerformanceRow: View {
    let tier: AssetTier
    let portfolio: Portfolio?
    
    var tierPositions: [Position] {
        portfolio?.positions.filter { $0.tier == tier } ?? []
    }
    
    var tierValue: Decimal {
        tierPositions.reduce(0) { $0 + $1.currentValue }
    }
    
    var tierPnL: Decimal {
        tierPositions.reduce(0) { $0 + $1.unrealizedPnL }
    }
    
    var body: some View {
        HStack {
            // Tier info
            VStack(alignment: .leading, spacing: 4) {
                Text(tier.displayName)
                    .font(.headline)
                    .foregroundColor(tierColor)
                
                Text("\(tierPositions.count) positions")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // Value
            VStack(alignment: .trailing, spacing: 4) {
                Text("$\(formatDecimal(tierValue))")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text("$\(formatDecimal(tierPnL))")
                    .font(.caption)
                    .foregroundColor(tierPnL >= 0 ? .green : .red)
            }
        }
        .padding()
        .background(tierColor.opacity(0.1))
        .cornerRadius(8)
    }
    
    private var tierColor: Color {
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

struct StatRow: View {
    let label: String
    let value: String
    var color: Color = .primary
    
    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(color)
        }
        .padding(.vertical, 4)
    }
}
