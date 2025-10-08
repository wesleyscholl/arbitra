//
//  Portfolio.swift
//  Arbitra
//
//  Portfolio data models
//

import Foundation

struct Portfolio: Codable, Identifiable {
    let id: UUID
    let totalValue: Decimal
    let cash: Decimal
    let positions: [Position]
    let dailyPnL: Decimal
    let dailyPnLPct: Decimal
    let totalPnL: Decimal
    let totalPnLPct: Decimal
    let updatedAt: Date
    
    var positionValue: Decimal {
        positions.reduce(Decimal(0)) { $0 + $1.currentValue }
    }
}

struct Position: Codable, Identifiable {
    let id: String
    let symbol: String
    let quantity: Decimal
    let entryPrice: Decimal
    let currentPrice: Decimal
    let unrealizedPnL: Decimal
    let unrealizedPnLPct: Decimal
    let stopLoss: Decimal?
    let takeProfit: Decimal?
    let tier: AssetTier
    let strategy: String
    let confidence: Decimal
    let entryTime: Date
    
    var currentValue: Decimal {
        currentPrice * quantity
    }
    
    var costBasis: Decimal {
        entryPrice * quantity
    }
}

enum AssetTier: String, Codable, CaseIterable {
    case foundation = "FOUNDATION"
    case growth = "GROWTH"
    case opportunity = "OPPORTUNITY"
    
    var color: String {
        switch self {
        case .foundation: return "blue"
        case .growth: return "purple"
        case .opportunity: return "orange"
        }
    }
    
    var displayName: String {
        switch self {
        case .foundation: return "Foundation"
        case .growth: return "Growth"
        case .opportunity: return "Opportunity"
        }
    }
}

struct Trade: Codable, Identifiable {
    let id: String
    let symbol: String
    let action: TradeAction
    let entryPrice: Decimal
    let exitPrice: Decimal?
    let quantity: Decimal
    let pnl: Decimal?
    let pnlPct: Decimal?
    let entryTime: Date
    let exitTime: Date?
    let exitReason: String?
    let strategy: String
    let confidence: Decimal
    let tier: AssetTier
    let fees: Decimal?
    let slippage: Decimal?
    
    var isOpen: Bool {
        exitPrice == nil
    }
    
    var holdingTime: TimeInterval? {
        guard let exitTime = exitTime else { return nil }
        return exitTime.timeIntervalSince(entryTime)
    }
}

enum TradeAction: String, Codable {
    case buy = "BUY"
    case sell = "SELL"
}

struct PerformanceMetrics: Codable {
    let totalTrades: Int
    let winningTrades: Int
    let losingTrades: Int
    let winRate: Double
    let profitFactor: Double
    let sharpeRatio: Double
    let maxDrawdown: Double
    let averageWin: Decimal
    let averageLoss: Decimal
    let avgWin: Decimal
    let avgLoss: Decimal
    let largestWin: Decimal
    let largestLoss: Decimal
    let riskRewardRatio: Double
    let totalFees: Decimal
    let runtimeDays: Double
}
