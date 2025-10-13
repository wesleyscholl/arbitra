//
//  AITradingView.swift
//  Arbitra
//
//  AI Trading Agent Control and Monitoring
//

import SwiftUI

struct AITradingView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = AITradingViewModel()
    @State private var showConfigSheet = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Main content with 4 panes
            ScrollView {
                VStack(spacing: 20) {
                    // Top Row: Status Cards (4 panes style)
                    HStack(spacing: 16) {
                        AIStatusCard(
                            title: "Agent Status",
                            value: viewModel.agentStatus?.running == true ? "Running" : "Stopped",
                            icon: viewModel.agentStatus?.running == true ? "play.circle.fill" : "stop.circle.fill",
                            color: viewModel.agentStatus?.running == true ? .green : .red,
                            subtitle: viewModel.agentStatus?.running == true ? "Active Trading" : "Inactive"
                        )
                        
                        AIStatusCard(
                            title: "Total Signals",
                            value: "\(viewModel.agentStatus?.totalSignals ?? 0)",
                            icon: "waveform.path.ecg",
                            color: .blue,
                            subtitle: "Generated"
                        )
                        
                        AIStatusCard(
                            title: "Watchlist",
                            value: "\(viewModel.agentStatus?.watchlist.count ?? 0)",
                            icon: "eye.fill",
                            color: .purple,
                            subtitle: "Symbols Monitored"
                        )
                        
                        AIStatusCard(
                            title: "Confidence",
                            value: String(format: "%.0f%%", (viewModel.agentStatus?.signalThreshold ?? 0) * 100),
                            icon: "gauge.high",
                            color: .orange,
                            subtitle: "Min Threshold"
                        )
                    }
                    
                    // Second Row: Configuration Cards
                    HStack(spacing: 16) {
                        AIConfigCard(
                            title: "Scan Interval",
                            value: formatScanInterval(viewModel.agentStatus?.scanInterval ?? 0),
                            icon: "timer",
                            color: .cyan,
                            detail: "Analysis frequency"
                        )
                        
                        AIConfigCard(
                            title: "Max Positions",
                            value: "\(viewModel.agentStatus?.maxPositions ?? 0)",
                            icon: "square.stack.3d.up.fill",
                            color: .indigo,
                            detail: "Concurrent limit"
                        )
                        
                        AIConfigCard(
                            title: "Position Size",
                            value: formatCurrency(viewModel.agentStatus?.maxPositionSize ?? 0),
                            icon: "dollarsign.circle.fill",
                            color: .green,
                            detail: "Max per trade"
                        )
                        
                        if let lastScan = viewModel.agentStatus?.lastScanTime {
                            AIConfigCard(
                                title: "Last Scan",
                                value: formatRelativeTime(lastScan),
                                icon: "clock.arrow.circlepath",
                                color: .teal,
                                detail: "Most recent"
                            )
                        } else {
                            AIConfigCard(
                                title: "Last Scan",
                                value: "Never",
                                icon: "clock.arrow.circlepath",
                                color: .gray,
                                detail: "No scans yet"
                            )
                        }
                    }
                    
                    // Recent Signals Panel
                    AISignalsPanel(viewModel: viewModel)
                    
                    // Watchlist Panel
                    AIWatchlistPanel(viewModel: viewModel)
                }
                .padding()
            }
            
            // Action Bar at Bottom
            AIActionBar(viewModel: viewModel)
        }
        .navigationTitle("AI Trading Agent")
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear {
            viewModel.startPolling()
        }
        .onDisappear {
            viewModel.stopPolling()
        }
        .sheet(isPresented: $showConfigSheet) {
            ConfigEditor(viewModel: viewModel, isPresented: $showConfigSheet)
        }
    }
    
    private func formatScanInterval(_ seconds: Int) -> String {
        if seconds < 60 {
            return "\(seconds)s"
        } else if seconds < 3600 {
            return "\(seconds / 60)m"
        } else {
            return "\(seconds / 3600)h"
        }
    }
    
    private func formatCurrency(_ value: Double) -> String {
        if value >= 1000 {
            return String(format: "$%.1fK", value / 1000)
        } else {
            return String(format: "$%.0f", value)
        }
    }
    
    private func formatRelativeTime(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .short
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

// MARK: - Status Card (Dashboard Style)

struct AIStatusCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    let subtitle: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundColor(color)
                
                Spacer()
            }
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(value)
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(color)
            
            Text(subtitle)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
        .shadow(color: color.opacity(0.1), radius: 5, x: 0, y: 2)
    }
}

