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
        let url = try buildURL(endpoint: "/portfolio")
        return try await performRequest(url: url)
    }
    
    func fetchRecentTrades(limit: Int = 20) async throws -> [Trade] {
        let url = try buildURL(endpoint: "/trades/recent", queryItems: [
            URLQueryItem(name: "limit", value: "\(limit)")
        ])
        return try await performRequest(url: url)
    }
    
    func fetchPerformanceMetrics() async throws -> PerformanceMetrics {
        let url = try buildURL(endpoint: "/performance/metrics")
        return try await performRequest(url: url)
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
