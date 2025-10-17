# DynamoDB MCP Operations

A comprehensive demonstration of DynamoDB operations through Model Context Protocol (MCP) architecture with AI-powered natural language interface using AWS Bedrock.

## 🚀 Features

### Core Capabilities
- **MCP Architecture**: Modular tool-based operations for DynamoDB
- **Multi-Table Support**: 5 pre-configured tables (users, products, orders, reviews, inventory)
- **Natural Language Interface**: AI-powered chat using AWS Bedrock Claude 3 Haiku
- **Real-time Cost Tracking**: Monitor operation costs and capacity usage
- **Dynamic Forms**: Table-specific input forms for all operations

### DynamoDB Extensions
- **🎯 Partition Key Optimizer**: Validates efficient key usage
- **📊 Capacity Planner**: Monitors RCU/WCU and recommends billing modes
- **🔄 Stream Event Adapter**: Generates AI-ready stream events
- **📈 Index Advisor**: Detects inefficient queries and suggests GSI indexes

## 📋 Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS CLI configured or environment variables set
- Required Python packages (see requirements.txt)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd dynamodb-mcp-operations
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure AWS credentials**
```bash
aws configure
# OR set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

4. **Enable Bedrock model access**
   - Go to AWS Bedrock console
   - Request access to Claude 3 Haiku model
   - Ensure IAM permissions for `bedrock:InvokeModel`

## 🚀 Usage

### Run the Demo
```bash
streamlit run enhanced_mcp_demo.py
```

### Access the Interface
- Open browser to `http://localhost:8501`
- Select AWS region for Bedrock
- Choose table from sidebar
- Use tabs to explore different features

### Natural Language Commands
- "Get user with id u001"
- "Create a new product with name iPhone"
- "List all orders where status is pending"
- "Update user u002 set city to Boston"
- "Delete product p003"

## 📁 Project Structure

```
dynamodb-mcp-operations/
├── enhanced_mcp_demo.py          # Main Streamlit application
├── requirements.txt              # Python dependencies
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## 🏗️ Architecture

```
💬 Natural Language Input
        ↓
🤖 AWS Bedrock (Claude 3 Haiku)
        ↓
🔧 MCP Tools (DynamoDB Operations)
        ↓
🗄️ Simulated DynamoDB Tables
        ↓
🚀 Extensions Analysis & Optimization
```

## 📊 Supported Tables

| Table | Partition Key | Fields |
|-------|---------------|--------|
| users | user_id | name, email, age, city |
| products | product_id | name, price, category, rating |
| orders | order_id | user_id, product_id, quantity, total, status |
| reviews | review_id | product_id, user_id, rating, comment, date |
| inventory | item_id | product_id, warehouse, quantity, last_updated |

## 🔧 MCP Operations

- **create_table**: Create new DynamoDB table
- **put_item**: Insert item with stream event generation
- **get_item**: Retrieve single item by key
- **update_item**: Modify existing item
- **delete_item**: Remove item from table
- **query**: Efficient key-based queries with optimization analysis
- **scan**: Full table scan with efficiency warnings

## 🚀 Extensions

### Partition Key Optimizer
- Validates query efficiency
- Warns about expensive scan operations
- Recommends partition key usage

### Capacity Planner
- Tracks RCU/WCU consumption
- Recommends provisioned vs pay-per-request
- Calculates average capacity per operation

### Stream Event Adapter
- Generates DynamoDB Stream-like events
- Creates AI-ready payloads for personalization
- Supports real-time analytics workflows

### Index Advisor
- Detects high scan ratios
- Suggests Global Secondary Indexes (GSI)
- Provides query optimization tips

## 💰 Cost Tracking

- Real-time operation cost calculation
- Per-operation cost breakdown
- Total cost and operation count metrics
- Average cost per operation analysis

## 🔒 Security & Permissions

Required IAM permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "bedrock:InvokeModel",
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
        }
    ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Bedrock Access Denied**
- Ensure model access is enabled in Bedrock console
- Check IAM permissions for bedrock:InvokeModel
- Verify AWS credentials are configured

**Model Not Available**
- Claude 3 Haiku may not be available in all regions
- Try us-east-1 or us-west-2 regions
- Check Bedrock service availability

**Streamlit Issues**
- Ensure all dependencies are installed
- Try `pip install --upgrade streamlit`
- Clear browser cache and restart

## 📞 Support

For issues and questions:
- Create GitHub issue
- Check troubleshooting section
- Review AWS Bedrock documentation

## 🎯 Future Enhancements

- [ ] Real DynamoDB integration
- [ ] Additional LLM providers
- [ ] Advanced query optimization
- [ ] Performance benchmarking
- [ ] Export/import functionality
- [ ] Multi-region support
