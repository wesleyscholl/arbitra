//
//  PortfolioState.swift
//  Arbitra
//
//  Portfolio state management
//

import Foundation
import SwiftUI

@MainActor
class PortfolioState: ObservableObject {
    @Published var portfolio: Portfolio?
    @Published var recentTrades: [Trade] = []
    @Published var performanceMetrics: PerformanceMetrics?
    @Published var performanceHistory: [PerformanceDataPoint] = []
    @Published var isLoading: Bool = false
    @Published var error: String?
    
    private let apiService = APIService.shared
    private var refreshTimer: Timer?
    
    struct PerformanceDataPoint: Identifiable {
        let id = UUID()
        let date: Date
        let portfolioValue: Decimal
        let totalPnL: Decimal
        let winRate: Double
        let sharpeRatio: Double
    }
    
    init() {
        startAutoRefresh()
    }
    
    func refresh() async {
        isLoading = true
        error = nil
        
        do {
            async let portfolioTask = apiService.fetchPortfolio()
            async let tradesTask = apiService.fetchRecentTrades(limit: 20)
            async let metricsTask = apiService.fetchPerformanceMetrics()
            
            portfolio = try await portfolioTask
            recentTrades = try await tradesTask
            performanceMetrics = try await metricsTask
            
            isLoading = false
        } catch {
            self.error = error.localizedDescription
            isLoading = false
        }
    }
    
    func closePosition(symbol: String) async {
        do {
            try await apiService.closePosition(symbol)
            await refresh()
        } catch {
            self.error = "Failed to close position: \(error.localizedDescription)"
        }
    }
    
    func updatePositionStopLoss(symbol: String, stopLossPrice: Decimal) async {
        do {
            try await apiService.updatePositionStopLoss(symbol, stopLoss: stopLossPrice)
            await refresh()
        } catch {
            self.error = "Failed to update stop loss: \(error.localizedDescription)"
        }
    }
    
    private func startAutoRefresh() {
        // Refresh every 5 seconds
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            Task { @MainActor in
                await self?.refresh()
            }
        }
        
        // Initial refresh
        Task {
            await refresh()
        }
    }
    
    deinit {
        refreshTimer?.invalidate()
    }
}