struct AIConfigCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    let detail: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundColor(color)
                
                Spacer()
            }
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
            
            Text(detail)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - Signals Panel

struct AISignalsPanel: View {
    @ObservedObject var viewModel: AITradingViewModel
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Recent AI Signals")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Spacer()
                
                Button(action: { viewModel.refreshSignals() }) {
                    Image(systemName: "arrow.clockwise")
                        .font(.subheadline)
                }
                .buttonStyle(.plain)
            }
            
            if viewModel.recentSignals.isEmpty {
                VStack(spacing: 12) {
                    Image(systemName: "waveform.path.ecg")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    
                    Text("No signals generated yet")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    Text("The agent will generate signals every \(viewModel.agentStatus?.scanInterval ?? 300) seconds")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                .padding(40)
            } else {
                ForEach(viewModel.recentSignals.prefix(5)) { signal in
                    AISignalCard(signal: signal)
                }
            }
        }
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
    }
}

struct AISignalCard: View {
    let signal: AISignal
    
    private var signalColor: Color {
        switch signal.signalType {
        case "buy": return .green
        case "sell": return .red
        default: return .gray
        }
    }
    
    var body: some View {
        HStack(spacing: 12) {
            // Signal badge
            VStack {
                Image(systemName: signalIcon)
                    .font(.title2)
                    .foregroundColor(.white)
            }
            .frame(width: 50, height: 50)
            .background(signalColor)
            .cornerRadius(10)
            
            // Signal info
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(signal.symbol)
                        .font(.headline)
                        .fontWeight(.bold)
                    
                    Text(signal.signalType.uppercased())
                        .font(.caption)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(signalColor)
                        .cornerRadius(4)
                    
                    Spacer()
                    
                    Text(signal.timestamp, style: .relative)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Text(signal.reasoning)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }
            
            // Confidence meter
            VStack(alignment: .trailing, spacing: 4) {
                Text(String(format: "%.0f%%", signal.confidence * 100))
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(signalColor)
                
                Text("confidence")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(10)
    }
    
    private var signalIcon: String {
        switch signal.signalType {
        case "buy": return "arrow.up.circle.fill"
        case "sell": return "arrow.down.circle.fill"
        default: return "minus.circle.fill"
        }
    }
}

// MARK: - Watchlist Panel

struct AIWatchlistPanel: View {
    @ObservedObject var viewModel: AITradingViewModel
    @State private var newSymbol = ""
    @State private var isEditing = false
    // removed local sheet state – top-level view controls the config sheet
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Trading Watchlist")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Spacer()
                
                Button(isEditing ? "Done" : "Edit") {
                    isEditing.toggle()
                }
                .buttonStyle(.plain)
                .foregroundColor(.blue)
            }
            
