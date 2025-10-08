//
//  FormatHelpers.swift
//  Arbitra
//
//  Formatting utilities
//

import Foundation

extension Double {
    func toDecimal() -> Decimal {
        Decimal(self)
    }
    
    func formatted() -> String {
        String(format: "%.2f", self)
    }
}

func formatDecimal(_ value: Double) -> String {
    String(format: "%.2f", value)
}

func formatDecimal(_ value: Decimal) -> String {
    String(format: "%.2f", Double(truncating: value as NSNumber))
}
