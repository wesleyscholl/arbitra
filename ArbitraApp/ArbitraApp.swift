//
//  ArbitraApp.swift
//  Arbitra
//
//  Native macOS trading bot interface
//

import SwiftUI
import AppKit

@main
struct ArbitraApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var appState = AppState()
    @StateObject private var portfolioState = PortfolioState()
    @StateObject private var connectionState = ConnectionState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .environmentObject(portfolioState)
                .environmentObject(connectionState)
                .frame(minWidth: 1200, minHeight: 800)
                .onAppear {
                    setupAppearance()
                    activateApp()
                }
        }
        .windowStyle(.automatic)
        .defaultSize(width: 1400, height: 900)
        .commands {
            // File menu
            CommandGroup(replacing: .newItem) {}
            
            // Trading commands
            CommandMenu("Trading") {
                Button("Start Trading") {
                    Task {
                        await appState.startTrading()
                    }
                }
                .keyboardShortcut("s", modifiers: [.command])
                .disabled(appState.isTradingActive)
                
                Button("Stop Trading") {
                    Task {
                        await appState.stopTrading()
                    }
                }
                .keyboardShortcut("s", modifiers: [.command, .shift])
                .disabled(!appState.isTradingActive)
                
                Divider()
                
                Button("Emergency Stop") {
                    Task {
                        await appState.emergencyStop()
                    }
                }
                .keyboardShortcut("e", modifiers: [.command, .option])
                
                Divider()
                
                Button("Refresh Data") {
                    Task {
                        await portfolioState.refresh()
                    }
                }
                .keyboardShortcut("r", modifiers: [.command])
            }
            
            // View menu
            CommandMenu("View") {
                Button("Dashboard") {
                    appState.selectedView = .dashboard
                }
                .keyboardShortcut("1", modifiers: [.command])
                
                Button("Positions") {
                    appState.selectedView = .positions
                }
                .keyboardShortcut("2", modifiers: [.command])
                
                Button("History") {
                    appState.selectedView = .history
                }
                .keyboardShortcut("3", modifiers: [.command])
                
                Button("Performance") {
                    appState.selectedView = .performance
                }
                .keyboardShortcut("4", modifiers: [.command])
            }
        }
        
        // Settings window
        Settings {
            SettingsView()
                .environmentObject(appState)
        }
    }
    
    private func setupAppearance() {
        // Configure window appearance
        if let window = NSApplication.shared.windows.first {
            window.titlebarAppearsTransparent = true
            window.toolbarStyle = .unified
        }
    }
    
    private func activateApp() {
        // Activate the application and bring windows to front
        NSApplication.shared.activate(ignoringOtherApps: true)
        
        // Make sure the window is visible and key
        if let window = NSApplication.shared.windows.first {
            window.makeKeyAndOrderFront(nil)
        }
    }
}
