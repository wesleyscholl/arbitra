//
//  PositionsView.swift
//  Arbitra
//
//  Detailed positions table with management controls
//

import SwiftUI

struct PositionsView: View {
    @EnvironmentObject var portfolioState: PortfolioState
    @State private var selectedPosition: Position?
    @State private var showingCloseConfirmation = false
    @State private var showingStopLossEditor = false
    @State private var newStopLoss: String = ""
    @State private var searchText = ""
    @State private var sortOrder = PositionSortOrder.value
    
    enum PositionSortOrder: String, CaseIterable {
        case symbol = "Symbol"
        case value = "Value"
        case pnl = "P/L"
        case pnlPercent = "P/L %"
        
        var systemImage: String {
            switch self {
            case .symbol: return "textformat.abc"
            case .value: return "dollarsign.circle"
            case .pnl: return "chart.line.uptrend.xyaxis"
            case .pnlPercent: return "percent"
            }
        }
    }
    
    var filteredPositions: [Position] {
        guard let positions = portfolioState.portfolio?.positions else { return [] }
        
        let filtered = searchText.isEmpty
            ? positions
            : positions.filter { $0.symbol.localizedCaseInsensitiveContains(searchText) }
        
        return filtered.sorted { pos1, pos2 in
            switch sortOrder {
            case .symbol:
                return pos1.symbol < pos2.symbol
            case .value:
                return pos1.currentValue > pos2.currentValue
            case .pnl:
                return pos1.unrealizedPnL > pos2.unrealizedPnL
            case .pnlPercent:
                return pos1.unrealizedPnLPct > pos2.unrealizedPnLPct
            }
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            searchAndSortBar
            Divider()
            positionsContent
        }
        .navigationTitle("Positions (\(filteredPositions.count))")
        .sheet(item: $selectedPosition) { position in
            PositionDetailSheet(
                position: position,
                onClose: { showingCloseConfirmation = true },
                onUpdateStopLoss: { showingStopLossEditor = true }
            )
        }
        .alert("Close Position", isPresented: $showingCloseConfirmation) {
            Button("Cancel", role: .cancel) { }
            Button("Close", role: .destructive) {
                closeSelectedPosition()
            }
        } message: {
            closePositionMessage
        }
        .alert("Update Stop Loss", isPresented: $showingStopLossEditor) {
            TextField("Stop Loss Price", text: $newStopLoss)
            Button("Cancel", role: .cancel) { newStopLoss = "" }
            Button("Update") { updateStopLoss() }
        } message: {
            stopLossMessage
        }
    }
    
    private var searchAndSortBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
            
            TextField("Search positions...", text: $searchText)
                .textFieldStyle(.plain)
            
            if !searchText.isEmpty {
                Button(action: { searchText = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
            }
            
            Divider().frame(height: 20)
            
            Menu {
                ForEach(PositionSortOrder.allCases, id: \.self) { order in
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
                Label("Sort: \(sortOrder.rawValue)", systemImage: "arrow.up.arrow.down")
            }
        }
        .padding()
        .background(Color(.controlBackgroundColor))
    }
    
    private var positionsContent: some View {
        Group {
            if filteredPositions.isEmpty {
                EmptyPositionsView(hasSearch: !searchText.isEmpty)
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(filteredPositions) { position in
                            PositionDetailCard(position: position) {
                                selectedPosition = position
                            }
                        }
                    }
                    .padding()
                }
            }
        }
    }
    
    private var closePositionMessage: some View {
        Group {
            if let position = selectedPosition {
                Text("Close position in \(position.symbol) for $\(formatDecimal(position.currentValue))?")
            }
        }
    }
    
    private var stopLossMessage: some View {
        Group {
            if let position = selectedPosition {
                Text("Update stop loss for \(position.symbol)")
            }
        }
    }
    
    private func closeSelectedPosition() {
        if let position = selectedPosition {
            Task {
                await portfolioState.closePosition(symbol: position.symbol)
                selectedPosition = nil
            }
        }
    }
    
    private func updateStopLoss() {
        if let position = selectedPosition,
           let stopPrice = Decimal(string: newStopLoss) {
            Task {
                await portfolioState.updatePositionStopLoss(
                    symbol: position.symbol,
                    stopLossPrice: stopPrice
                )
                newStopLoss = ""
            }
        }
    }
    
    private func formatDecimal(_ value: Decimal) -> String {
        String(format: "%.2f", Double(truncating: value as NSNumber))
    }
}

