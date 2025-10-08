//
//  HistoryView.swift
//  Arbitra
//
//  Trade history with filtering and export
//

import SwiftUI

struct HistoryView: View {
    @EnvironmentObject var portfolioState: PortfolioState
    @State private var searchText = ""
    @State private var filterAction: TradeAction? = nil
    @State private var dateRange = DateRange.all
    @State private var sortOrder = TradeSortOrder.dateDescending
    @State private var selectedTrade: Trade?
    
    enum DateRange: String, CaseIterable {
        case all = "All Time"
        case today = "Today"
        case week = "This Week"
        case month = "This Month"
        case year = "This Year"
        
        var systemImage: String {
            switch self {
            case .all: return "calendar"
            case .today: return "calendar.badge.clock"
            case .week: return "calendar.badge.plus"
            case .month: return "calendar.circle"
            case .year: return "calendar.circle.fill"
            }
        }
        
        func filter(_ date: Date) -> Bool {
            let calendar = Calendar.current
            let now = Date()
            
            switch self {
            case .all:
                return true
            case .today:
                return calendar.isDateInToday(date)
            case .week:
                return calendar.isDate(date, equalTo: now, toGranularity: .weekOfYear)
            case .month:
                return calendar.isDate(date, equalTo: now, toGranularity: .month)
            case .year:
                return calendar.isDate(date, equalTo: now, toGranularity: .year)
            }
        }
    }
    
    enum TradeSortOrder: String, CaseIterable {
        case dateDescending = "Newest First"
        case dateAscending = "Oldest First"
        case pnlDescending = "Highest P/L"
        case pnlAscending = "Lowest P/L"
        case symbolAscending = "Symbol A-Z"
        
        var systemImage: String {
            switch self {
            case .dateDescending: return "arrow.down"
            case .dateAscending: return "arrow.up"
            case .pnlDescending: return "arrow.up.right"
            case .pnlAscending: return "arrow.down.right"
            case .symbolAscending: return "textformat.abc"
            }
        }
    }
    
    var filteredTrades: [Trade] {
        var trades = portfolioState.recentTrades
        
        // Search filter
        if !searchText.isEmpty {
            trades = trades.filter { $0.symbol.localizedCaseInsensitiveContains(searchText) }
        }
        
        // Action filter
        if let action = filterAction {
            trades = trades.filter { $0.action == action }
        }
        
        // Date filter
        trades = trades.filter { dateRange.filter($0.entryTime) }
        
        // Sort
        trades.sort { trade1, trade2 in
            switch sortOrder {
            case .dateDescending:
                return trade1.entryTime > trade2.entryTime
            case .dateAscending:
                return trade1.entryTime < trade2.entryTime
            case .pnlDescending:
                return (trade1.pnl ?? 0) > (trade2.pnl ?? 0)
            case .pnlAscending:
                return (trade1.pnl ?? 0) < (trade2.pnl ?? 0)
            case .symbolAscending:
                return trade1.symbol < trade2.symbol
            }
        }
        
        return trades
    }
    
    var totalPnL: Decimal {
        filteredTrades.reduce(0) { $0 + ($1.pnl ?? 0) }
    }
    
