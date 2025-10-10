// 
//  APIResponseModels.swift
//  Arbitra
//
//  Response models that match the backend API
//

import Foundation

// MARK: - Account Response (from /api/trading/account)

struct AccountResponse: Codable {
    let cash: Double
    let buyingPower: Double
    let equity: Double
    let portfolioValue: Double
    let initialCapital: Double
    let totalPl: Double
    let realizedPl: Double
    let unrealizedPl: Double
    let totalReturn: Double
    let positionCount: Int
    let tradeCount: Int
}

// MARK: - Position Response (from /api/trading/positions)

struct PositionResponse: Codable {
    let symbol: String
    let quantity: Double
    let side: String
    let entryPrice: Double
    let entryTime: String
    let currentPrice: Double
    let marketValue: Double
    let costBasis: Double
    let unrealizedPl: Double
    let unrealizedPlpc: Double
    let realizedPl: Double
}

// MARK: - Trade Response (from /api/trading/trades)

struct TradeResponse: Codable {
    let symbol: String
    let side: String
    let quantity: Double
    let price: Double
    let commission: Double
    let timestamp: String
    let orderId: String
}

// MARK: - Trades List Response

struct TradesListResponse: Codable {
    let trades: [TradeResponse]
}

// MARK: - Positions List Response

struct PositionsListResponse: Codable {
    let positions: [PositionResponse]
}

// MARK: - Quote Response (from /api/trading/quote/{symbol})

struct QuoteResponse: Codable {
    let symbol: String
    let bidPrice: Double
    let bidSize: Int
    let askPrice: Double
    let askSize: Int
    let timestamp: String
}

// MARK: - Order Response

struct OrderResponse: Codable {
    let orderId: String
    let symbol: String
    let side: String
    let quantity: Double
    let orderType: String
    let limitPrice: Double?
    let status: String
    let submittedAt: String
    let filledAt: String?
    let filledPrice: Double?
}

// MARK: - Conversion Extensions

extension AccountResponse {
    func toPortfolio(positions: [Position]) -> Portfolio {
        return Portfolio(
            id: UUID(),
            totalValue: Decimal(portfolioValue),
            cash: Decimal(cash),
            positions: positions,
            dailyPnL: Decimal(unrealizedPl),
            dailyPnLPct: Decimal(totalReturn),
            totalPnL: Decimal(totalPl),
            totalPnLPct: Decimal(totalReturn),
            updatedAt: Date()
        )
    }
}

extension PositionResponse {
    func toPosition() -> Position {
        let dateFormatter = ISO8601DateFormatter()
        let entryDate = dateFormatter.date(from: entryTime) ?? Date()
        
        return Position(
            id: symbol,
            symbol: symbol,
            quantity: Decimal(quantity),
            entryPrice: Decimal(entryPrice),
            currentPrice: Decimal(currentPrice),
            unrealizedPnL: Decimal(unrealizedPl),
            unrealizedPnLPct: Decimal(unrealizedPlpc),
            stopLoss: nil,
            takeProfit: nil,
            tier: .growth, // Default tier
            strategy: "paper", // Default strategy
            confidence: Decimal(0.7), // Default confidence
            entryTime: entryDate
        )
    }
}

extension TradeResponse {
    func toTrade() -> Trade {
        let dateFormatter = ISO8601DateFormatter()
        let tradeDate = dateFormatter.date(from: timestamp) ?? Date()
        
        let action: TradeAction = side.lowercased() == "buy" ? .buy : .sell
        
        return Trade(
            id: orderId,
            symbol: symbol,
            action: action,
            entryPrice: Decimal(price),
            exitPrice: side.lowercased() == "sell" ? Decimal(price) : nil,
            quantity: Decimal(quantity),
            pnl: nil,
            pnlPct: nil,
            entryTime: tradeDate,
            exitTime: side.lowercased() == "sell" ? tradeDate : nil,
            exitReason: nil,
            strategy: "paper",
            confidence: Decimal(0.7),
            tier: .growth,
            fees: Decimal(commission),
            slippage: nil
        )
    }
}
