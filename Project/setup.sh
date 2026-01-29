#!/bin/bash

echo ""
echo "================================"
echo "Legal CBR System - Quick Setup"
echo "================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found!"
    echo "Please install Node.js from: https://nodejs.org/"
    echo "Then run this script again."
    exit 1
fi

echo "✅ Node.js found"
node --version

# Install dependencies
echo ""
echo "Installing dependencies..."
npm install

# Start the server
echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting web server..."
echo "📱 Opening http://localhost:3000 in your browser..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || echo "Open http://localhost:3000 in your browser"
npm start
