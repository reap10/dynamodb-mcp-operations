#!/usr/bin/env python3
"""
Enhanced DynamoDB Operations Through MCP Demo
With DynamoDB-Specific Extensions: Partition Key Optimizer, Capacity Planner, Stream Event Adapter, Index Advisor
"""

import streamlit as st
import json
import boto3
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import uuid

# Page config
st.set_page_config(page_title="Enhanced DynamoDB MCP", page_icon="🚀", layout="wide")

# CSS
st.markdown("""
<style>
.operation-card {
    background: var(--background-color);
    border: 1px solid var(--secondary-background-color);
    border-left: 4px solid #007bff;
    padding: 15px;
    margin: 10px 0;
    border-radius: 8px;
}
.mcp-tool {
    background: rgba(0, 123, 255, 0.1);
    border: 1px solid rgba(0, 123, 255, 0.3);
    padding: 10px;
    margin: 5px 0;
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
    color: var(--text-color);
}
.extension-card {
    background: rgba(40, 167, 69, 0.1);
    border: 1px solid rgba(40, 167, 69, 0.3);
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
.warning-card {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.3);
    padding: 12px;
    border-radius: 4px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Bedrock-powered Natural Language Processor
class NaturalLanguageProcessor:
    """Uses AWS Bedrock to convert natural language to SQL/MCP actions"""
    
    def __init__(self):
        self.bedrock = None
        self.region = 'us-east-1'
    
    def set_credentials(self, region: str = 'us-east-1'):
        """Initialize Bedrock client"""
        self.region = region
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
    
    def parse_request(self, text: str, table_name: str) -> Dict[str, Any]:
        """Parse natural language request using Bedrock"""
        if not self.bedrock:
            return {'action': 'error', 'message': 'Bedrock client not initialized'}
        
        schema = self._get_table_schema(table_name)
        
        prompt = f"""Convert this natural language to DynamoDB action JSON.

Table: {table_name}
Schema: {schema}
Request: "{text}"

Return only JSON:
{{
  "action": "get_item|put_item|update_item|delete_item|scan|query",
  "table_name": "{table_name}",
  "key": {{"field": "value"}},
  "item": {{"field": "value"}},
  "updates": {{"field": "value"}}
}}

Examples:
"Get user jordan" → {{"action": "get_item", "table_name": "{table_name}", "key": {{"user_id": "jordan"}}}}
"Create user jordan" → {{"action": "put_item", "table_name": "{table_name}", "item": {{"user_id": "jordan", "name": "New User"}}}}"""
        
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0
            })
            
            response = self.bedrock.invoke_model(
                body=body,
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            completion = response_body['content'][0]['text']
            
            # Extract JSON from response
            json_start = completion.find('{')
            json_end = completion.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(completion[json_start:json_end])
                return result
            else:
                return {'action': 'error', 'message': 'Could not parse LLM response'}
                
        except Exception as e:
            return {'action': 'error', 'message': f'Bedrock error: {str(e)}'}
    
    def _get_table_schema(self, table_name: str) -> str:
        """Get table schema description"""
        schemas = {
            'users': 'Primary key: user_id. Fields: name, email, age, city',
            'products': 'Primary key: product_id. Fields: name, price, category, rating',
            'orders': 'Primary key: order_id. Fields: user_id, product_id, quantity, total, status',
            'reviews': 'Primary key: review_id. Fields: product_id, user_id, rating, comment, date',
            'inventory': 'Primary key: item_id. Fields: product_id, warehouse, quantity, last_updated'
        }
        return schemas.get(table_name, 'Primary key: id')

# Sample data
SAMPLE_ITEMS = [
    {"user_id": "user001", "name": "Alice Johnson", "email": "alice@example.com", "age": 28, "city": "San Francisco"},
    {"user_id": "user002", "name": "Bob Smith", "email": "bob@example.com", "age": 35, "city": "New York"},
    {"user_id": "user003", "name": "Carol Davis", "email": "carol@example.com", "age": 42, "city": "Chicago"},
    {"user_id": "user004", "name": "David Wilson", "email": "david@example.com", "age": 31, "city": "Austin"},
    {"user_id": "user005", "name": "Eva Brown", "email": "eva@example.com", "age": 26, "city": "Seattle"}
]

# DynamoDB Extensions
class DynamoDBExtensions:
    def __init__(self):
        self.query_patterns = []
        self.capacity_usage = {"RCU": 0, "WCU": 0}
        self.scan_operations = []
        
    def partition_key_optimizer(self, query_pattern: str, uses_partition_key: bool) -> Dict:
        """Validates efficient partition key usage"""
        self.query_patterns.append({"pattern": query_pattern, "uses_pk": uses_partition_key, "timestamp": datetime.now()})
        
        if not uses_partition_key:
            return {
                "status": "warning",
                "message": "Query does not use partition key - will result in expensive scan operation",
                "recommendation": "Modify query to include partition key for better performance",
                "cost_impact": "High - scan operations cost significantly more"
            }
        return {
            "status": "optimal",
            "message": "Query efficiently uses partition key",
            "cost_impact": "Low - efficient key-based access"
        }
    
    def capacity_planner(self, operation_type: str, item_size_kb: float = 1.0) -> Dict:
        """Monitors and recommends capacity adjustments"""
        if operation_type in ["put_item", "update_item", "delete_item"]:
            wcu_consumed = max(1, int(item_size_kb))
            self.capacity_usage["WCU"] += wcu_consumed
        else:
            rcu_consumed = max(1, int(item_size_kb / 4))  # 4KB per RCU
            self.capacity_usage["RCU"] += rcu_consumed
        
        # Calculate recommendations
        total_ops = st.session_state.mcp_costs['operations'] if 'mcp_costs' in st.session_state else 1
        avg_rcu = self.capacity_usage["RCU"] / max(total_ops, 1)
        avg_wcu = self.capacity_usage["WCU"] / max(total_ops, 1)
        
        recommendations = []
        if avg_rcu > 5:
            recommendations.append(f"Consider provisioned RCU: {int(avg_rcu * 1.2)} units")
        if avg_wcu > 5:
            recommendations.append(f"Consider provisioned WCU: {int(avg_wcu * 1.2)} units")
        if not recommendations:
            recommendations.append("Current usage suits pay-per-request billing")
        
        return {
            "current_usage": self.capacity_usage,
            "average_per_operation": {"RCU": avg_rcu, "WCU": avg_wcu},
            "recommendations": recommendations,
            "billing_recommendation": "PROVISIONED" if (avg_rcu > 5 or avg_wcu > 5) else "PAY_PER_REQUEST"
        }
    
    def stream_event_adapter(self, operation: str, item_data: Dict) -> Dict:
        """Converts operations into DynamoDB Stream-like events for AI workflows"""
        stream_event = {
            "eventID": f"stream-{random.randint(100000, 999999)}",
            "eventName": operation.upper(),
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-1",
            "dynamodb": {
                "ApproximateCreationDateTime": datetime.now().timestamp(),
                "Keys": {"user_id": {"S": item_data.get("user_id", "unknown")}},
                "NewImage": {k: {"S": str(v)} for k, v in item_data.items()},
                "SequenceNumber": f"{random.randint(100000000, 999999999)}",
                "SizeBytes": len(json.dumps(item_data)),
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            }
        }
        
        # AI-ready payload
        ai_payload = {
            "user_id": item_data.get("user_id"),
            "operation": operation,
            "data": item_data,
            "timestamp": datetime.now().isoformat(),
            "ai_context": {
                "user_segment": "active" if item_data.get("age", 0) > 25 else "young",
                "location_tier": "tier1" if item_data.get("city") in ["San Francisco", "New York"] else "tier2",
                "engagement_score": random.randint(1, 100)
            }
        }
        
        return {
            "stream_event": stream_event,
            "ai_payload": ai_payload,
            "processing_recommendations": [
                "Send to real-time personalization engine",
                "Update user behavior analytics",
                "Trigger recommendation refresh"
            ]
        }
    
    def index_advisor(self, query_pattern: str, filter_attributes: List[str], result_count: int, scanned_count: int) -> Dict:
        """Detects inefficient queries and suggests indexes"""
        scan_ratio = scanned_count / max(result_count, 1)
        
        self.scan_operations.append({
            "pattern": query_pattern,
            "scan_ratio": scan_ratio,
            "filter_attributes": filter_attributes,
            "timestamp": datetime.now()
        })
        
        recommendations = []
        index_suggestions = []
        
        if scan_ratio > 10:  # Scanning 10x more items than returned
            recommendations.append("⚠️ High scan ratio detected - query is inefficient")
            
            for attr in filter_attributes:
                if attr not in ["user_id"]:
                    index_suggestions.append({
                        "type": "GSI",
                        "partition_key": attr,
                        "name": f"{attr}-index",
                        "benefit": "Convert scan to efficient query operation"
                    })
        
        return {
            "scan_efficiency": {
                "scan_ratio": scan_ratio,
                "status": "efficient" if scan_ratio < 2 else "warning" if scan_ratio < 10 else "critical"
            },
            "recommendations": recommendations,
            "suggested_indexes": index_suggestions,
            "query_optimization_tips": [
                "Use partition key in query conditions",
                "Add sort key conditions when possible",
                "Consider composite keys for complex queries"
            ]
        }

# Enhanced MCP Tools
class EnhancedMCPDynamoDBTools:
    def __init__(self):
        self.operation_costs = {
            "create_table": 0.0,
            "put_item": 0.00125,
            "get_item": 0.00025,
            "query": 0.00025,
            "scan": 0.00025,
            "update_item": 0.00125,
            "delete_item": 0.00125,
            "batch_write": 0.00125,
            "batch_get": 0.00025
        }
        self.extensions = DynamoDBExtensions()
    
    def create_table(self, table_name: str, key_schema: Dict) -> Dict:
        """MCP Tool: Create DynamoDB table"""
        cost = self.operation_costs["create_table"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if table_name in st.session_state.tables:
            return {"success": False, "error": "Table already exists", "cost": cost}
        
        st.session_state.tables[table_name] = {
            "items": {},
            "key_schema": key_schema,
            "created_at": datetime.now(),
            "query_patterns": [],
            "scan_operations": []
        }
        st.session_state.current_table = table_name
        
        return {
            "success": True,
            "table_name": table_name,
            "status": "CREATING",
            "key_schema": key_schema,
            "cost": cost
        }
    
    def put_item(self, table_name: str, item: Dict) -> Dict:
        """MCP Tool: Put item with stream event generation"""
        cost = self.operation_costs["put_item"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if table_name not in st.session_state.tables:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        # Get primary key from item based on table schema
        key_field = st.session_state.tables[table_name]["key_schema"]["partition_key"]
        item_key = item.get(key_field, f"item_{len(st.session_state.tables[table_name]['items'])}")
        st.session_state.tables[table_name]["items"][item_key] = item
        
        # Generate stream event for AI workflows
        stream_data = self.extensions.stream_event_adapter("INSERT", item)
        
        # Capacity analysis
        item_size = len(json.dumps(item)) / 1024  # KB
        capacity_analysis = self.extensions.capacity_planner("put_item", item_size)
        
        return {
            "success": True,
            "item_key": item_key,
            "item": item,
            "cost": cost,
            "stream_event": stream_data["stream_event"],
            "ai_payload": stream_data["ai_payload"],
            "capacity_analysis": capacity_analysis
        }
    
    def query(self, table_name: str, key_condition: str, filter_expression: str = None) -> Dict:
        """MCP Tool: Query with optimization analysis"""
        cost = self.operation_costs["query"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if table_name not in st.session_state.tables:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        # Get partition key for this table
        partition_key = st.session_state.tables[table_name]["key_schema"]["partition_key"]
        uses_partition_key = partition_key in key_condition
        partition_analysis = self.extensions.partition_key_optimizer(key_condition, uses_partition_key)
        
        # Store query pattern for this table
        st.session_state.tables[table_name]["query_patterns"].append({
            "pattern": key_condition,
            "uses_pk": uses_partition_key,
            "timestamp": datetime.now()
        })
        
        # Simulate query results
        results = []
        scanned_items = list(st.session_state.tables[table_name]["items"].values())
        
        for item in scanned_items:
            if "age > 30" in key_condition and item.get("age", 0) > 30:
                results.append(item)
            elif "city = 'San Francisco'" in key_condition and item.get("city") == "San Francisco":
                results.append(item)
            elif "user_id" in key_condition and uses_partition_key:
                results.append(item)
                break  # Efficient partition key lookup
        
        # Capacity planning
        capacity_analysis = self.extensions.capacity_planner("query", 1.0)
        
        # Index analysis
        filter_attrs = []
        if "age" in key_condition: filter_attrs.append("age")
        if "city" in key_condition: filter_attrs.append("city")
        
        index_analysis = self.extensions.index_advisor(
            key_condition, filter_attrs, len(results), len(scanned_items)
        )
        
        return {
            "success": True,
            "items": results[:5],
            "count": len(results),
            "scanned_count": len(scanned_items),
            "cost": cost,
            "optimization_analysis": {
                "partition_key_analysis": partition_analysis,
                "capacity_analysis": capacity_analysis,
                "index_analysis": index_analysis
            }
        }
    
    def scan(self, table_name: str, filter_expression: str = None) -> Dict:
        """MCP Tool: Scan with efficiency warnings"""
        cost = self.operation_costs["scan"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if table_name not in st.session_state.tables:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        items = list(st.session_state.tables[table_name]["items"].values())
        
        # Store scan operation for this table
        st.session_state.tables[table_name]["scan_operations"].append({
            "pattern": f"SCAN with filter: {filter_expression or 'none'}",
            "scan_ratio": len(items),
            "filter_attributes": [],
            "timestamp": datetime.now()
        })
        
        # Analyze scan efficiency
        partition_analysis = self.extensions.partition_key_optimizer("SCAN operation", False)
        capacity_analysis = self.extensions.capacity_planner("scan", len(items) * 0.5)
        
        filter_attrs = []
        if filter_expression:
            if "age" in filter_expression: filter_attrs.append("age")
            if "city" in filter_expression: filter_attrs.append("city")
        
        index_analysis = self.extensions.index_advisor(
            f"SCAN with filter: {filter_expression or 'none'}", 
            filter_attrs, len(items), len(items)
        )
        
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "scanned_count": len(items),
            "cost": cost,
            "optimization_analysis": {
                "partition_key_analysis": partition_analysis,
                "capacity_analysis": capacity_analysis,
                "index_analysis": index_analysis
            }
        }
    
    def get_item(self, table_name: str, key: Dict) -> Dict:
        """MCP Tool: Get single item by key"""
        cost = self.operation_costs["get_item"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if table_name not in st.session_state.tables:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        # Extract key value
        key_field = list(key.keys())[0]
        key_value = key[key_field]
        
        items = st.session_state.tables[table_name]["items"]
        if key_value in items:
            return {
                "success": True,
                "item": items[key_value],
                "cost": cost
            }
        else:
            return {
                "success": False,
                "error": "Item not found",
                "cost": cost
            }
    
    def update_item(self, table_name: str, key: Dict, updates: Dict) -> Dict:
        """MCP Tool: Update item"""
        cost = self.operation_costs["update_item"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if table_name not in st.session_state.tables:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        key_field = list(key.keys())[0]
        key_value = key[key_field]
        
        items = st.session_state.tables[table_name]["items"]
        if key_value in items:
            items[key_value].update(updates)
            return {
                "success": True,
                "updated_item": items[key_value],
                "cost": cost
            }
        else:
            return {
                "success": False,
                "error": "Item not found",
                "cost": cost
            }
    
    def delete_item(self, table_name: str, key: Dict) -> Dict:
        """MCP Tool: Delete item"""
        cost = self.operation_costs["delete_item"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if table_name not in st.session_state.tables:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        key_field = list(key.keys())[0]
        key_value = key[key_field]
        
        items = st.session_state.tables[table_name]["items"]
        if key_value in items:
            deleted_item = items.pop(key_value)
            return {
                "success": True,
                "deleted_item": deleted_item,
                "cost": cost
            }
        else:
            return {
                "success": False,
                "error": "Item not found",
                "cost": cost
            }

# Initialize session state
if 'tables' not in st.session_state:
    st.session_state.tables = {}
if 'current_table' not in st.session_state:
    st.session_state.current_table = None
if 'mcp_costs' not in st.session_state:
    st.session_state.mcp_costs = {"total": 0.0, "operations": 0}
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'nlp' not in st.session_state:
    st.session_state.nlp = NaturalLanguageProcessor()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'bedrock_region' not in st.session_state:
    st.session_state.bedrock_region = 'us-east-1'

# Sample data for different tables
TABLE_SAMPLES = {
    "users": [
        {"user_id": "u001", "name": "Alice Johnson", "email": "alice@example.com", "age": 28, "city": "San Francisco"},
        {"user_id": "u002", "name": "Bob Smith", "email": "bob@example.com", "age": 35, "city": "New York"},
        {"user_id": "u003", "name": "Carol Davis", "email": "carol@example.com", "age": 42, "city": "Chicago"}
    ],
    "products": [
        {"product_id": "p001", "name": "iPhone 15", "category": "electronics", "price": 999, "rating": 4.5},
        {"product_id": "p002", "name": "MacBook Pro", "category": "electronics", "price": 2499, "rating": 4.8},
        {"product_id": "p003", "name": "AirPods", "category": "electronics", "price": 249, "rating": 4.3}
    ],
    "orders": [
        {"order_id": "o001", "user_id": "u001", "product_id": "p001", "quantity": 1, "total": 999, "status": "shipped"},
        {"order_id": "o002", "user_id": "u002", "product_id": "p002", "quantity": 1, "total": 2499, "status": "delivered"},
        {"order_id": "o003", "user_id": "u001", "product_id": "p003", "quantity": 2, "total": 498, "status": "pending"}
    ],
    "reviews": [
        {"review_id": "r001", "product_id": "p001", "user_id": "u001", "rating": 5, "comment": "Great phone!", "date": "2024-01-15"},
        {"review_id": "r002", "product_id": "p002", "user_id": "u002", "rating": 4, "comment": "Excellent laptop", "date": "2024-01-20"}
    ],
    "inventory": [
        {"item_id": "i001", "product_id": "p001", "warehouse": "west", "quantity": 150, "last_updated": "2024-01-10"},
        {"item_id": "i002", "product_id": "p002", "warehouse": "east", "quantity": 75, "last_updated": "2024-01-12"}
    ]
}

# Initialize enhanced MCP tools
mcp_tools = EnhancedMCPDynamoDBTools()

# Initialize sample tables and data
def initialize_sample_data():
    if not st.session_state.initialized:
        # Create 5 tables with different schemas
        table_configs = {
            "users": {"partition_key": "user_id"},
            "products": {"partition_key": "product_id"},
            "orders": {"partition_key": "order_id"},
            "reviews": {"partition_key": "review_id"},
            "inventory": {"partition_key": "item_id"}
        }
        
        for table_name, schema in table_configs.items():
            mcp_tools.create_table(table_name, schema)
            
            # Add sample data
            if table_name in TABLE_SAMPLES:
                for item in TABLE_SAMPLES[table_name]:
                    mcp_tools.put_item(table_name, item)
        
        # Perform some sample operations for analysis
        mcp_tools.query("users", "age > 30")
        mcp_tools.query("products", "category = 'electronics'")
        mcp_tools.scan("orders", "status = 'pending'")
        mcp_tools.query("reviews", "rating > 4")
        
        st.session_state.initialized = True

initialize_sample_data()

# Header
st.title("DynamoDB Operations Through MCP")
st.markdown("**With DynamoDB-Specific Extensions: Partition Key Optimizer, Capacity Planner, Stream Event Adapter, Index Advisor**")

# Sidebar
with st.sidebar:
    st.header("📊 Table Overview")
    
    # Table selection
    tables = list(st.session_state.tables.keys())
    selected_table = st.selectbox("Select Table", tables, key="main_table_select")
    
    # Table stats
    table_data = st.session_state.tables[selected_table]
    st.metric("Items", len(table_data['items']))
    st.metric("Operations", st.session_state.mcp_costs['operations'])
    st.metric("Total Cost", f"${st.session_state.mcp_costs['total']:.4f}")
    
    # Architecture Flow
    st.markdown("---")
    st.subheader("🏗️ Architecture Flow")
    
    flow_diagram = f"""
    ```
    💬 Natural Language
            ↓
    🤖 Bedrock (Claude 3)
            ↓
    🔧 MCP Tools
            ↓
    🗄️ DynamoDB ({selected_table})
            ↓
    🚀 Extensions Analysis
    ```
    """
    st.markdown(flow_diagram)
    
    # Table-specific operations
    st.markdown("---")
    st.subheader(f"🔍 {selected_table.title()} Operations")
    
    table_operations = {
        'users': ['Get by user_id', 'Query by age', 'Query by city', 'Scan all users'],
        'products': ['Get by product_id', 'Query by category', 'Query by price range', 'Scan all products'],
        'orders': ['Get by order_id', 'Query by user_id', 'Query by status', 'Scan all orders'],
        'reviews': ['Get by review_id', 'Query by product_id', 'Query by rating', 'Scan all reviews'],
        'inventory': ['Get by item_id', 'Query by product_id', 'Query by warehouse', 'Scan all inventory']
    }
    
    for op in table_operations.get(selected_table, []):
        st.text(f"• {op}")
    
    # Table-specific extensions
    st.markdown("---")
    st.subheader("🚀 Active Extensions")
    
    table_extensions = {
        'users': ['🎯 User Segmentation', '📊 Age Analytics', '🌍 Location Insights'],
        'products': ['💰 Price Optimization', '🏷️ Category Analysis', '⭐ Rating Trends'],
        'orders': ['📈 Sales Analytics', '🚚 Status Tracking', '💵 Revenue Analysis'],
        'reviews': ['📝 Sentiment Analysis', '⭐ Rating Distribution', '📅 Review Trends'],
        'inventory': ['🏢 Warehouse Analytics', '📉 Stock Levels', '🔄 Reorder Alerts']
    }
    
    for ext in table_extensions.get(selected_table, []):
        st.text(f"• {ext}")

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏗️ Table Operations", "📝 Item Operations", "🔍 Query Operations", "🚀 DynamoDB Extensions", "💬 Chat"])

with tab1:
    st.subheader("Table Management Operations")
    
    # Show existing tables
    if st.session_state.tables:
        st.markdown("### 📊 Existing Tables")
        
        table_df = []
        for table_name, table_data in st.session_state.tables.items():
            table_df.append({
                "Table Name": table_name,
                "Items": len(table_data["items"]),
                "Partition Key": table_data["key_schema"]["partition_key"],
                "Created": table_data["created_at"].strftime("%H:%M:%S")
            })
        
        df = pd.DataFrame(table_df)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
    
    # Create Table
    st.markdown("### Create New Table")
    
    col1, col2 = st.columns(2)
    with col1:
        table_name = st.text_input("Table Name:", value="new-table")
        partition_key = st.text_input("Partition Key:", value="id")
    
    with col2:
        sort_key = st.text_input("Sort Key (optional):", value="")
        billing_mode = st.selectbox("Billing Mode:", ["PAY_PER_REQUEST", "PROVISIONED"])
    
    if st.button("🔧 Create Table via MCP", use_container_width=True):
        key_schema = {"partition_key": partition_key}
        if sort_key:
            key_schema["sort_key"] = sort_key
        
        result = mcp_tools.create_table(table_name, key_schema)
        
        st.markdown(f"""
        <div class="mcp-tool">
            MCP Tool: create_table()<br>
            Parameters: table_name="{table_name}", key_schema={key_schema}<br>
            Cost: ${result['cost']:.4f}
        </div>
        """, unsafe_allow_html=True)
        
        if result["success"]:
            st.success(f"✅ Table Created: {result['table_name']}")
            st.rerun()
        else:
            st.error(f"❌ Error: {result['error']}")

with tab2:
    st.subheader("Item Operations with Stream Events")
    
    if not st.session_state.tables:
        st.warning("⚠️ No tables available")
    else:
        # Table selection
        selected_table = st.selectbox("Select Table:", list(st.session_state.tables.keys()))
        st.session_state.current_table = selected_table
        
        # Show table schema
        schema = st.session_state.tables[selected_table]["key_schema"]
        st.info(f"Table Schema - Partition Key: {schema['partition_key']}")
        # Put Item
        st.markdown("### Put Item")
        
        # Dynamic form based on table
        if selected_table == "users":
            col1, col2 = st.columns(2)
            with col1:
                user_id = st.text_input("User ID:", value=f"u{random.randint(100,999)}")
                name = st.text_input("Name:", value="John Doe")
                email = st.text_input("Email:", value="john@example.com")
            with col2:
                age = st.number_input("Age:", min_value=18, max_value=100, value=30)
                city = st.text_input("City:", value="San Francisco")
            item = {"user_id": user_id, "name": name, "email": email, "age": age, "city": city}
        
        elif selected_table == "products":
            col1, col2 = st.columns(2)
            with col1:
                product_id = st.text_input("Product ID:", value=f"p{random.randint(100,999)}")
                name = st.text_input("Name:", value="New Product")
                category = st.selectbox("Category:", ["electronics", "clothing", "books", "home"])
            with col2:
                price = st.number_input("Price:", min_value=0.01, value=99.99)
                rating = st.slider("Rating:", 1.0, 5.0, 4.0, 0.1)
            item = {"product_id": product_id, "name": name, "category": category, "price": price, "rating": rating}
        
        elif selected_table == "orders":
            col1, col2 = st.columns(2)
            with col1:
                order_id = st.text_input("Order ID:", value=f"o{random.randint(100,999)}")
                user_id = st.text_input("User ID:", value="u001")
                product_id = st.text_input("Product ID:", value="p001")
            with col2:
                quantity = st.number_input("Quantity:", min_value=1, value=1)
                total = st.number_input("Total:", min_value=0.01, value=99.99)
                status = st.selectbox("Status:", ["pending", "shipped", "delivered", "cancelled"])
            item = {"order_id": order_id, "user_id": user_id, "product_id": product_id, "quantity": quantity, "total": total, "status": status}
        
        elif selected_table == "reviews":
            col1, col2 = st.columns(2)
            with col1:
                review_id = st.text_input("Review ID:", value=f"r{random.randint(100,999)}")
                product_id = st.text_input("Product ID:", value="p001")
                user_id = st.text_input("User ID:", value="u001")
            with col2:
                rating = st.slider("Rating:", 1, 5, 4)
                comment = st.text_area("Comment:", value="Great product!")
                date = st.date_input("Date:", value=datetime.now().date())
            item = {"review_id": review_id, "product_id": product_id, "user_id": user_id, "rating": rating, "comment": comment, "date": str(date)}
        
        elif selected_table == "inventory":
            col1, col2 = st.columns(2)
            with col1:
                item_id = st.text_input("Item ID:", value=f"i{random.randint(100,999)}")
                product_id = st.text_input("Product ID:", value="p001")
                warehouse = st.selectbox("Warehouse:", ["west", "east", "central", "north", "south"])
            with col2:
                quantity = st.number_input("Quantity:", min_value=0, value=100)
                last_updated = st.date_input("Last Updated:", value=datetime.now().date())
            item = {"item_id": item_id, "product_id": product_id, "warehouse": warehouse, "quantity": quantity, "last_updated": str(last_updated)}
        
        else:
            st.warning("Unknown table schema")
            item = {}
        
        if st.button("📝 Put Item via MCP", use_container_width=True) and item:
            result = mcp_tools.put_item(selected_table, item)
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: put_item()<br>
                Parameters: item={item}<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success(f"✅ Item added with key: {result['item_key']}")
                
                # Show stream event
                with st.expander("📡 Generated Stream Event for AI"):
                    st.json(result["ai_payload"])
                    st.info("This event can be processed by AI workflows for real-time personalization")
            else:
                st.error(f"❌ Error: {result['error']}")
        
        # Quick add sample data
        if st.button("🚀 Add Sample Data", use_container_width=True):
            if selected_table in TABLE_SAMPLES:
                for item in TABLE_SAMPLES[selected_table]:
                    mcp_tools.put_item(selected_table, item)
                st.success(f"✅ Added sample items to {selected_table} with stream events")
            else:
                st.warning("No sample data available for this table")

with tab3:
    st.subheader("Query Operations with Optimization Analysis")
    
    if not st.session_state.tables:
        st.warning("⚠️ No tables available")
    else:
        # Table selection for queries
        query_table = st.selectbox("Select Table for Query:", list(st.session_state.tables.keys()), key="query_table")
        
        # Show table items count
        items_count = len(st.session_state.tables[query_table]["items"])
        st.info(f"Table '{query_table}' has {items_count} items")
        # Query
        st.markdown("### Query Operation")
        
        # Table-specific query conditions
        query_conditions = {
            'users': ["age > 30", "city = 'San Francisco'", "user_id = 'u001'", "age < 25"],
            'products': ["category = 'electronics'", "price > 100", "product_id = 'p001'", "rating > 4.0"],
            'orders': ["status = 'pending'", "user_id = 'u001'", "order_id = 'o001'", "total > 500"],
            'reviews': ["rating > 4", "product_id = 'p001'", "review_id = 'r001'", "rating = 5"],
            'inventory': ["quantity < 50", "warehouse = 'west'", "item_id = 'i001'", "quantity = 0"]
        }
        
        query_condition = st.selectbox("Query Condition:", query_conditions.get(query_table, ["No conditions available"]))
        
        if st.button("🔍 Query via MCP", use_container_width=True):
            result = mcp_tools.query(query_table, query_condition)
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: query()<br>
                Parameters: key_condition="{query_condition}"<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success(f"✅ Query returned {result['count']} items (scanned {result.get('scanned_count', 0)})")
                if result["items"]:
                    df = pd.DataFrame(result["items"])
                    st.dataframe(df, use_container_width=True)
                
                # Show optimization analysis
                if "optimization_analysis" in result:
                    with st.expander("🔍 Query Optimization Analysis"):
                        analysis = result["optimization_analysis"]
                        
                        # Partition key analysis
                        pk_analysis = analysis["partition_key_analysis"]
                        if pk_analysis["status"] == "optimal":
                            st.success(f"✅ {pk_analysis['message']}")
                        else:
                            st.warning(f"⚠️ {pk_analysis['message']}")
                            st.info(f"💡 {pk_analysis['recommendation']}")
                        
                        # Index recommendations
                        idx_analysis = analysis["index_analysis"]
                        if idx_analysis["suggested_indexes"]:
                            st.markdown("**💡 Index Suggestions:**")
                            for idx in idx_analysis["suggested_indexes"]:
                                st.write(f"• {idx['type']} on {idx['partition_key']}: {idx['benefit']}")
            else:
                st.error(f"❌ Error: {result['error']}")
        
        st.markdown("---")
        
        # Scan
        st.markdown("### Scan Operation")
        
        # Table-specific scan filters
        scan_filters = {
            'users': ["", "age > 25", "city = 'New York'", "name contains 'John'"],
            'products': ["", "price < 100", "category = 'electronics'", "rating > 4.5"],
            'orders': ["", "status = 'delivered'", "total > 100", "quantity > 1"],
            'reviews': ["", "rating >= 4", "comment contains 'great'", "date > '2024-01-01'"],
            'inventory': ["", "quantity > 0", "warehouse = 'east'", "last_updated > '2024-01-01'"]
        }
        
        scan_filter = st.selectbox("Filter Expression:", scan_filters.get(query_table, [""]))
        
        if st.button("📊 Scan Table via MCP", use_container_width=True):
            result = mcp_tools.scan(query_table, scan_filter if scan_filter else None)
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: scan()<br>
                Parameters: filter_expression="{scan_filter or 'None'}"<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success(f"✅ Scan returned {result['count']} items")
                if result["items"]:
                    df = pd.DataFrame(result["items"])
                    st.dataframe(df, use_container_width=True)
                
                # Show scan warnings
                if "optimization_analysis" in result:
                    with st.expander("⚠️ Scan Optimization Analysis"):
                        st.warning("🚨 SCAN operations are expensive and should be avoided when possible")
                        
                        analysis = result["optimization_analysis"]
                        idx_analysis = analysis["index_analysis"]
                        if idx_analysis["suggested_indexes"]:
                            st.markdown("**💡 Consider these indexes to convert SCAN to QUERY:**")
                            for idx in idx_analysis["suggested_indexes"]:
                                st.write(f"• **{idx['type']}** on `{idx['partition_key']}` → {idx['benefit']}")
            else:
                st.error(f"❌ Error: {result['error']}")

with tab4:
    st.subheader("🚀 DynamoDB-Specific Extensions")
    
    if not st.session_state.tables:
        st.warning("⚠️ No tables available for analysis")
    else:
        # Table selection for analysis
        analysis_table = st.selectbox("Select Table for Analysis:", list(st.session_state.tables.keys()), key="analysis_table")
        
        # Show table analysis summary
        table_data = st.session_state.tables[analysis_table]
        st.info(f"Analyzing table '{analysis_table}' with {len(table_data['items'])} items, {len(table_data['query_patterns'])} queries, {len(table_data['scan_operations'])} scans")
        # Partition Key Optimizer
        st.markdown("### 1. 🎯 Partition Key Optimizer")
        
        # Table-specific test queries and partition keys
        test_queries = {
            'users': "age > 30 AND city = 'San Francisco'",
            'products': "category = 'electronics' AND price > 100",
            'orders': "status = 'pending' AND total > 500",
            'reviews': "rating > 4 AND date > '2024-01-01'",
            'inventory': "warehouse = 'west' AND quantity < 50"
        }
        
        partition_keys = {
            'users': 'user_id',
            'products': 'product_id', 
            'orders': 'order_id',
            'reviews': 'review_id',
            'inventory': 'item_id'
        }
        
        test_query = st.text_input("Test Query Pattern:", value=test_queries.get(analysis_table, "test query"))
        pk_field = partition_keys.get(analysis_table, 'id')
        uses_pk = st.checkbox(f"Query uses partition key ({pk_field})", value=False)
        
        if st.button("🔍 Analyze Query Efficiency", use_container_width=True):
            analysis = mcp_tools.extensions.partition_key_optimizer(test_query, uses_pk)
            
            if analysis["status"] == "optimal":
                st.success(f"✅ {analysis['message']}")
            else:
                st.warning(f"⚠️ {analysis['message']}")
                st.info(f"💡 Recommendation: {analysis['recommendation']}")
            
            st.info(f"💰 Cost Impact: {analysis['cost_impact']}")
        
        st.markdown("---")
        
        # Capacity Planner
        st.markdown("### 2. 📊 Capacity Planner")
        
        if st.session_state.mcp_costs['operations'] > 0:
            capacity_analysis = mcp_tools.extensions.capacity_planner("analysis", 1.0)
            
            cap_col1, cap_col2 = st.columns(2)
            
            with cap_col1:
                st.metric("Total RCU Consumed", capacity_analysis["current_usage"]["RCU"])
                st.metric("Total WCU Consumed", capacity_analysis["current_usage"]["WCU"])
            
            with cap_col2:
                st.metric("Avg RCU/Operation", f"{capacity_analysis['average_per_operation']['RCU']:.2f}")
                st.metric("Avg WCU/Operation", f"{capacity_analysis['average_per_operation']['WCU']:.2f}")
            
            st.markdown("**💡 Recommendations:**")
            for rec in capacity_analysis["recommendations"]:
                st.write(f"• {rec}")
            
            st.info(f"🏷️ Recommended Billing: **{capacity_analysis['billing_recommendation']}**")
        else:
            st.info("Perform some operations to see capacity analysis")
        
        st.markdown("---")
        
        # Stream Event Adapter
        st.markdown("### 3. 🔄 Stream Event Adapter")
        
        if st.session_state.tables[analysis_table]['items']:
            sample_item = list(st.session_state.tables[analysis_table]['items'].values())[0]
            
            # Table-specific stream operations
            stream_operations = {
                'users': ['User Registration', 'Profile Update', 'Login Event'],
                'products': ['Product Launch', 'Price Change', 'Inventory Update'],
                'orders': ['Order Placed', 'Status Change', 'Payment Processed'],
                'reviews': ['Review Posted', 'Rating Updated', 'Comment Modified'],
                'inventory': ['Stock Replenished', 'Item Moved', 'Quantity Adjusted']
            }
            
            selected_operation = st.selectbox("Stream Operation Type:", stream_operations.get(analysis_table, ['MODIFY']))
            
            if st.button("🎬 Generate Stream Event for AI", use_container_width=True):
                stream_data = mcp_tools.extensions.stream_event_adapter(selected_operation, sample_item)
                
                stream_col1, stream_col2 = st.columns(2)
                
                with stream_col1:
                    st.markdown("**📡 DynamoDB Stream Event:**")
                    st.json(stream_data["stream_event"])
                
                with stream_col2:
                    st.markdown("**🤖 AI-Ready Payload:**")
                    st.json(stream_data["ai_payload"])
                
                st.markdown("**🔧 Processing Recommendations:**")
                for rec in stream_data["processing_recommendations"]:
                    st.write(f"• {rec}")
        else:
            st.info("Add some items to generate stream events")
        
        st.markdown("---")
        
        # Index Advisor
        st.markdown("### 4. 📈 Index Advisor")
        
        table_data = st.session_state.tables[analysis_table]
        
        if table_data['query_patterns'] or table_data['scan_operations']:
            st.markdown(f"**Query Analysis for '{analysis_table}' Table:**")
            
            # Show query patterns
            if table_data['query_patterns']:
                st.markdown("**Query Patterns:**")
                for i, pattern in enumerate(table_data['query_patterns'][-3:]):
                    with st.expander(f"Query {i+1}: {pattern['pattern'][:50]}..."):
                        st.write(f"**Uses Partition Key:** {'✅' if pattern['uses_pk'] else '❌'}")
                        st.write(f"**Pattern:** {pattern['pattern']}")
                        st.write(f"**Timestamp:** {pattern['timestamp'].strftime('%H:%M:%S')}")
            
            # Show scan operations
            if table_data['scan_operations']:
                st.markdown("**Scan Operations:**")
                for i, scan in enumerate(table_data['scan_operations'][-3:]):
                    with st.expander(f"Scan {i+1}: {scan['pattern'][:50]}..."):
                        st.write(f"**Items Scanned:** {scan['scan_ratio']}")
                        st.write(f"**Pattern:** {scan['pattern']}")
                        st.write(f"**Timestamp:** {scan['timestamp'].strftime('%H:%M:%S')}")
            
            # Get latest analysis
            if mcp_tools.extensions.scan_operations:
                latest_op = mcp_tools.extensions.scan_operations[-1]
                analysis = mcp_tools.extensions.index_advisor(
                    latest_op['pattern'], 
                    latest_op['filter_attributes'], 
                    5, 10  # Sample values
                )
                
                st.markdown("**🎯 Index Recommendations:**")
                
                efficiency = analysis["scan_efficiency"]
                if efficiency["status"] == "critical":
                    st.error(f"❌ Critical: Scan ratio {efficiency['scan_ratio']:.1f}x")
                elif efficiency["status"] == "warning":
                    st.warning(f"⚠️ Warning: Scan ratio {efficiency['scan_ratio']:.1f}x")
                else:
                    st.success(f"✅ Efficient: Scan ratio {efficiency['scan_ratio']:.1f}x")
                
                if analysis["suggested_indexes"]:
                    st.markdown("**💡 Suggested Indexes:**")
                    for idx in analysis["suggested_indexes"]:
                        st.write(f"• **{idx['type']}**: {idx['name']} on {idx['partition_key']}")
                        st.write(f"  Benefit: {idx['benefit']}")
                
                st.markdown("**🔧 Optimization Tips:**")
                for tip in analysis["query_optimization_tips"]:
                    st.write(f"• {tip}")
        else:
            st.info("Perform some query/scan operations to see index recommendations")

with tab5:
    st.subheader("💬 Natural Language Chat (Bedrock-Powered)")
    st.markdown("Ask me to perform DynamoDB operations using natural language powered by AWS Bedrock!")
    
    # Region selection
    region = st.selectbox("AWS Region:", ['us-east-1', 'us-west-2', 'eu-west-1'], index=0)
    if region != st.session_state.bedrock_region:
        st.session_state.bedrock_region = region
        st.session_state.nlp.set_credentials(region)
    
    # Initialize Bedrock
    try:
        st.session_state.nlp.set_credentials(region)
        st.success("✅ Bedrock client initialized")
    except Exception as e:
        st.error(f"❌ Bedrock initialization failed: {str(e)}")
        st.info("💡 Make sure AWS credentials are configured (AWS CLI, IAM role, or environment variables)")
        st.stop()
    
    # Chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Table selection for chat
        chat_table = st.selectbox("Select Table for Operations", list(st.session_state.tables.keys()), key="chat_table_select")
    
    with col2:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Chat history display
    chat_container = st.container(height=400)
    with chat_container:
        for i, msg in enumerate(st.session_state.chat_history):
            if msg['type'] == 'user':
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Assistant:** {msg['content']}")
                if 'result' in msg:
                    with st.expander("View Result", expanded=False):
                        st.json(msg['result'])
    
    # Chat input
    user_input = st.chat_input("Type your request... (e.g., 'Get user with id u001', 'List all products', 'Create a new user')")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'type': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process the request
        action = st.session_state.nlp.parse_request(user_input, chat_table)
        
        # Display parsed action
        st.markdown(f"**🔍 Parsed Action:** `{action}`")
        
        if action['action'] in ['unknown', 'error']:
            response = action.get('message', 'Could not understand request')
            result = None
        else:
            # Execute the action
            try:
                if action['action'] == 'get_item':
                    result = mcp_tools.get_item(action['table_name'], action['key'])
                    response = f"Retrieved item from {action['table_name']}"
                
                elif action['action'] == 'put_item':
                    result = mcp_tools.put_item(action['table_name'], action['item'])
                    response = f"Created new item in {action['table_name']}"
                
                elif action['action'] == 'update_item':
                    result = mcp_tools.update_item(action['table_name'], action['key'], action['updates'])
                    response = f"Updated item in {action['table_name']}"
                
                elif action['action'] == 'delete_item':
                    result = mcp_tools.delete_item(action['table_name'], action['key'])
                    response = f"Deleted item from {action['table_name']}"
                
                elif action['action'] == 'scan':
                    result = mcp_tools.scan(action['table_name'], None)
                    response = f"Scanned {action['table_name']} - found {len(result.get('items', []))} items"
                
                elif action['action'] == 'query':
                    result = mcp_tools.query(action['table_name'], action['key_condition'])
                    response = f"Queried {action['table_name']} - found {len(result.get('items', []))} items"
                
                else:
                    response = "Action not supported yet"
                    result = None
            
            except Exception as e:
                response = f"Error executing action: {str(e)}"
                result = None
        
        # Add assistant response to history
        assistant_msg = {
            'type': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        }
        if result:
            assistant_msg['result'] = result
        
        st.session_state.chat_history.append(assistant_msg)
        st.rerun()
    
    # Example requests
    st.subheader("💡 Example Requests")
    examples = [
        "Get user with id u001",
        "List all products",
        "Create a new user",
        "Update user u002 set name=Alice",
        "Delete product p003",
        "Show me all orders",
        "Find items where category electronics"
    ]
    
    for example in examples:
        if st.button(example, key=f"example_{hash(example)}", use_container_width=True):
            # Add user message
            st.session_state.chat_history.append({
                'type': 'user',
                'content': example,
                'timestamp': datetime.now().isoformat()
            })
            
            # Process immediately
            action = st.session_state.nlp.parse_request(example, chat_table)
            
            if action['action'] in ['unknown', 'error']:
                response = action.get('message', 'Could not understand request')
                result = None
            else:
                try:
                    if action['action'] == 'get_item':
                        result = mcp_tools.get_item(action['table_name'], action['key'])
                        response = f"Retrieved item from {action['table_name']}"
                    elif action['action'] == 'put_item':
                        result = mcp_tools.put_item(action['table_name'], action['item'])
                        response = f"Created new item in {action['table_name']}"
                    elif action['action'] == 'update_item':
                        result = mcp_tools.update_item(action['table_name'], action['key'], action['updates'])
                        response = f"Updated item in {action['table_name']}"
                    elif action['action'] == 'delete_item':
                        result = mcp_tools.delete_item(action['table_name'], action['key'])
                        response = f"Deleted item from {action['table_name']}"
                    elif action['action'] == 'scan':
                        result = mcp_tools.scan(action['table_name'], None)
                        response = f"Scanned {action['table_name']} - found {len(result.get('items', []))} items"
                    elif action['action'] == 'query':
                        result = mcp_tools.query(action['table_name'], action['key_condition'])
                        response = f"Queried {action['table_name']} - found {len(result.get('items', []))} items"
                    else:
                        response = "Action not supported"
                        result = None
                except Exception as e:
                    response = f"Error: {str(e)}"
                    result = None
            
            # Add response
            assistant_msg = {
                'type': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            }
            if result:
                assistant_msg['result'] = result
            
            st.session_state.chat_history.append(assistant_msg)
            st.rerun()

# Operation Summary
if st.session_state.mcp_costs['operations'] > 0:
    st.markdown("---")
    st.subheader("📈 Enhanced Operation Summary")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Total Operations", st.session_state.mcp_costs['operations'])
    
    with summary_col2:
        st.metric("Total Cost", f"${st.session_state.mcp_costs['total']:.4f}")
    
    with summary_col3:
        avg_cost = st.session_state.mcp_costs['total'] / st.session_state.mcp_costs['operations']
        st.metric("Avg Cost/Op", f"${avg_cost:.4f}")
    
    with summary_col4:
        extensions_used = len([x for x in [
            mcp_tools.extensions.query_patterns,
            mcp_tools.extensions.scan_operations
        ] if x])
        st.metric("Extensions Used", extensions_used)

# Reset button
if st.button("🔄 Reset All Data", use_container_width=True):
    st.session_state.tables = {}
    st.session_state.current_table = None
    st.session_state.mcp_costs = {"total": 0.0, "operations": 0}
    st.session_state.initialized = False
    # Reset extensions and chat
    mcp_tools.extensions = DynamoDBExtensions()
    st.session_state.chat_history = []
    st.rerun()