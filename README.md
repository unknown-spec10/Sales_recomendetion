# Sales Recommendation API 🚀

An AI-powered FastAPI application that provides intelligent product recommendations based on company names and product requirements using Groq AI.

## 🌟 Features

- **AI-Powered Recommendations**: Uses Groq's `llama-3.1-8b-instant` model for intelligent product matching
- **Dual Endpoint Support**: 
  - Simplified endpoint (`/recommend`) - takes company name and product name
  - Advanced endpoint (`/recommend-ai`) - takes company name and business lines
- **Company Prioritization**: Prioritizes products from the same company when available
- **Cross-Company Intelligence**: Finds relevant products across all companies when needed
- **Fallback Logic**: Graceful handling when AI is unavailable
- **Real-time Processing**: Fast recommendations with comprehensive product database

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Groq AI**: Advanced language model for intelligent recommendations
- **Python 3.12+**: Core programming language
- **JSON Data Storage**: Efficient product and business line data management

## 📊 Data Overview

- **44 Products** across 4 companies
- **Companies**: Danfoss, Fowler, Grundfos, Thermax
- **Product Categories**: VFD, Pumps, Cleaners, Heaters, Boilers, and more

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.12+
# pip package manager
```

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd sales_recomendetion_API
```

2. **Create virtual environment**
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Groq API Key**
   - Get your free API key from [Groq Console](https://console.groq.com/keys)
   - Update the `GROQ_API_KEY` in `main.py` (line 11)

5. **Run the server**
```bash
python -m uvicorn main:app --reload --port 8001
```

6. **Access the API**
   - API Server: http://127.0.0.1:8001
   - Interactive Docs: http://127.0.0.1:8001/docs
   - Alternative Docs: http://127.0.0.1:8001/redoc

## 📡 API Endpoints

### 1. API Status
```http
GET http://127.0.0.1:8001/
```

### 2. Get Companies
```http
GET http://127.0.0.1:8001/companies
```

### 3. Simplified Recommendations
```http
GET http://127.0.0.1:8001/recommend?company_name=Fowler&product_name=Cleaner
```

### 4. Advanced Recommendations
```http
GET http://127.0.0.1:8001/recommend-ai?company_name=TechCorp&business_lines=VFD&business_lines=Pump
```

## 🧪 Testing

### Run Test Suite
```bash
python test_postman.py
```

### Example API Calls

**Simplified Endpoint:**
```bash
curl "http://127.0.0.1:8001/recommend?company_name=Fowler&product_name=Cleaner"
```

**Advanced Endpoint:**
```bash
curl "http://127.0.0.1:8001/recommend-ai?company_name=TechCorp&business_lines=VFD&business_lines=Pump"
```

## 📝 Example Responses

### Successful AI Recommendation
```json
{
  "request": {
    "company_name": "Fowler",
    "product_name": "Cleaner"
  },
  "recommendations": [
    {
      "id": "6891a4b69b788ad40d4980ea",
      "company_name": "Fowler",
      "product_line": "Modular Cleaner"
    }
  ],
  "total_recommendations": 5,
  "ai_used": true,
  "method": "🤖 Groq AI"
}
```

## 🏗️ Project Structure

```
sales_recomendetion_API/
├── main.py                     # Main FastAPI application
├── requirements.txt            # Python dependencies
├── data.json                   # Source product data
├── products_with_tuples.json   # Processed product data
├── business_line_tuples.json   # Business line mappings
├── test_postman.py            # API test suite
├── test.py                    # Legacy test file
├── final_extraction.py        # Data processing script
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for sensitive configurations:
```env
GROQ_API_KEY=your_groq_api_key_here
PORT=8001
```

### API Key Security
- Never commit API keys to version control
- Use environment variables for production deployments
- Rotate API keys regularly

## 🚦 API Response Codes

- `200 OK`: Successful request
- `422 Unprocessable Entity`: Invalid request parameters
- `500 Internal Server Error`: Server-side error

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Performance

- **Response Time**: < 3 seconds with AI
- **Throughput**: Handles concurrent requests
- **Accuracy**: High relevance matching with Groq AI
- **Fallback**: Graceful degradation when AI unavailable

## 🛡️ Security

- API key protection
- Input validation
- Error handling
- Rate limiting (can be added)

## 📈 Future Enhancements

- [ ] User authentication
- [ ] Request rate limiting
- [ ] Database integration
- [ ] Caching layer
- [ ] Analytics dashboard
- [ ] A/B testing for recommendation algorithms

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions and support:
- Create an issue in the repository
- Contact the development team

---

**Made with ❤️ using FastAPI and Groq AI**
