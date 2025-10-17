#!/usr/bin/env python3
"""
Core DynamoDB Operations Through MCP Demo
Interactive demonstration of all essential DynamoDB operations via MCP tools
"""

import streamlit as st
import json
import boto3
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd

# Page config
st.set_page_config(page_title="DynamoDB MCP Operations", page_icon="🗄️", layout="wide")

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
.success-result {
    background: rgba(40, 167, 69, 0.1);
    border: 1px solid rgba(40, 167, 69, 0.3);
    padding: 12px;
    border-radius: 4px;
    margin: 10px 0;
}
.error-result {
    background: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220, 53, 69, 0.3);
    padding: 12px;
    border-radius: 4px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Sample data for operations
SAMPLE_ITEMS = [
    {"user_id": "user001", "name": "Alice Johnson", "email": "alice@example.com", "age": 28, "city": "San Francisco"},
    {"user_id": "user002", "name": "Bob Smith", "email": "bob@example.com", "age": 35, "city": "New York"},
    {"user_id": "user003", "name": "Carol Davis", "email": "carol@example.com", "age": 42, "city": "Chicago"},
    {"user_id": "user004", "name": "David Wilson", "email": "david@example.com", "age": 31, "city": "Austin"},
    {"user_id": "user005", "name": "Eva Brown", "email": "eva@example.com", "age": 26, "city": "Seattle"}
]

# Initialize session state
if 'table_exists' not in st.session_state:
    st.session_state.table_exists = False
if 'table_items' not in st.session_state:
    st.session_state.table_items = {}
if 'operation_history' not in st.session_state:
    st.session_state.operation_history = []
if 'mcp_costs' not in st.session_state:
    st.session_state.mcp_costs = {"total": 0.0, "operations": 0}

