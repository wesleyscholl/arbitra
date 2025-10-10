//
//  ConnectionState.swift
//  Arbitra
//
//  WebSocket connection state
//

import Foundation
import SwiftUI

@MainActor
class ConnectionState: ObservableObject {
    @Published var isConnected: Bool = false
    @Published var connectionStatus: String = "Disconnected"
    @Published var lastUpdateTime: Date?
    
    private var webSocket: URLSessionWebSocketTask?
    private let baseURL = "ws://localhost:8000/ws/market-data"
    
    init() {
        connect()
    }
    
    func connect() {
        guard let url = URL(string: baseURL) else { return }
        
        let session = URLSession(configuration: .default)
        webSocket = session.webSocketTask(with: url)
        webSocket?.resume()
        
        isConnected = true
        connectionStatus = "Connected"
        
        receiveMessage()
    }
    
    func disconnect() {
        webSocket?.cancel(with: .goingAway, reason: nil)
        isConnected = false
        connectionStatus = "Disconnected"
    }
    
    private func receiveMessage() {
        webSocket?.receive { [weak self] result in
            Task { @MainActor in
                switch result {
                case .success(let message):
                    await self?.handleMessage(message)
                    self?.receiveMessage() // Continue receiving
                    
                case .failure(let error):
                    print("WebSocket receive error: \(error)")
                    // Try to reconnect
                    try? await Task.sleep(nanoseconds: 5_000_000_000)
                    self?.connect()
                }
            }
        }
    }
    
    private func handleMessage(_ message: URLSessionWebSocketTask.Message) async {
        lastUpdateTime = Date()
        
        switch message {
        case .string(let text):
            if let data = text.data(using: .utf8),
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                print("Received WebSocket message: \(json)")
                // TODO: Handle different message types
            }
        case .data(let data):
            print("Received binary data: \(data.count) bytes")
        @unknown default:
            break
        }
    }
    
    deinit {
        webSocket?.cancel(with: .goingAway, reason: nil)
    }
}