            if let watchlist = viewModel.agentStatus?.watchlist, !watchlist.isEmpty {
                FlowLayout(spacing: 8) {
                    ForEach(watchlist, id: \.self) { symbol in
                        WatchlistSymbolChip(
                            symbol: symbol,
                            isEditing: isEditing,
                            onRemove: { viewModel.removeFromWatchlist(symbol) }
                        )
                    }
                }
                
                if isEditing {
                    HStack {
                        TextField("Add symbol (e.g., NVDA)", text: $newSymbol)
                            .textFieldStyle(.roundedBorder)
                            .textCase(.uppercase)
                        
                        Button(action: addSymbol) {
                            Image(systemName: "plus.circle.fill")
                                .font(.title2)
                                .foregroundColor(.blue)
                        }
                        .buttonStyle(.plain)
                        .disabled(newSymbol.isEmpty)
                    }
                    .padding(.top, 8)
                }
            } else {
                Text("No symbols in watchlist")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            }
        }
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
    }
    
    private func addSymbol() {
        let symbol = newSymbol.uppercased().trimmingCharacters(in: .whitespacesAndNewlines)
        if !symbol.isEmpty {
            viewModel.addToWatchlist(symbol)
            newSymbol = ""
        }
    }
}

struct WatchlistSymbolChip: View {
    let symbol: String
    let isEditing: Bool
    let onRemove: () -> Void
    
    var body: some View {
        HStack(spacing: 6) {
            Text(symbol)
                .font(.callout)
                .fontWeight(.semibold)
            
            if isEditing {
                Button(action: onRemove) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.caption)
                        .foregroundColor(.red)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(chipBackground)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(chipBorder, lineWidth: 1)
        )
    }

    private var isCrypto: Bool {
        return symbol.uppercased().contains("/") || symbol.uppercased().contains("USD")
    }

    private var chipBackground: Color {
        isCrypto ? Color.purple.opacity(0.12) : Color.green.opacity(0.12)
    }

    private var chipBorder: Color {
        isCrypto ? Color.purple.opacity(0.25) : Color.green.opacity(0.25)
    }
}

// MARK: - Action Bar

struct AIActionBar: View {
    @ObservedObject var viewModel: AITradingViewModel
    
    var body: some View {
        HStack(spacing: 16) {
            // Start button
            Button(action: { viewModel.startAgent() }) {
                HStack(spacing: 8) {
                    Image(systemName: "play.fill")
                    Text("Start Agent")
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(viewModel.agentStatus?.running == true ? Color.gray.opacity(0.3) : Color.green)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .buttonStyle(.plain)
            .disabled(viewModel.agentStatus?.running == true || viewModel.isLoading)
            
            // Stop button
            Button(action: { viewModel.stopAgent() }) {
                HStack(spacing: 8) {
                    Image(systemName: "stop.fill")
                    Text("Stop Agent")
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(viewModel.agentStatus?.running != true ? Color.gray.opacity(0.3) : Color.red)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .buttonStyle(.plain)
            .disabled(viewModel.agentStatus?.running != true || viewModel.isLoading)
            
            // Refresh button
            Button(action: { viewModel.refreshStatus() }) {
                HStack(spacing: 8) {
                    Image(systemName: viewModel.isLoading ? "arrow.clockwise" : "arrow.clockwise")
                        .rotationEffect(.degrees(viewModel.isLoading ? 360 : 0))
                        .animation(viewModel.isLoading ? .linear(duration: 1).repeatForever(autoreverses: false) : .default, value: viewModel.isLoading)
                    Text("Refresh")
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.blue.opacity(0.1))
                .foregroundColor(.blue)
                .cornerRadius(10)
            }
            .buttonStyle(.plain)
            .disabled(viewModel.isLoading)
            
            // View Config button
            Button(action: {}) {
                HStack(spacing: 8) {
                    Image(systemName: "gearshape.fill")
                    Text("Configure")
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.purple.opacity(0.1))
                .foregroundColor(.purple)
                .cornerRadius(10)
            }
            .buttonStyle(.plain)
        }
        .padding()
        .background(Color(.controlBackgroundColor))
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: -2)
    }
}



// MARK: - Flow Layout for chips

struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(
            in: proposal.replacingUnspecifiedDimensions().width,
            subviews: subviews,
            spacing: spacing
        )
        return result.size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(
            in: bounds.width,
            subviews: subviews,
            spacing: spacing
        )
        for (index, subview) in subviews.enumerated() {
            subview.place(at: CGPoint(x: bounds.minX + result.positions[index].x, y: bounds.minY + result.positions[index].y), proposal: .unspecified)
        }
    }
    
    struct FlowResult {
        var size: CGSize = .zero
        var positions: [CGPoint] = []
        
        init(in maxWidth: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var currentX: CGFloat = 0
            var currentY: CGFloat = 0
            var lineHeight: CGFloat = 0
            
            for subview in subviews {
                let size = subview.sizeThatFits(.unspecified)
                
                if currentX + size.width > maxWidth && currentX > 0 {
                    currentX = 0
                    currentY += lineHeight + spacing
                    lineHeight = 0
                }
                
                positions.append(CGPoint(x: currentX, y: currentY))
                lineHeight = max(lineHeight, size.height)
                currentX += size.width + spacing
            }
            
            self.size = CGSize(width: maxWidth, height: currentY + lineHeight)
        }
    }
}

// MARK: - Preview

struct AITradingView_Previews: PreviewProvider {
    static var previews: some View {
        AITradingView()
            .environmentObject(AppState())
            .frame(width: 800, height: 600)
    }
}

// MARK: - Config Editor Sheet

struct ConfigEditor: View {
    @ObservedObject var viewModel: AITradingViewModel
    @Binding var isPresented: Bool

