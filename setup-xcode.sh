#!/bin/bash

# Create Xcode project for Arbitra macOS app
# This script generates the Xcode project structure

set -e

echo "🚀 Creating Arbitra macOS App Xcode Project..."

# Project configuration
PROJECT_NAME="Arbitra"
BUNDLE_ID="com.arbitra.app"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$PROJECT_DIR/ArbitraApp"

echo "📁 Project directory: $PROJECT_DIR"

# Check if ArbitraApp directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Error: ArbitraApp directory not found"
    exit 1
fi

echo "✅ Found ArbitraApp directory"

# Create Info.plist
echo "📝 Creating Info.plist..."
cat > "$APP_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>13.0</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024. All rights reserved.</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>NSMainStoryboardFile</key>
    <string>Main</string>
</dict>
</plist>
EOF

echo "✅ Created Info.plist"

# Create Assets.xcassets directory structure
echo "📦 Creating Assets catalog..."
mkdir -p "$APP_DIR/Assets.xcassets/AppIcon.appiconset"
mkdir -p "$APP_DIR/Assets.xcassets/AccentColor.colorset"

# Create AppIcon Contents.json
cat > "$APP_DIR/Assets.xcassets/AppIcon.appiconset/Contents.json" << 'EOF'
{
  "images" : [
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "16x16"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "16x16"
    },
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "32x32"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "32x32"
    },
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "128x128"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "128x128"
    },
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "256x256"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "256x256"
    },
    {
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "512x512"
    },
    {
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "512x512"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF

# Create AccentColor Contents.json
cat > "$APP_DIR/Assets.xcassets/AccentColor.colorset/Contents.json" << 'EOF'
{
  "colors" : [
    {
      "idiom" : "universal"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF

# Create Assets.xcassets Contents.json
cat > "$APP_DIR/Assets.xcassets/Contents.json" << 'EOF'
{
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF

echo "✅ Created Assets catalog"

# Create Arbitra.entitlements
echo "🔐 Creating entitlements..."
cat > "$APP_DIR/Arbitra.entitlements" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
EOF

echo "✅ Created entitlements"

# Instructions for Xcode
echo ""
echo "✨ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Open Xcode"
echo "2. File → New → Project"
echo "3. Choose macOS → App"
echo "4. Configure:"
echo "   - Product Name: Arbitra"
echo "   - Team: Your Team"
echo "   - Organization Identifier: com.arbitra"
echo "   - Bundle Identifier: com.arbitra.app"
echo "   - Interface: SwiftUI"
echo "   - Language: Swift"
echo "   - Storage: None"
echo "5. Save in: $PROJECT_DIR"
echo "6. Replace generated files with ArbitraApp contents"
echo ""
echo "Or use Swift Package Manager:"
echo "   swift build"
echo "   swift run ArbitraApp"
echo ""
echo "🎉 Happy coding!"
