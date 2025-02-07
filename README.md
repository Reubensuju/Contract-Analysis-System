# Enterprise Contract Analysis System

#### Contract Analyzer is an AI-powered contract analysis system that processes PDF contracts to extract key information, identify risks, and assess compliance.

### Business Context

Enterprise businesses manage thousands of vendor contracts, each with specific compliance requirements, renewal dates, and business obligations. Reviewing those documents manually, is time-consuming and error-prone, leading to missed renewals and compliance risks.

### Features
- PDF contract upload and processing

- AI-powered contract analysis using Google Vertex AI

- Risk assessment and compliance checking

- Interactive timeline visualization

- Real-time processing status updates

### Requirements
1. **Document Processing Pipeline**
   - Implement a system to process PDF contracts.
   - Extract key contract metadata: parties involved, effective dates, renewal terms, compliance requirements.
   - Store processed information in a structured format.

2. **Intelligent Analysis Engine**
   - Design an agent-based system using LangGraph for orchestrating multiple specialized agents.
   - Implement agents for different aspects: compliance checking, risk assessment, renewal tracking.
   - Use function calling to integrate with external tools/APIs (functions may return mock data; don't use real external APIs).

3. **Business Intelligence Layer**
   - Generate automated contract summaries.
   - Identify potential risks and compliance issues.
   - Create renewal timeline visualizations.

### Core Technology Stack
   - Python 3.12
   - LangGraph for agent orchestration
   - OCI Free Tier (LLM inference) or Gemini 1.5 Pro
   - FastAPI for REST API endpoints
   - SQLite for data persistence

### Setup Instructions
1. Clone the Repository
```
git clone https://github.com/your-username/contract-analyzer.git
cd contract-analyzer
```
2. Set Up a Virtual Environment
Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```
3. Install Dependencies
```
pip install -r requirements.txt
```
4. Build the Frontend
```
npm run build
```
5. Run the Backend Server
Go back to the project root and start the FastAPI backend:
```
python main.py
```
7. Open the Application
Open your browser and navigate to:

http://localhost:8000

### Running Tests
To run tests using pytest with coverage:
```
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
python -m pytest --cov=src ./tests
```