    var winRate: Double {
        let closedTrades = filteredTrades.filter { $0.pnl != nil }
        guard !closedTrades.isEmpty else { return 0 }
        
        let winners = closedTrades.filter { ($0.pnl ?? 0) > 0 }.count
        return Double(winners) / Double(closedTrades.count) * 100
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Summary stats
            HStack(spacing: 20) {
                StatCard(
                    title: "Total Trades",
                    value: "\(filteredTrades.count)",
                    icon: "chart.bar.fill",
                    color: .blue
                )
                
                StatCard(
                    title: "Win Rate",
                    value: String(format: "%.1f%%", winRate),
                    icon: "target",
                    color: .green
                )
                
                StatCard(
                    title: "Total P/L",
                    value: "$\(formatDecimal(totalPnL))",
                    icon: totalPnL >= 0 ? "arrow.up.right" : "arrow.down.right",
                    color: totalPnL >= 0 ? .green : .red
                )
            }
            .padding()
            .background(Color(.controlBackgroundColor))
            
            Divider()
            
            // Filters
            HStack {
                // Search
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)
                
                TextField("Search trades...", text: $searchText)
                    .textFieldStyle(.plain)
                
                if !searchText.isEmpty {
                    Button(action: { searchText = "" }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                    .buttonStyle(.plain)
                }
                
                Divider()
                    .frame(height: 20)
                
                // Action filter
                Menu {
                    Button("All Actions") {
                        filterAction = nil
                    }
                    Divider()
                    ForEach([TradeAction.buy, TradeAction.sell], id: \.self) { action in
                        Button {
                            filterAction = action
                        } label: {
                            Label(action.rawValue.capitalized, systemImage: action == .buy ? "plus.circle" : "minus.circle")
                            if filterAction == action {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                } label: {
                    Label(filterAction?.rawValue.capitalized ?? "Action", systemImage: "slider.horizontal.3")
                }
                
                // Date range
                Menu {
                    ForEach(DateRange.allCases, id: \.self) { range in
                        Button {
                            dateRange = range
                        } label: {
                            Label(range.rawValue, systemImage: range.systemImage)
                            if dateRange == range {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                } label: {
                    Label(dateRange.rawValue, systemImage: dateRange.systemImage)
                }
                
                // Sort order
                Menu {
                    ForEach(TradeSortOrder.allCases, id: \.self) { order in
                        Button {
                            sortOrder = order
                        } label: {
                            Label(order.rawValue, systemImage: order.systemImage)
                            if sortOrder == order {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                } label: {
                    Label("Sort", systemImage: "arrow.up.arrow.down")
                }
            }
            .padding()
            .background(Color(.windowBackgroundColor))
            
            Divider()
            
            // Trade list
            if filteredTrades.isEmpty {
                EmptyTradesView(hasFilters: !searchText.isEmpty || filterAction != nil || dateRange != .all)
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(filteredTrades) { trade in
                            TradeHistoryCard(trade: trade) {
                                selectedTrade = trade
                            }
                        }
                    }
                    .padding()
                }
            }
        }
        .navigationTitle("Trade History")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button(action: exportTrades) {
                    Label("Export", systemImage: "square.and.arrow.up")
                }
            }
        }
        .sheet(item: $selectedTrade) { trade in
            TradeDetailSheet(trade: trade)
        }
    }
    
    private func exportTrades() {
        // TODO: Implement CSV export
        print("Exporting \(filteredTrades.count) trades...")
    }
    
    private func formatDecimal(_ value: Decimal) -> String {
        String(format: "%.2f", Double(truncating: value as NSNumber))
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

struct EmptyTradesView: View {
    let hasFilters: Bool
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: hasFilters ? "line.3.horizontal.decrease.circle" : "chart.bar.doc.horizontal")
                .font(.system(size: 60))
                .foregroundColor(.secondary)
            
            Text(hasFilters ? "No trades match filters" : "No trade history")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text(hasFilters
                 ? "Try adjusting your filters"
                 : "Completed trades will appear here")
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct TradeHistoryCard: View {
    let trade: Trade
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 16) {
                // Action badge
                ZStack {
                    Circle()
                        .fill(trade.action == .buy ? Color.green : Color.red)
                        .frame(width: 50, height: 50)
                    
                    Image(systemName: trade.action == .buy ? "arrow.down.circle.fill" : "arrow.up.circle.fill")
                        .font(.title3)
                        .foregroundColor(.white)
                }
                
                // Symbol and details
                VStack(alignment: .leading, spacing: 4) {
                    Text(trade.symbol)
                        .font(.headline)
                        .fontWeight(.bold)
                    
                    HStack(spacing: 12) {
                        Label("\(formatDecimal(trade.quantity))", systemImage: "number")
                        Label("$\(formatDecimal(trade.entryPrice))", systemImage: "dollarsign.circle")
                    }
                    .font(.caption)
                    .foregroundColor(.secondary)
                    
                    Text(formatDate(trade.entryTime))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                // P/L
                if let pnl = trade.pnl, let pnlPct = trade.pnlPct {
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("$\(formatDecimal(pnl))")
                            .font(.headline)
                            .fontWeight(.bold)
                            .foregroundColor(pnl >= 0 ? .green : .red)
                        
                        Text(String(format: "%+.2f%%", Double(truncating: pnlPct as NSNumber)))
                            .font(.subheadline)
                            .foregroundColor(pnl >= 0 ? .green : .red)
                    }
                }
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.windowBackgroundColor))
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }
    
    private func formatDecimal(_ value: Decimal) -> String {
        String(format: "%.2f", Double(truncating: value as NSNumber))
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

struct TradeDetailSheet: View {
    let trade: Trade
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(trade.symbol)
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    HStack(spacing: 4) {
                        Text(trade.action.rawValue.uppercased())
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(trade.action == .buy ? Color.green : Color.red)
                            .cornerRadius(6)
                    }
                }
                
                Spacer()
                
                Button(action: { dismiss() }) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
            }
            
            Divider()
            
            // P/L (if closed)
            if let pnl = trade.pnl, let pnlPct = trade.pnlPct {
                VStack(spacing: 8) {
                    Text("Realized P/L")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Text("$\(formatDecimal(pnl))")
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(pnl >= 0 ? .green : .red)
                    
                    Text(String(format: "%+.2f%%", Double(truncating: pnlPct as NSNumber)))
                        .font(.title2)
                        .foregroundColor(pnl >= 0 ? .green : .red)
                }
                .padding()
                .background(Color.gray.opacity(0.05))
                .cornerRadius(12)
            }
            
            // Trade details
            VStack(alignment: .leading, spacing: 16) {
                DetailRow(label: "Quantity", value: formatDecimal(trade.quantity))
                DetailRow(label: "Entry Price", value: "$\(formatDecimal(trade.entryPrice))")
                
                if let exitPrice = trade.exitPrice {
                    DetailRow(label: "Exit Price", value: "$\(formatDecimal(exitPrice))")
                }
                
                DetailRow(label: "Entry Time", value: formatDateTime(trade.entryTime))
                
                if let exitTime = trade.exitTime {
                    DetailRow(label: "Exit Time", value: formatDateTime(exitTime))
                }
                
                if let fees = trade.fees {
                    DetailRow(label: "Fees", value: "$\(formatDecimal(fees))", valueColor: .orange)
                }
                
                if let slippage = trade.slippage {
                    DetailRow(label: "Slippage", value: "$\(formatDecimal(slippage))", valueColor: .orange)
                }
            }
            
            Spacer()
        }
        .padding()
        .frame(width: 500, height: 600)
    }
    
    private func formatDecimal(_ value: Decimal) -> String {
        String(format: "%.2f", Double(truncating: value as NSNumber))
    }
    
    private func formatDateTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}
