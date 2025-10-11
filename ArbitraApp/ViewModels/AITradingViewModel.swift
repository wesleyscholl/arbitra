//
//  AITradingViewModel.swift
//  Arbitra
//
//  View model for AI Trading Agent
//

import Foundation
import Combine

class AITradingViewModel: ObservableObject {
    @Published var agentStatus: AIAgentStatus?
    @Published var recentSignals: [AISignal] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private var pollingTimer: Timer?
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        refreshStatus()
        refreshSignals()
    }
    
    // MARK: - Polling
    
    func startPolling() {
        pollingTimer?.invalidate()
        pollingTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            self?.refreshStatus()
            self?.refreshSignals()
        }
    }
    
    func stopPolling() {
        pollingTimer?.invalidate()
        pollingTimer = nil
    }
    
    // MARK: - Actions
    
    func startAgent() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                try await AITradingService.shared.startAgent()
                await MainActor.run {
                    isLoading = false
                    refreshStatus()
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "Failed to start agent: \(error.localizedDescription)"
                }
            }
        }
    }
    
    func stopAgent() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                try await AITradingService.shared.stopAgent()
                await MainActor.run {
                    isLoading = false
                    refreshStatus()
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "Failed to stop agent: \(error.localizedDescription)"
                }
            }
        }
    }
    
    func refreshStatus() {
        Task {
            do {
                let status = try await AITradingService.shared.getAgentStatus()
                await MainActor.run {
                    self.agentStatus = status
                    self.errorMessage = nil
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = "Failed to fetch status: \(error.localizedDescription)"
                }
            }
        }
    }
    
    func refreshSignals() {
        Task {
            do {
                let signals = try await AITradingService.shared.getRecentSignals(limit: 20)
                await MainActor.run {
                    self.recentSignals = signals
                }
            } catch {
                // Silent fail for signals refresh
                print("Failed to fetch signals: \(error)")
            }
        }
    }
    
    func addToWatchlist(_ symbol: String) {
        guard let status = agentStatus else { return }
        
        var updatedWatchlist = status.watchlist
        if !updatedWatchlist.contains(symbol) {
            updatedWatchlist.append(symbol)
            updateWatchlist(updatedWatchlist)
        }
    }
    
    func removeFromWatchlist(_ symbol: String) {
        guard let status = agentStatus else { return }
        
        var updatedWatchlist = status.watchlist
        updatedWatchlist.removeAll { $0 == symbol }
        updateWatchlist(updatedWatchlist)
    }
    
    private func updateWatchlist(_ symbols: [String]) {
        Task {
            do {
                try await AITradingService.shared.updateWatchlist(symbols)
                await MainActor.run {
                    refreshStatus()
                }
            } catch {
                await MainActor.run {
                    errorMessage = "Failed to update watchlist: \(error.localizedDescription)"
                }
            }
        }
    }
    
    deinit {
        stopPolling()
    }
}
