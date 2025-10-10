//
//  APIService.swift
//  Arbitra
//
//  API service for backend communication
//

import Foundation

enum APIError: Error {
    case invalidURL
    case requestFailed
    case invalidResponse
    case decodingError
    case serverError(String)
}

class APIService {
    static let shared = APIService()
    
    private let baseURL = "http://localhost:8000/api"
    private let decoder: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()
    
    private let encoder: JSONEncoder = {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }()
    
    private init() {}
    
    // MARK: - Portfolio
    
    func fetchPortfolio() async throws -> Portfolio {
        // Fetch account info
        let accountURL = try buildURL(endpoint: "/trading/account")
        let accountResponse: AccountResponse = try await performRequest(url: accountURL)
        
        // Fetch positions
        let positionsURL = try buildURL(endpoint: "/trading/positions")
        let positionsResponse: PositionsListResponse = try await performRequest(url: positionsURL)
        
        // Convert positions
        let positions = positionsResponse.positions.map { $0.toPosition() }
        
        // Convert to Portfolio
        return accountResponse.toPortfolio(positions: positions)
    }
    
    func fetchRecentTrades(limit: Int = 20) async throws -> [Trade] {
        let url = try buildURL(endpoint: "/trading/trades", queryItems: [
            URLQueryItem(name: "limit", value: "\(limit)")
        ])
        let response: TradesListResponse = try await performRequest(url: url)
        
        // Convert trades
        return response.trades.map { $0.toTrade() }
    }
    
    func fetchPerformanceMetrics() async throws -> PerformanceMetrics {
        // Use account endpoint to get performance data
        let url = try buildURL(endpoint: "/trading/account")
        let accountResponse: AccountResponse = try await performRequest(url: url)
        
        // Convert to PerformanceMetrics model
        // Note: Most fields are not available from the account endpoint yet
        return PerformanceMetrics(
            totalTrades: accountResponse.tradeCount,
            winningTrades: 0, // Not available yet
            losingTrades: 0, // Not available yet
            winRate: 0, // Not available yet
            profitFactor: 0, // Not available yet
            sharpeRatio: 0, // Not available yet
            maxDrawdown: 0, // Not available yet
            averageWin: 0,
            averageLoss: 0,
            avgWin: 0,
            avgLoss: 0,
            largestWin: 0,
            largestLoss: 0,
            riskRewardRatio: 0,
            totalFees: 0,
            runtimeDays: 0
        )
    }
    
    // MARK: - Trading Control
    
    func startTrading(paperMode: Bool) async throws {
        let url = try buildURL(endpoint: "/trading/start")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["paper_mode": paperMode]
        request.httpBody = try encoder.encode(body)
        
        try await performVoidRequest(request: request)
    }
    
    func stopTrading() async throws {
        let url = try buildURL(endpoint: "/trading/stop")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        try await performVoidRequest(request: request)
    }
    
    func emergencyStop() async throws {
        let url = try buildURL(endpoint: "/trading/emergency-stop")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        try await performVoidRequest(request: request)
    }
    
    // MARK: - Position Management
    
    func closePosition(_ positionId: String) async throws {
        let url = try buildURL(endpoint: "/positions/\(positionId)/close")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        try await performVoidRequest(request: request)
    }
    
    func updatePositionStopLoss(_ positionId: String, stopLoss: Decimal) async throws {
        let url = try buildURL(endpoint: "/positions/\(positionId)/stop-loss")
        var request = URLRequest(url: url)
        request.httpMethod = "PATCH"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["stop_loss": stopLoss]
        request.httpBody = try encoder.encode(body)
        
        try await performVoidRequest(request: request)
    }
    
    // MARK: - Private Methods
    
    private func buildURL(endpoint: String, queryItems: [URLQueryItem]? = nil) throws -> URL {
        guard var components = URLComponents(string: baseURL + endpoint) else {
            throw APIError.invalidURL
        }
        
        components.queryItems = queryItems
        
        guard let url = components.url else {
            throw APIError.invalidURL
        }
        
        return url
    }
    
    private func performRequest<T: Decodable>(url: URL) async throws -> T {
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            print("Decoding error: \(error)")
            throw APIError.decodingError
        }
    }
    
    private func performVoidRequest(request: URLRequest) async throws {
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.serverError("HTTP \(httpResponse.statusCode)")
        }
    }
}
