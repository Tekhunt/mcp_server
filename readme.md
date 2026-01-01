# Pydantic MCP Server

A Model Context Protocol (MCP) server with type-safe tool inputs and structured outputs using Pydantic models. This server provides utility tools accessible via SSE (Server-Sent Events) HTTP transport.

## 🚀 Features

- **Type-safe inputs** using Pydantic validation
- **Structured JSON outputs** for all tools
- **SSE HTTP transport** for real-time communication
- **Input validation** with helpful error messages
- **Security features** (path traversal protection, sanitization)
- **Production-ready** deployment to Render

## 📋 Available Tools

### 1. **calculate**
Perform arithmetic calculations with validated inputs.

**Parameters:**
- `operation` (string): Operation type - `add`, `subtract`, `multiply`, or `divide`
- `a` (number): First operand
- `b` (number): Second operand

**Validation:**
- Prevents division by zero
- Validates operation type

**Example:**
```json
{
  "operation": "multiply",
  "a": 5,
  "b": 3
}
```

**Response:**
```json
{
  "operation": "multiply",
  "operand_a": 5.0,
  "operand_b": 3.0,
  "result": 15.0,
  "formatted": "5.0 multiply 3.0 = 15.0",
  "timestamp": "2025-01-01T12:00:00"
}
```

---

### 2. **get_weather**
Get weather information for a specified city.

**Parameters:**
- `city` (string): City name (1-100 characters)

**Validation:**
- Trims whitespace
- Validates length

**Example:**
```json
{
  "city": "San Francisco"
}
```

**Response:**
```json
{
  "city": "San Francisco",
  "temperature": "72°F",
  "temperature_celsius": 22.2,
  "condition": "Sunny",
  "humidity": "45%",
  "wind": "10 mph",
  "timestamp": "2025-01-01T12:00:00"
}
```

---

### 3. **save_note**
Save a note with optional tags to a file.

**Parameters:**
- `title` (string): Note title (1-100 characters)
- `content` (string): Note content (minimum 1 character)
- `tags` (array, optional): List of tags for categorization

**Validation:**
- Sanitizes title for safe filename
- Removes special characters
- Validates alphanumeric content

**Example:**
```json
{
  "title": "Meeting Notes",
  "content": "Discussed Q1 goals and project timeline",
  "tags": ["work", "planning", "q1"]
}
```

**Response:**
```json
{
  "filename": "note_Meeting_Notes.txt",
  "title": "Meeting Notes",
  "content_length": 42,
  "tags": ["work", "planning", "q1"],
  "created_at": "2025-01-01T12:00:00",
  "success": true,
  "message": "Note successfully saved to note_Meeting_Notes.txt"
}
```

---

### 4. **convert_temperature**
Convert temperature from Fahrenheit to Celsius.

**Parameters:**
- `temperature_fahrenheit` (number): Temperature in Fahrenheit

**Validation:**
- Ensures temperature is above absolute zero (-459.67°F)

**Example:**
```json
{
  "temperature_fahrenheit": 98.6
}
```

**Response:**
```json
{
  "fahrenheit": 98.6,
  "celsius": 37.0,
  "formatted": "98.6°F = 37.00°C",
  "timestamp": "2025-01-01T12:00:00"
}
```

---

### 5. **read_file**
Read contents of a file with path traversal protection.

**Parameters:**
- `filename` (string): Name of file to read

**Validation:**
- Prevents path traversal attacks
- Only allows basename (no directory paths)

**Example:**
```json
{
  "filename": "example.txt"
}
```

**Response:**
```json
{
  "filename": "example.txt",
  "content": "File contents here...",
  "size_bytes": 1024,
  "lines": 42,
  "success": true
}
```

---

### 6. **get_time**
Get current time in various formats.

**Parameters:**
- `format` (string, optional): Time format - `iso`, `human`, or `unix` (default: `iso`)

**Example:**
```json
{
  "format": "human"
}
```

**Response:**
```json
{
  "timestamp": "2025-01-01T12:00:00",
  "formatted": "January 01, 2025 at 12:00:00 PM",
  "format_type": "human",
  "timezone": "UTC"
}
```

---

## 📡 API Endpoints

Once deployed, your server provides these endpoints:

- **SSE Connection**: `https://your-app.onrender.com/sse`
- **Health Check**: `https://your-app.onrender.com/health`
- **List Tools**: `https://your-app.onrender.com/tools`

## 🛠️ Installation

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd pydantic-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

The server will start on `http://localhost:8080`

### Requirements

```txt
mcp>=1.0.0
pydantic>=2.0.0
starlette>=0.27.0
uvicorn[standard]>=0.23.0
python-dotenv>=1.0.0
```

## 🚢 Deployment to Render

### Prerequisites
- GitHub/GitLab account with your code
- Render account (free tier available)

### Deployment Steps

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - **Name**: `pydantic-mcp-server`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python run.py`
     - **Instance Type**: Free or paid tier

3. **Your server will be live at**: `https://your-app-name.onrender.com`

### Using render.yaml (Optional)

Create `render.yaml` in your repository root:

```yaml
services:
  - type: web
    name: pydantic-mcp-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python run.py
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
```

Then deploy via Blueprint in Render Dashboard.

## 🔌 Connecting to Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pydantic-server": {
      "transport": {
        "type": "sse",
        "url": "https://your-app-name.onrender.com/sse"
      }
    }
  }
}
```

Restart Claude Desktop to connect.

## 🧪 Testing

### Test Health Endpoint
```bash
curl https://your-app-name.onrender.com/health
```

### Test Tools List
```bash
curl https://your-app-name.onrender.com/tools
```

### Local Testing
```bash
# Start the server
python run.py

# In another terminal, test the health endpoint
curl http://localhost:8080/health
```

## 📁 Project Structure

```
pydantic-mcp-server/
├── requirements.txt          # Python dependencies
├── render.yaml              # Render deployment config (optional)
├── run.py                   # Entry point
└── src/
    └── servers/
        ├── models/
        │   └── local_models.py    # Pydantic models
        └── mcp_tools/
            └── local_tools.py     # Tool implementations
```

## 🔒 Security Features

- **Input Validation**: All inputs validated with Pydantic
- **Path Traversal Protection**: File operations restricted to safe paths
- **Sanitization**: Special characters removed from user inputs
- **Error Handling**: Structured error responses
- **Type Safety**: Strong typing prevents runtime errors

## 📝 Error Handling

All tools return structured error responses on failure:

```json
{
  "success": false,
  "error_type": "ValueError",
  "error_message": "Cannot divide by zero",
  "timestamp": "2025-01-01T12:00:00"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this project for your own purposes.

## 🆘 Support

For issues or questions:
- Check the [Render documentation](https://render.com/docs)
- Review the [MCP documentation](https://modelcontextprotocol.io)
- Open an issue in this repository

## 🔄 Updates

To update your deployment:
```bash
git add .
git commit -m "Your changes"
git push
```

Render will automatically redeploy your changes.
