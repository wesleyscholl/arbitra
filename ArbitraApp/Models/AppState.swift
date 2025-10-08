//
//  AppState.swift
//  Arbitra
//
//  Global application state
//

import Foundation
import SwiftUI

enum AppView {
    case dashboard
    case positions
    case history
    case performance
    case settings
}

@MainActor
class AppState: ObservableObject {
    @Published var selectedView: AppView = .dashboard
    @Published var isTradingActive: Bool = false
    @Published var isPaperTrading: Bool = true
    @Published var showingAlert: Bool = false
    @Published var alertMessage: String = ""
    @Published var alertType: AlertType = .info
    
    private let apiService = APIService.shared
    
    enum AlertType {
        case info
        case success
        case warning
        case error
    }
    
    func startTrading() async {
        do {
            try await apiService.startTrading(paperMode: isPaperTrading)
            isTradingActive = true
            showAlert("Trading started", type: .success)
        } catch {
            showAlert("Failed to start trading: \(error.localizedDescription)", type: .error)
        }
    }
    
    func stopTrading() async {
        do {
            try await apiService.stopTrading()
            isTradingActive = false
            showAlert("Trading stopped", type: .info)
        } catch {
            showAlert("Failed to stop trading: \(error.localizedDescription)", type: .error)
        }
    }
    
    func emergencyStop() async {
        do {
            try await apiService.emergencyStop()
            isTradingActive = false
            showAlert("EMERGENCY STOP ACTIVATED - All positions closed", type: .warning)
        } catch {
            showAlert("Emergency stop failed: \(error.localizedDescription)", type: .error)
        }
    }
    
    func showAlert(_ message: String, type: AlertType = .info) {
        alertMessage = message
        alertType = type
        showingAlert = true
        
        // Also send system notification
        sendNotification(message, type: type)
    }
    
    private func sendNotification(_ message: String, type: AlertType) {
        let notification = NSUserNotification()
        notification.title = "Arbitra"
        notification.informativeText = message
        notification.soundName = type == .error ? NSUserNotificationDefaultSoundName : nil
        
        NSUserNotificationCenter.default.deliver(notification)
    }
}
