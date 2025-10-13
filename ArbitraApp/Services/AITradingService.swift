//
//  AITradingService.swift
//  Arbitra
//
//  Service for AI Trading Agent API calls
//

import Foundation

enum AITradingError: Error {
    case invalidURL
    case requestFailed
    case invalidResponse
    case decodingError
    case serverError(String)
}

class AITradingService {
    static let shared = AITradingService()
    
    private let baseURL = "http://localhost:8000/api"
    private let decoder: JSONDecoder = {
        let decoder = JSONDecoder()
        // Don't use automatic snake_case conversion - we handle it explicitly in CodingKeys
        
        // Custom date decoding strategy to handle Python datetime format
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        
        decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)
            
            // Try ISO8601 with fractional seconds first
            if let date = formatter.date(from: dateString) {
                return date
            }
            
            // Fallback: Try without timezone (Python format: 2025-10-10T19:51:29.220918)
            let fallbackFormatter = DateFormatter()
            fallbackFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
            fallbackFormatter.timeZone = TimeZone.current
            
            if let date = fallbackFormatter.date(from: dateString) {
                return date
            }
            
            // Last fallback: Standard ISO8601
            fallbackFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
            if let date = fallbackFormatter.date(from: dateString) {
                return date
            }
            
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Cannot decode date from: \(dateString)")
        }
        
        return decoder
    }()
    
    private let encoder: JSONEncoder = {
        let encoder = JSONEncoder()
        // Don't use automatic snake_case conversion - we handle it explicitly in CodingKeys
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }()
    
    private init() {}
    
    // MARK: - Agent Control
    
    func startAgent() async throws {
        let url = try buildURL(endpoint: "/agent/start")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AITradingError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw AITradingError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        // Parse response
        _ = try decoder.decode(AgentControlResponse.self, from: data)
    }
    
    func stopAgent() async throws {
        let url = try buildURL(endpoint: "/agent/stop")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AITradingError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw AITradingError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        _ = try decoder.decode(AgentControlResponse.self, from: data)
    }
    
    // MARK: - Agent Status
    
    func getAgentStatus() async throws -> AIAgentStatus {
        let url = try buildURL(endpoint: "/agent/status")
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AITradingError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw AITradingError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        return try decoder.decode(AIAgentStatus.self, from: data)
    }
    
    // MARK: - Signals
    
    func getRecentSignals(limit: Int = 20) async throws -> [AISignal] {
        let url = try buildURL(endpoint: "/agent/signals", queryItems: [
            URLQueryItem(name: "limit", value: "\(limit)")
        ])
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AITradingError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw AITradingError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        let signalsResponse = try decoder.decode(SignalsResponse.self, from: data)
        return signalsResponse.signals
    }
    
    // MARK: - Watchlist
    
    func getWatchlist() async throws -> [String] {
        let url = try buildURL(endpoint: "/agent/watchlist")
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AITradingError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw AITradingError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        let watchlistResponse = try decoder.decode(WatchlistResponse.self, from: data)
        return watchlistResponse.symbols
    }
    
    func updateWatchlist(_ symbols: [String]) async throws {
        let url = try buildURL(endpoint: "/agent/watchlist")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encoder.encode(symbols)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AITradingError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw AITradingError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        _ = try decoder.decode(WatchlistUpdateResponse.self, from: data)
    }
    
    // MARK: - Configuration
    
    func getAgentConfig() async throws -> AIAgentConfig {
        let url = try buildURL(endpoint: "/agent/config")
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AITradingError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw AITradingError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        return try decoder.decode(AIAgentConfig.self, from: data)
    }
    
    func updateAgentConfig(_ config: AIAgentConfig) async throws {
        let url = try buildURL(endpoint: "/agent/config")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encoder.encode(config)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AITradingError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw AITradingError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        // Response parsing: expect { "message": "...", "config": { ... } }
        struct ConfigResponse: Codable {
            let message: String
            let config: AIAgentConfig
        }

        let _ = try decoder.decode(ConfigResponse.self, from: data)
    }
    
    // MARK: - Helper Methods
    
    private func buildURL(endpoint: String, queryItems: [URLQueryItem]? = nil) throws -> URL {
        guard var components = URLComponents(string: baseURL + endpoint) else {
            throw AITradingError.invalidURL
        }
        
        components.queryItems = queryItems
        
        guard let url = components.url else {
            throw AITradingError.invalidURL
        }
        
        return url
    }
}