# MCP Tool Simulator
class MCPDynamoDBTools:
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
    
    def create_table(self, table_name: str, key_schema: Dict) -> Dict:
        """MCP Tool: Create DynamoDB table"""
        cost = self.operation_costs["create_table"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if st.session_state.table_exists:
            return {"success": False, "error": "Table already exists", "cost": cost}
        
        st.session_state.table_exists = True
        st.session_state.table_items = {}
        
        return {
            "success": True,
            "table_name": table_name,
            "status": "CREATING",
            "key_schema": key_schema,
            "cost": cost
        }
    
    def put_item(self, table_name: str, item: Dict) -> Dict:
        """MCP Tool: Put item into DynamoDB"""
        cost = self.operation_costs["put_item"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if not st.session_state.table_exists:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        item_key = item.get("user_id", f"item_{len(st.session_state.table_items)}")
        st.session_state.table_items[item_key] = item
        
        return {
            "success": True,
            "item_key": item_key,
            "item": item,
            "cost": cost
        }
    
    def get_item(self, table_name: str, key: Dict) -> Dict:
        """MCP Tool: Get item from DynamoDB"""
        cost = self.operation_costs["get_item"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if not st.session_state.table_exists:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        item_key = key.get("user_id")
        item = st.session_state.table_items.get(item_key)
        
        if item:
            return {"success": True, "item": item, "cost": cost}
        else:
            return {"success": False, "error": "Item not found", "cost": cost}
    
    def query(self, table_name: str, key_condition: str, filter_expression: str = None) -> Dict:
        """MCP Tool: Query DynamoDB table"""
        cost = self.operation_costs["query"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if not st.session_state.table_exists:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        # Simulate query results
        results = []
        for item in st.session_state.table_items.values():
            if "age > 30" in key_condition and item.get("age", 0) > 30:
                results.append(item)
            elif "city = 'San Francisco'" in key_condition and item.get("city") == "San Francisco":
                results.append(item)
            elif len(results) == 0:  # Return first item if no specific condition
                results.append(item)
        
        return {
            "success": True,
            "items": results[:5],  # Limit to 5 items
            "count": len(results),
            "cost": cost
        }
    
    def scan(self, table_name: str, filter_expression: str = None) -> Dict:
        """MCP Tool: Scan DynamoDB table"""
        cost = self.operation_costs["scan"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if not st.session_state.table_exists:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        items = list(st.session_state.table_items.values())
        
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "scanned_count": len(items),
            "cost": cost
        }
    
    def update_item(self, table_name: str, key: Dict, update_expression: str, expression_values: Dict) -> Dict:
        """MCP Tool: Update item in DynamoDB"""
        cost = self.operation_costs["update_item"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if not st.session_state.table_exists:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        item_key = key.get("user_id")
        if item_key in st.session_state.table_items:
            # Simple update simulation
            item = st.session_state.table_items[item_key]
            for attr, value in expression_values.items():
                if attr.startswith(":"):
                    attr_name = attr[1:]  # Remove ':'
                    if "age" in update_expression:
                        item["age"] = value
                    elif "city" in update_expression:
                        item["city"] = value
            
            return {"success": True, "updated_item": item, "cost": cost}
        else:
            return {"success": False, "error": "Item not found", "cost": cost}
    
    def delete_item(self, table_name: str, key: Dict) -> Dict:
        """MCP Tool: Delete item from DynamoDB"""
        cost = self.operation_costs["delete_item"]
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if not st.session_state.table_exists:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        item_key = key.get("user_id")
        if item_key in st.session_state.table_items:
            deleted_item = st.session_state.table_items.pop(item_key)
            return {"success": True, "deleted_item": deleted_item, "cost": cost}
        else:
            return {"success": False, "error": "Item not found", "cost": cost}
    
    def batch_write_item(self, table_name: str, items: List[Dict]) -> Dict:
        """MCP Tool: Batch write items to DynamoDB"""
        cost = self.operation_costs["batch_write"] * len(items)
        st.session_state.mcp_costs["total"] += cost
        st.session_state.mcp_costs["operations"] += 1
        
        if not st.session_state.table_exists:
            return {"success": False, "error": "Table does not exist", "cost": cost}
        
        processed_items = []
        for item in items:
            item_key = item.get("user_id", f"batch_{len(processed_items)}")
            st.session_state.table_items[item_key] = item
            processed_items.append(item_key)
        
        return {
            "success": True,
            "processed_items": processed_items,
            "count": len(processed_items),
            "cost": cost
        }

# Initialize MCP tools
mcp_tools = MCPDynamoDBTools()

# Header
st.title("🗄️ Core DynamoDB Operations Through MCP")
st.markdown("**Interactive demonstration of all essential DynamoDB operations using MCP tools**")

# Sidebar - MCP Status
with st.sidebar:
    st.header("🔧 MCP Status")
    
    st.markdown("""
    <div class="mcp-tool">
        <strong>DynamoDB MCP Server</strong><br>
        Status: 🟢 Active<br>
        Tools: 8 available
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("💰 Operation Costs")
    st.metric("Total Cost", f"${st.session_state.mcp_costs['total']:.4f}")
    st.metric("Operations", st.session_state.mcp_costs['operations'])
    
    if st.session_state.table_exists:
        st.markdown("---")
        st.subheader("📊 Table Status")
        st.success("✅ Table Active")
        st.metric("Items Count", len(st.session_state.table_items))

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Table Operations", "📝 Item Operations", "🔍 Query Operations", "📊 Batch Operations"])

with tab1:
    st.subheader("Table Management Operations")
    
    # Create Table
    st.markdown("### 1. Create Table")
    
    col1, col2 = st.columns(2)
    with col1:
        table_name = st.text_input("Table Name:", value="users-table")
        partition_key = st.text_input("Partition Key:", value="user_id")
    
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
            st.markdown(f"""
            <div class="success-result">
                ✅ <strong>Table Created Successfully</strong><br>
                Table: {result['table_name']}<br>
                Status: {result['status']}<br>
                Key Schema: {result['key_schema']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-result">
                ❌ <strong>Error:</strong> {result['error']}
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.subheader("Item CRUD Operations")
    
    if not st.session_state.table_exists:
        st.warning("⚠️ Create a table first in the Table Operations tab")
    else:
        # Put Item
        st.markdown("### 1. Put Item")
        
        col1, col2 = st.columns(2)
        with col1:
            user_id = st.text_input("User ID:", value=f"user{random.randint(100,999)}")
            name = st.text_input("Name:", value="John Doe")
            email = st.text_input("Email:", value="john@example.com")
        
        with col2:
            age = st.number_input("Age:", min_value=18, max_value=100, value=30)
            city = st.text_input("City:", value="San Francisco")
        
        if st.button("📝 Put Item via MCP", use_container_width=True):
            item = {"user_id": user_id, "name": name, "email": email, "age": age, "city": city}
            result = mcp_tools.put_item(table_name, item)
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: put_item()<br>
                Parameters: item={item}<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success(f"✅ Item added with key: {result['item_key']}")
            else:
                st.error(f"❌ Error: {result['error']}")
        
        # Quick add sample data
        if st.button("🚀 Add Sample Data (5 items)", use_container_width=True):
            for item in SAMPLE_ITEMS:
                mcp_tools.put_item(table_name, item)
            st.success("✅ Added 5 sample items")
        
        st.markdown("---")
        
        # Get Item
        st.markdown("### 2. Get Item")
        
        get_user_id = st.text_input("User ID to retrieve:", value="user001")
        
        if st.button("🔍 Get Item via MCP", use_container_width=True):
            result = mcp_tools.get_item(table_name, {"user_id": get_user_id})
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: get_item()<br>
                Parameters: key={{"user_id": "{get_user_id}"}}<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.json(result["item"])
            else:
                st.error(f"❌ Error: {result['error']}")
        
        st.markdown("---")
        
        # Update Item
        st.markdown("### 3. Update Item")
        
        update_col1, update_col2 = st.columns(2)
        with update_col1:
            update_user_id = st.text_input("User ID to update:", value="user001")
            new_age = st.number_input("New Age:", min_value=18, max_value=100, value=35)
        
        with update_col2:
            new_city = st.text_input("New City:", value="Los Angeles")
        
        if st.button("✏️ Update Item via MCP", use_container_width=True):
            result = mcp_tools.update_item(
                table_name, 
                {"user_id": update_user_id},
                "SET age = :age, city = :city",
                {":age": new_age, ":city": new_city}
            )
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: update_item()<br>
                Parameters: key={{"user_id": "{update_user_id}"}}, updates={{"age": {new_age}, "city": "{new_city}"}}<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success("✅ Item updated successfully")
                st.json(result["updated_item"])
            else:
                st.error(f"❌ Error: {result['error']}")
        
        st.markdown("---")
        
        # Delete Item
        st.markdown("### 4. Delete Item")
        
        delete_user_id = st.text_input("User ID to delete:", value="user005")
        
        if st.button("🗑️ Delete Item via MCP", use_container_width=True):
            result = mcp_tools.delete_item(table_name, {"user_id": delete_user_id})
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: delete_item()<br>
                Parameters: key={{"user_id": "{delete_user_id}"}}<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success("✅ Item deleted successfully")
                st.json(result["deleted_item"])
            else:
                st.error(f"❌ Error: {result['error']}")

with tab3:
    st.subheader("Query & Scan Operations")
    
    if not st.session_state.table_exists:
        st.warning("⚠️ Create a table first and add some items")
    else:
        # Query
        st.markdown("### 1. Query Operation")
        
        query_condition = st.selectbox("Query Condition:", [
            "age > 30",
            "city = 'San Francisco'",
            "user_id begins_with 'user00'"
        ])
        
        if st.button("🔍 Query via MCP", use_container_width=True):
            result = mcp_tools.query(table_name, query_condition)
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: query()<br>
                Parameters: key_condition="{query_condition}"<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success(f"✅ Query returned {result['count']} items")
                if result["items"]:
                    df = pd.DataFrame(result["items"])
                    st.dataframe(df, use_container_width=True)
            else:
                st.error(f"❌ Error: {result['error']}")
        
        st.markdown("---")
        
        # Scan
        st.markdown("### 2. Scan Operation")
        
        scan_filter = st.text_input("Filter Expression (optional):", value="")
        
        if st.button("📊 Scan Table via MCP", use_container_width=True):
            result = mcp_tools.scan(table_name, scan_filter if scan_filter else None)
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: scan()<br>
                Parameters: filter_expression="{scan_filter or 'None'}"<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success(f"✅ Scan returned {result['count']} items (scanned {result['scanned_count']})")
                if result["items"]:
                    df = pd.DataFrame(result["items"])
                    st.dataframe(df, use_container_width=True)
            else:
                st.error(f"❌ Error: {result['error']}")

with tab4:
    st.subheader("Batch Operations")
    
    if not st.session_state.table_exists:
        st.warning("⚠️ Create a table first")
    else:
        # Batch Write
        st.markdown("### 1. Batch Write Items")
        
        batch_count = st.slider("Number of items to batch write:", 1, 10, 3)
        
        if st.button("📦 Batch Write via MCP", use_container_width=True):
            batch_items = []
            for i in range(batch_count):
                item = {
                    "user_id": f"batch_user_{i+1}",
                    "name": f"Batch User {i+1}",
                    "email": f"batch{i+1}@example.com",
                    "age": random.randint(20, 60),
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston"])
                }
                batch_items.append(item)
            
            result = mcp_tools.batch_write_item(table_name, batch_items)
            
            st.markdown(f"""
            <div class="mcp-tool">
                MCP Tool: batch_write_item()<br>
                Parameters: items_count={len(batch_items)}<br>
                Cost: ${result['cost']:.4f}
            </div>
            """, unsafe_allow_html=True)
            
            if result["success"]:
                st.success(f"✅ Batch wrote {result['count']} items")
                st.json(result["processed_items"])
            else:
                st.error(f"❌ Error: {result['error']}")

# Operation History
if st.session_state.mcp_costs['operations'] > 0:
    st.markdown("---")
    st.subheader("📈 Operation Summary")
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.metric("Total Operations", st.session_state.mcp_costs['operations'])
    
    with summary_col2:
        st.metric("Total Cost", f"${st.session_state.mcp_costs['total']:.4f}")
    
    with summary_col3:
        avg_cost = st.session_state.mcp_costs['total'] / st.session_state.mcp_costs['operations']
        st.metric("Avg Cost/Op", f"${avg_cost:.4f}")

# Reset button
if st.button("🔄 Reset All Data", use_container_width=True):
    st.session_state.table_exists = False
    st.session_state.table_items = {}
    st.session_state.operation_history = []
    st.session_state.mcp_costs = {"total": 0.0, "operations": 0}
    st.rerun()