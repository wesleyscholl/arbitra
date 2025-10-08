//
//  ContentView.swift
//  Arbitra
//
//  Main content view with navigation
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var portfolioState: PortfolioState
    @EnvironmentObject var connectionState: ConnectionState
    
    var body: some View {
        NavigationSplitView {
            // Sidebar
            SidebarView()
        } detail: {
            // Main content area
            mainContentView
                .toolbar {
                    ToolbarItem(placement: .navigation) {
                        TradingStatusButton()
                    }
                    
                    ToolbarItem {
                        ConnectionStatusView()
                    }
                    
                    ToolbarItem {
                        RefreshButton()
                    }
                }
        }
        .alert("Alert", isPresented: $appState.showingAlert) {
            Button("OK") {
                appState.showingAlert = false
            }
        } message: {
            Text(appState.alertMessage)
        }
    }
    
    @ViewBuilder
    private var mainContentView: some View {
        switch appState.selectedView {
        case .dashboard:
            DashboardView()
        case .positions:
            PositionsView()
        case .history:
            HistoryView()
        case .performance:
            PerformanceView()
        case .settings:
            SettingsView()
        }
    }
}

struct SidebarView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        List(selection: $appState.selectedView) {
            Section("Trading") {
                NavigationLink(value: AppView.dashboard) {
                    Label("Dashboard", systemImage: "chart.line.uptrend.xyaxis")
                }
                
                NavigationLink(value: AppView.positions) {
                    Label("Positions", systemImage: "briefcase")
                }
                
                NavigationLink(value: AppView.history) {
                    Label("History", systemImage: "clock.arrow.circlepath")
                }
            }
            
            Section("Analytics") {
                NavigationLink(value: AppView.performance) {
                    Label("Performance", systemImage: "chart.bar.xaxis")
                }
            }
            
            Section("System") {
                NavigationLink(value: AppView.settings) {
                    Label("Settings", systemImage: "gearshape")
                }
            }
        }
        .listStyle(.sidebar)
        .navigationTitle("Arbitra")
    }
}

struct TradingStatusButton: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Button(action: toggleTrading) {
            HStack(spacing: 6) {
                Circle()
                    .fill(appState.isTradingActive ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
                
                Text(appState.isTradingActive ? "Trading Active" : "Trading Stopped")
                    .font(.caption)
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.gray.opacity(0.2))
            .cornerRadius(8)
        }
        .buttonStyle(.plain)
    }
    
    private func toggleTrading() {
        Task {
            if appState.isTradingActive {
                await appState.stopTrading()
            } else {
                await appState.startTrading()
            }
        }
    }
}

struct ConnectionStatusView: View {
    @EnvironmentObject var connectionState: ConnectionState
    
    var body: some View {
        HStack(spacing: 6) {
            Circle()
                .fill(connectionState.isConnected ? Color.green : Color.red)
                .frame(width: 8, height: 8)
            
            Text(connectionState.connectionStatus)
                .font(.caption)
        }
    }
}

struct RefreshButton: View {
    @EnvironmentObject var portfolioState: PortfolioState
    @State private var isRotating = false
    
    var body: some View {
        Button(action: refresh) {
            Image(systemName: "arrow.clockwise")
                .rotationEffect(.degrees(isRotating ? 360 : 0))
                .animation(isRotating ? .linear(duration: 1).repeatForever(autoreverses: false) : .default, value: isRotating)
        }
    }
    
    private func refresh() {
        isRotating = true
        Task {
            await portfolioState.refresh()
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            isRotating = false
        }
    }
}