    @State private var scanInterval: String = ""
    @State private var signalThreshold: String = ""
    @State private var maxPositions: String = ""
    @State private var maxPositionSize: String = ""
    @State private var watchlistPreview: String = ""

    var body: some View {
        VStack(spacing: 12) {
            Text("Configure AI Agent")
                .font(.title2)
                .fontWeight(.bold)

            Form {
                HStack {
                    Text("Scan Interval (s)")
                    Spacer()
                    TextField("", text: $scanInterval)
                        .frame(width: 80)
                        .multilineTextAlignment(.trailing)
                }

                HStack {
                    Text("Signal Threshold")
                    Spacer()
                    TextField("0.7", text: $signalThreshold)
                        .frame(width: 80)
                        .multilineTextAlignment(.trailing)
                }

                HStack {
                    Text("Max Positions")
                    Spacer()
                    TextField("", text: $maxPositions)
                        .frame(width: 80)
                        .multilineTextAlignment(.trailing)
                }

                HStack {
                    Text("Max Position Size")
                    Spacer()
                    TextField("", text: $maxPositionSize)
                        .frame(width: 120)
                        .multilineTextAlignment(.trailing)
                }

                VStack(alignment: .leading) {
                    Text("Watchlist Preview")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    TextEditor(text: $watchlistPreview)
                        .frame(height: 100)
                        .font(.caption)
                        .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color.gray.opacity(0.2)))
                }
            }

            HStack(spacing: 12) {
                Button("Cancel") {
                    isPresented = false
                }
                .keyboardShortcut(.cancelAction)

                Spacer()

                Button("Save") {
                    saveConfig()
                }
                .keyboardShortcut(.defaultAction)
            }
            .padding(.horizontal)
        }
        .padding()
        .frame(width: 600, height: 420)
        .onAppear(perform: loadFromViewModel)
    }

    private func loadFromViewModel() {
        guard let s = viewModel.agentStatus else { return }
        scanInterval = "\(s.scanInterval)"
        signalThreshold = String(format: "%.2f", s.signalThreshold)
        maxPositions = "\(s.maxPositions)"
        maxPositionSize = String(format: "%.2f", s.maxPositionSize)
        watchlistPreview = s.watchlist.joined(separator: ", ")
    }

    private func saveConfig() {
        guard let scan = Int(scanInterval), let threshold = Double(signalThreshold), let maxPos = Int(maxPositions), let maxSize = Double(maxPositionSize) else {
            return
        }

        let config = AIAgentConfig(watchlist: watchlistPreview.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }, scanInterval: scan, signalThreshold: threshold, maxPositions: maxPos, maxPositionSize: maxSize)

        viewModel.updateAgentConfig(config)
        isPresented = false
    }
}
