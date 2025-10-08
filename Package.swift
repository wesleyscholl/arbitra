// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "ArbitraApp",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "ArbitraApp",
            targets: ["ArbitraApp"]
        )
    ],
    targets: [
        .executableTarget(
            name: "ArbitraApp",
            dependencies: [],
            path: "ArbitraApp"
        )
    ]
)
