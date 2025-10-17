# 🔧 MCP DynamoDB Tools Reference

## Available MCP Tools

### Table Management Tools

#### `create_table`
**Purpose**: Create a new DynamoDB table
**Parameters**:
- `table_name` (string): Name of the table
- `key_schema` (object): Primary key configuration
- `billing_mode` (string): PAY_PER_REQUEST or PROVISIONED

**Example**:
```json
{
  "tool": "create_table",
  "parameters": {
    "table_name": "users-table",
    "key_schema": {"partition_key": "user_id"},
    "billing_mode": "PAY_PER_REQUEST"
  }
}
```

#### `describe_table`
**Purpose**: Get table information and status
**Parameters**:
- `table_name` (string): Name of the table

#### `delete_table`
**Purpose**: Delete a DynamoDB table
**Parameters**:
- `table_name` (string): Name of the table to delete

### Item Operations Tools

#### `put_item`
**Purpose**: Insert or replace an item
**Parameters**:
- `table_name` (string): Target table name
- `item` (object): Item data to insert

**Example**:
```json
{
  "tool": "put_item",
  "parameters": {
    "table_name": "users-table",
    "item": {
      "user_id": "user001",
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30
    }
  }
}
```

#### `get_item`
**Purpose**: Retrieve an item by primary key
**Parameters**:
- `table_name` (string): Source table name
- `key` (object): Primary key values

**Example**:
```json
{
  "tool": "get_item",
  "parameters": {
    "table_name": "users-table",
    "key": {"user_id": "user001"}
  }
}
```

#### `update_item`
**Purpose**: Modify an existing item
**Parameters**:
- `table_name` (string): Target table name
- `key` (object): Primary key values
- `update_expression` (string): Update expression
- `expression_values` (object): Values for the expression

**Example**:
```json
{
  "tool": "update_item",
  "parameters": {
    "table_name": "users-table",
    "key": {"user_id": "user001"},
    "update_expression": "SET age = :age, city = :city",
    "expression_values": {":age": 35, ":city": "San Francisco"}
  }
}
```

#### `delete_item`
**Purpose**: Remove an item from the table
**Parameters**:
- `table_name` (string): Target table name
- `key` (object): Primary key values

### Query Operations Tools

#### `query`
**Purpose**: Query items with conditions
**Parameters**:
- `table_name` (string): Source table name
- `key_condition` (string): Key condition expression
- `filter_expression` (string, optional): Additional filter

**Example**:
```json
{
  "tool": "query",
  "parameters": {
    "table_name": "users-table",
    "key_condition": "user_id = :uid",
    "expression_values": {":uid": "user001"}
  }
}
```

#### `scan`
**Purpose**: Scan entire table with optional filters
**Parameters**:
- `table_name` (string): Source table name
- `filter_expression` (string, optional): Filter expression
- `limit` (number, optional): Maximum items to return

**Example**:
```json
{
  "tool": "scan",
  "parameters": {
    "table_name": "users-table",
    "filter_expression": "age > :min_age",
    "expression_values": {":min_age": 25}
  }
}
```

### Batch Operations Tools

#### `batch_write_item`
**Purpose**: Write multiple items in a single request
**Parameters**:
- `table_name` (string): Target table name
- `items` (array): Array of items to write

**Example**:
```json
{
  "tool": "batch_write_item",
  "parameters": {
    "table_name": "users-table",
    "items": [
      {"user_id": "user001", "name": "Alice"},
      {"user_id": "user002", "name": "Bob"}
    ]
  }
}
```

#### `batch_get_item`
**Purpose**: Retrieve multiple items in a single request
**Parameters**:
- `table_name` (string): Source table name
- `keys` (array): Array of primary key values

## Cost Structure

| Operation | Cost per Request |
|-----------|------------------|
| create_table | $0.0000 |
| put_item | $0.00125 |
| get_item | $0.00025 |
| query | $0.00025 |
| scan | $0.00025 |
| update_item | $0.00125 |
| delete_item | $0.00125 |
| batch_write | $0.00125 per item |
| batch_get | $0.00025 per item |

## Error Handling

All MCP tools return a consistent response format:

**Success Response**:
```json
{
  "success": true,
  "data": {...},
  "cost": 0.00125
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error description",
  "cost": 0.00125
}
```

## Best Practices

1. **Use batch operations** for multiple items
2. **Query instead of scan** when possible
3. **Use projection expressions** to limit returned data
4. **Monitor costs** with the built-in cost tracking
5. **Handle errors gracefully** with proper error checking