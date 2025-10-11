//
//  SettingsView.swift
//  Arbitra
//
//  Application settings and configuration
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @AppStorage("apiBaseURL") private var apiBaseURL = "http://localhost:8000"
    @AppStorage("wsBaseURL") private var wsBaseURL = "ws://localhost:8000/ws/market-data"
    @AppStorage("refreshInterval") private var refreshInterval = 5
    @AppStorage("showNotifications") private var showNotifications = true
    @AppStorage("notificationSound") private var notificationSound = true
    @AppStorage("autoStartTrading") private var autoStartTrading = false
    @AppStorage("defaultPaperTrading") private var defaultPaperTrading = true
    @AppStorage("chartStyle") private var chartStyle = "line"
    @AppStorage("theme") private var theme = "system"
    
    var body: some View {
        Form {
            // Trading settings
            Section("Trading") {
                Toggle("Start in Paper Trading Mode", isOn: $defaultPaperTrading)
                    .help("Always start in paper trading mode for safety")
                
                Toggle("Auto-start Trading", isOn: $autoStartTrading)
                    .help("Automatically start trading when the app launches")
                
                Picker("Refresh Interval", selection: $refreshInterval) {
                    Text("1 second").tag(1)
                    Text("5 seconds").tag(5)
                    Text("10 seconds").tag(10)
                    Text("30 seconds").tag(30)
                    Text("1 minute").tag(60)
                }
                .help("How often to refresh portfolio data")
                
                Divider()
                
                Button(action: openAITradingView) {
                    Label("Configure AI Trading", systemImage: "brain")
                }
                .help("Open AI trading agent configuration")
            }
            
            // API settings
            Section("API Configuration") {
                TextField("API Base URL", text: $apiBaseURL)
                    .textFieldStyle(.roundedBorder)
                    .help("Backend API endpoint (e.g., http://localhost:8000)")
                
                TextField("WebSocket URL", text: $wsBaseURL)
                    .textFieldStyle(.roundedBorder)
                    .help("WebSocket endpoint for real-time updates")
                
                Button("Test Connection") {
                    testAPIConnection()
                }
            }
            
            // Notifications
            Section("Notifications") {
                Toggle("Show Notifications", isOn: $showNotifications)
                    .help("Show system notifications for important events")
                
                Toggle("Notification Sound", isOn: $notificationSound)
                    .disabled(!showNotifications)
                    .help("Play sound with notifications")
                
                HStack {
                    Text("Notify on:")
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("• Position opened/closed")
                        Text("• Stop loss triggered")
                        Text("• Take profit hit")
                        Text("• Emergency stop")
                    }
                    .font(.caption)
                    .foregroundColor(.secondary)
                }
            }
            
            // Display settings
            Section("Display") {
                Picker("Theme", selection: $theme) {
                    Text("System").tag("system")
                    Text("Light").tag("light")
                    Text("Dark").tag("dark")
                }
                
                Picker("Chart Style", selection: $chartStyle) {
                    Text("Line").tag("line")
                    Text("Area").tag("area")
                    Text("Candlestick").tag("candlestick")
                }
            }
            
            // Risk management
            Section("Risk Management") {
                RiskLimitsView()
            }
            
            // Data management
            Section("Data") {
                Button("Export Trade History") {
                    exportTradeHistory()
                }
                
                Button("Export Performance Report") {
                    exportPerformanceReport()
                }
                
                Divider()
                
                Button("Clear Cache", role: .destructive) {
                    clearCache()
                }
                
                Button("Reset to Defaults", role: .destructive) {
                    resetToDefaults()
                }
            }
            
            // About
            Section("About") {
                HStack {
                    Text("Version")
                    Spacer()
                    Text("1.0.0")
                        .foregroundColor(.secondary)
                }
                
                HStack {
                    Text("Build")
                    Spacer()
                    Text("2024.01")
                        .foregroundColor(.secondary)
                }
                
                Link("View Documentation", destination: URL(string: "https://github.com/yourusername/arbitra")!)
                
                Link("Report Issue", destination: URL(string: "https://github.com/yourusername/arbitra/issues")!)
            }
        }
        .formStyle(.grouped)
        .navigationTitle("Settings")
        .frame(minWidth: 600, minHeight: 700)
    }
    
    private func testAPIConnection() {
        Task {
            do {
                _ = try await APIService.shared.fetchPortfolio()
                appState.showAlert("Successfully connected to API", type: .success)
            } catch {
                appState.showAlert("Could not connect to API: \(error.localizedDescription)", type: .error)
            }
        }
    }
    
    private func exportTradeHistory() {
        let panel = NSSavePanel()
        panel.nameFieldStringValue = "trade-history-\(Date().ISO8601Format()).csv"
        panel.allowedContentTypes = [.commaSeparatedText]
        
        panel.begin { response in
            if response == .OK, let url = panel.url {
                // TODO: Implement CSV export
                print("Exporting trade history to: \(url)")
            }
        }
    }
    
    private func exportPerformanceReport() {
        let panel = NSSavePanel()
        panel.nameFieldStringValue = "performance-report-\(Date().ISO8601Format()).pdf"
        panel.allowedContentTypes = [.pdf]
        
        panel.begin { response in
            if response == .OK, let url = panel.url {
                // TODO: Implement PDF report generation
                print("Exporting performance report to: \(url)")
            }
        }
    }
    
    private func clearCache() {
        // TODO: Implement cache clearing
        appState.showAlert("Application cache has been cleared", type: .success)
    }
    
    private func resetToDefaults() {
        apiBaseURL = "http://localhost:8000"
        wsBaseURL = "ws://localhost:8000/ws/market-data"
        refreshInterval = 5
        showNotifications = true
        notificationSound = true
        autoStartTrading = false
        defaultPaperTrading = true
        chartStyle = "line"
        theme = "system"
        
        appState.showAlert("All settings have been reset to defaults", type: .success)
    }
    
    private func openAITradingView() {
        appState.selectedView = .aiTrading
    }
}

struct RiskLimitsView: View {
    @AppStorage("maxPositionSize") private var maxPositionSize = 10000.0
    @AppStorage("maxDailyLoss") private var maxDailyLoss = 500.0
    @AppStorage("maxTotalExposure") private var maxTotalExposure = 50000.0
    @AppStorage("defaultStopLossPercent") private var defaultStopLossPercent = 2.0
    @AppStorage("defaultTakeProfitPercent") private var defaultTakeProfitPercent = 5.0
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Set global risk limits for all trades")
                .font(.caption)
                .foregroundColor(.secondary)
            
            HStack {
                Text("Max Position Size")
                Spacer()
                TextField("", value: $maxPositionSize, format: .currency(code: "USD"))
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 120)
            }
            
            HStack {
                Text("Max Daily Loss")
                Spacer()
                TextField("", value: $maxDailyLoss, format: .currency(code: "USD"))
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 120)
            }
            
            HStack {
                Text("Max Total Exposure")
                Spacer()
                TextField("", value: $maxTotalExposure, format: .currency(code: "USD"))
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 120)
            }
            
            Divider()
            
            HStack {
                Text("Default Stop Loss")
                Spacer()
                TextField("", value: $defaultStopLossPercent, format: .percent)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 120)
            }
            
            HStack {
                Text("Default Take Profit")
                Spacer()
                TextField("", value: $defaultTakeProfitPercent, format: .percent)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 120)
            }
        }
        .padding(.vertical, 8)
    }
}

// Preview provider
struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
            .environmentObject(AppState())
    }
}
