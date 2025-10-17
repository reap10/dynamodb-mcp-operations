#!/bin/bash

echo "🗄️ Core DynamoDB Operations Through MCP Demo"
echo "=============================================="
echo ""
echo "🔧 MCP Tools Available:"
echo "   📝 Table Operations: create, describe, delete"
echo "   📊 Item Operations: put, get, update, delete"
echo "   🔍 Query Operations: query, scan"
echo "   📦 Batch Operations: batch_write, batch_get"
echo ""
echo "Installing requirements..."
pip3 install -r requirements.txt

echo ""
echo "🚀 Starting DynamoDB MCP Demo..."
echo "💡 Interactive UI to test all DynamoDB operations!"
echo ""

streamlit run enhanced_mcp_demo.py