struct EmptyPositionsView: View {
    let hasSearch: Bool
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: hasSearch ? "magnifyingglass" : "chart.line.flattrend.xyaxis")
                .font(.system(size: 60))
                .foregroundColor(.secondary)
            
            Text(hasSearch ? "No positions found" : "No open positions")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text(hasSearch
                 ? "Try adjusting your search"
                 : "Open positions will appear here when trading is active")
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct PositionDetailCard: View {
    let position: Position
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 12) {
                // Header row
                HStack {
                    // Symbol and tier
                    VStack(alignment: .leading, spacing: 4) {
                        Text(position.symbol)
                            .font(.title3)
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
                    
                    // P/L
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("$\(formatDecimal(position.unrealizedPnL))")
                            .font(.title3)
                            .fontWeight(.bold)
                            .foregroundColor(position.unrealizedPnL >= 0 ? .green : .red)
                        
                        Text(String(format: "%+.2f%%", Double(truncating: position.unrealizedPnLPct as NSNumber)))
                            .font(.subheadline)
                            .foregroundColor(position.unrealizedPnL >= 0 ? .green : .red)
                    }
                }
                
                Divider()
                
                // Details grid
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 12) {
                    DetailItem(label: "Quantity", value: formatDecimal(position.quantity))
                    DetailItem(label: "Entry Price", value: "$\(formatDecimal(position.entryPrice))")
                    DetailItem(label: "Current Price", value: "$\(formatDecimal(position.currentPrice))")
                    DetailItem(label: "Current Value", value: "$\(formatDecimal(position.currentValue))")
                    
                    if let stopLoss = position.stopLoss {
                        DetailItem(label: "Stop Loss", value: "$\(formatDecimal(stopLoss))", isAlert: true)
                    }
                    
                    if let takeProfit = position.takeProfit {
                        DetailItem(label: "Take Profit", value: "$\(formatDecimal(takeProfit))", isSuccess: true)
                    }
                }
            }
            .padding()
            .background(Color(.windowBackgroundColor))
            .cornerRadius(12)
            .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
        }
        .buttonStyle(.plain)
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

struct DetailItem: View {
    let label: String
    let value: String
    var isAlert: Bool = false
    var isSuccess: Bool = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(isAlert ? .red : (isSuccess ? .green : .primary))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct PositionDetailSheet: View {
    let position: Position
    let onClose: () -> Void
    let onUpdateStopLoss: () -> Void
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(position.symbol)
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    HStack(spacing: 4) {
                        Image(systemName: "tag.fill")
                        Text(position.tier.displayName)
                            .font(.subheadline)
                    }
                    .foregroundColor(tierColor(position.tier))
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
            
            // P/L summary
            VStack(spacing: 8) {
                Text("Unrealized P/L")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text("$\(formatDecimal(position.unrealizedPnL))")
                    .font(.system(size: 48, weight: .bold))
                    .foregroundColor(position.unrealizedPnL >= 0 ? .green : .red)
                
                Text(String(format: "%+.2f%%", Double(truncating: position.unrealizedPnLPct as NSNumber)))
                    .font(.title2)
                    .foregroundColor(position.unrealizedPnL >= 0 ? .green : .red)
            }
            .padding()
            .background(Color.gray.opacity(0.05))
            .cornerRadius(12)
            
            // Details
            VStack(alignment: .leading, spacing: 16) {
                DetailRow(label: "Quantity", value: formatDecimal(position.quantity))
                DetailRow(label: "Entry Price", value: "$\(formatDecimal(position.entryPrice))")
                DetailRow(label: "Current Price", value: "$\(formatDecimal(position.currentPrice))")
                DetailRow(label: "Current Value", value: "$\(formatDecimal(position.currentValue))")
                
                if let stopLoss = position.stopLoss {
                    DetailRow(label: "Stop Loss", value: "$\(formatDecimal(stopLoss))", valueColor: .red)
                }
                
                if let takeProfit = position.takeProfit {
                    DetailRow(label: "Take Profit", value: "$\(formatDecimal(takeProfit))", valueColor: .green)
                }
                
                DetailRow(label: "Entry Time", value: formatDate(position.entryTime))
            }
            
            Spacer()
            
            // Actions
            HStack(spacing: 12) {
                Button(action: {
                    dismiss()
                    onUpdateStopLoss()
                }) {
                    Label("Update Stop Loss", systemImage: "shield.fill")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
                
                Button(role: .destructive, action: {
                    dismiss()
                    onClose()
                }) {
                    Label("Close Position", systemImage: "xmark.circle.fill")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
            }
        }
        .padding()
        .frame(width: 500, height: 600)
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
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

struct DetailRow: View {
    let label: String
    let value: String
    var valueColor: Color = .primary
    
    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .fontWeight(.medium)
                .foregroundColor(valueColor)
        }
    }
}
