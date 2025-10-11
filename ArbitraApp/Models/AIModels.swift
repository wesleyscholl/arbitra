//
//  AIModels.swift
//  Arbitra
//
//  Models for AI Trading Agent
//

import Foundation

// MARK: - Agent Status

struct AIAgentStatus: Codable {
    let running: Bool
    let watchlist: [String]
    let scanInterval: Int
    let signalThreshold: Double
    let maxPositions: Int
    let maxPositionSize: Double
    let lastScanTime: Date?
    let totalSignals: Int
    
    enum CodingKeys: String, CodingKey {
        case running
        case watchlist
        case scanInterval = "scan_interval"
        case signalThreshold = "signal_threshold"
        case maxPositions = "max_positions"
        case maxPositionSize = "max_position_size"
        case lastScanTime = "last_scan_time"
        case totalSignals = "total_signals"
    }
}

// MARK: - AI Signal

struct AISignal: Codable, Identifiable {
    let id: UUID
    let symbol: String
    let signalType: String  // "buy", "sell", "hold"
    let confidence: Double
    let reasoning: String
    let timestamp: Date
    let currentPrice: Double?
    let targetSize: Int?
    let model: String?
    
    enum CodingKeys: String, CodingKey {
        case symbol
        case signalType = "signal_type"
        case confidence
        case reasoning
        case timestamp
        case currentPrice = "current_price"
        case targetSize = "target_size"
        case model
        case indicators  // Added to handle extra field in response
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = UUID()
        self.symbol = try container.decode(String.self, forKey: .symbol)
        self.signalType = try container.decode(String.self, forKey: .signalType)
        self.confidence = try container.decode(Double.self, forKey: .confidence)
        self.reasoning = try container.decode(String.self, forKey: .reasoning)
        self.timestamp = try container.decode(Date.self, forKey: .timestamp)
        self.currentPrice = try container.decodeIfPresent(Double.self, forKey: .currentPrice)
        self.targetSize = try container.decodeIfPresent(Int.self, forKey: .targetSize)
        self.model = try container.decodeIfPresent(String.self, forKey: .model)
        // Ignore indicators field
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(symbol, forKey: .symbol)
        try container.encode(signalType, forKey: .signalType)
        try container.encode(confidence, forKey: .confidence)
        try container.encode(reasoning, forKey: .reasoning)
        try container.encode(timestamp, forKey: .timestamp)
        try container.encodeIfPresent(currentPrice, forKey: .currentPrice)
        try container.encodeIfPresent(targetSize, forKey: .targetSize)
        try container.encodeIfPresent(model, forKey: .model)
    }
}

// MARK: - Agent Config

struct AIAgentConfig: Codable {
    var watchlist: [String]
    var scanInterval: Int
    var signalThreshold: Double
    var maxPositions: Int
    var maxPositionSize: Double
    
    enum CodingKeys: String, CodingKey {
        case watchlist
        case scanInterval = "scan_interval"
        case signalThreshold = "signal_threshold"
        case maxPositions = "max_positions"
        case maxPositionSize = "max_position_size"
    }
}

// MARK: - Response Wrappers

struct AgentStatusResponse: Codable {
    let status: AIAgentStatus?
    let message: String?
}

struct SignalsResponse: Codable {
    let signals: [AISignal]
}

struct AgentControlResponse: Codable {
    let message: String
    let status: String
}

struct WatchlistResponse: Codable {
    let symbols: [String]
}

struct WatchlistUpdateResponse: Codable {
    let message: String
    let symbols: [String]
}
