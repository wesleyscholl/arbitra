//
//  AppState.swift
//  Arbitra
//
//  Global application state
//

import Foundation
import SwiftUI
import UserNotifications

enum AppView {
    case dashboard
    case positions
    case history
    case performance
    case aiTrading
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
        let center = UNUserNotificationCenter.current()
        
        // Request authorization if not already granted
        center.requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                let content = UNMutableNotificationContent()
                content.title = "Arbitra"
                content.body = message
                
                if type == .error {
                    content.sound = .default
                }
                
                // Create notification request
                let request = UNNotificationRequest(
                    identifier: UUID().uuidString,
                    content: content,
                    trigger: nil // Deliver immediately
                )
                
                center.add(request) { error in
                    if let error = error {
                        print("Failed to deliver notification: \(error)")
                    }
                }
            }
        }
    }
}
