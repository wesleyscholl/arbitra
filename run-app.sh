#!/bin/bash
# Build and run Arbitra macOS app

#  Navigate to the project directory if not already there
cd "$(dirname "$0")"

# Build the Swift app
echo "🔨 Building Arbitra..."
swift build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "🚀 Launching Arbitra..."
    
    # Run the app in the background
    .build/debug/ArbitraApp &
    
    # Wait a moment for the app to start
    sleep 2
    
    # Try to activate the app using osascript
    osascript -e 'tell application "System Events" to set frontmost of the first process whose unix id is '$(pgrep -f ArbitraApp)' to true' 2>/dev/null
    
    echo "✨ Arbitra is running!"
    echo "   If the window doesn't appear, press Cmd+Tab to switch to it"
    echo "   or check the Dock for the Arbitra icon"
else
    echo "❌ Build failed!"
    exit 1
fi
