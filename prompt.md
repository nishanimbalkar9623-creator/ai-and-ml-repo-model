# AI Invoice & Business Analytics System — OpenCode Development Prompt

You are an experienced Python backend engineer and AI/ML engineer.

I want you to build an **AI-powered Invoice, Business Analytics, and Sales Forecasting backend**.

## 1. Project Goal

Build a backend where a business user can enter invoice/sales information such as:

* Customer name
* Product/service name
* Quantity/units
* Purchase price
* Selling price
* GST percentage
* Date

The system must store the information and automatically calculate:

* Subtotal
* GST amount
* Final invoice amount
* Cost
* Revenue
* Profit/loss
* Profit margin

The system should also analyze historical business data and provide:

* Sales analytics
* Product performance
* Revenue trends
* Profit/loss trends
* GST summaries
* Monthly/yearly summaries
* Sales forecasting
* AI-generated business insights

## 2. Technology Stack

Use:

* Python
* Flask
* SQLite initially
* SQLAlchemy
* Pandas
* NumPy
* Scikit-learn where appropriate
* Matplotlib/other Python libraries only if required for backend analytics
* Gemini API for natural-language business insights
* python-dotenv for environment variables

Do NOT build a frontend yet.

The current goal is a clean, modular backend/API.

## 3. Important Architecture Rule

Separate the system into clear modules.

Suggested structure:

```text
project/
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── invoice_routes.py
│   │   ├── analytics_routes.py
│   │   ├── forecast_routes.py
│   │   └── ai_routes.py
│   │
│   ├── models/
│   │   ├── invoice.py
│   │   └── product.py
│   │
│   ├── services/
│   │   ├── invoice_service.py
│   │   ├── calculation_service.py
│   │   ├── analytics_service.py
│   │   ├── forecast_service.py
│   │   └── ai_service.py
│   │
│   └── utils/
│
├── data/
├── tests/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

You may modify the structure if you have a better architecture, but explain why.

## 4. Development Method

IMPORTANT:

Do NOT generate the entire project blindly in one step.

Follow this workflow:

```text
Requirements
↓
Architecture
↓
Database
↓
Invoice API
↓
Calculations
↓
Analytics
↓
Forecasting
↓
Gemini AI
↓
Testing
↓
Final integration
```

Before implementing each major module:

1. Explain what you are going to build.
2. Explain which files will be changed.
3. Implement it.
4. Run/test it.
5. Fix errors.
6. Only then move to the next module.

Do not move to the next major module if the current module is broken.

## 5. Database

Create a proper relational database structure.

At minimum, support:

### Invoice

* id
* customer_name
* invoice_date
* subtotal
* gst_percentage
* gst_amount
* total_amount
* total_cost
* profit
* created_at

### Invoice Item

* id
* invoice_id
* product_name
* quantity
* purchase_price
* selling_price
* item_subtotal
* item_cost
* item_profit

Use SQLAlchemy models and relationships.

Make sure calculations are performed by backend code rather than by the LLM.

## 6. Invoice API

Create REST APIs for:

* Creating an invoice
* Getting an invoice
* Getting all invoices
* Updating an invoice
* Deleting an invoice

Validate all user input.

Reject invalid values such as:

* Negative quantity
* Negative prices
* Invalid GST percentage
* Missing required fields

Return clean JSON responses.

## 7. Financial Calculations

Implement reliable backend calculations.

For each invoice calculate:

```text
Subtotal = quantity × selling_price

GST = subtotal × GST_percentage / 100

Total = subtotal + GST

Cost = quantity × purchase_price

Profit = subtotal - Cost

Profit Margin = Profit / Subtotal × 100
```

Handle division-by-zero and invalid values safely.

IMPORTANT:

Financial calculations must NOT be delegated to Gemini.

The Python backend must calculate the actual numbers.

## 8. Analytics

Create analytics APIs for:

* Total revenue
* Total cost
* Total profit
* Total GST
* Number of invoices
* Average invoice value
* Best-selling products
* Most profitable products
* Monthly sales
* Monthly profit
* Sales growth
* Profit growth

Return structured JSON that a future frontend can easily convert into:

* Bar charts
* Line charts
* Pie charts
* KPI cards

Do not build the frontend now.

## 9. Sales Forecasting

Create a forecasting module using historical sales data.

The system should:

1. Retrieve historical sales.
2. Aggregate sales by date/month.
3. Prepare the dataset.
4. Train an appropriate forecasting model.
5. Generate future sales predictions.
6. Return predictions through an API.

Do NOT claim that predictions are guaranteed.

If the dataset is too small, return a meaningful response explaining that more historical data is required.

Choose the forecasting approach based on the available data instead of unnecessarily using a complicated model.

## 10. Gemini AI Integration

Integrate Gemini through an environment variable.

Use:

```env
GEMINI_API_KEY=your_api_key_here
```

NEVER hard-code the API key.

NEVER commit `.env` to GitHub.

Create:

```text
.env.example
```

containing:

```env
GEMINI_API_KEY=
```

The Gemini service should receive structured business information from the backend, such as:

* Revenue
* Profit
* GST
* Sales trends
* Top products
* Forecast results
* Growth rates

Then ask Gemini to convert these numbers into understandable business insights.

For example:

```text
Business data:
Revenue: ...
Profit: ...
Growth: ...
Top product: ...
Forecast: ...

Generate:
1. Key observations
2. Possible business risks
3. Possible opportunities
4. Simple actionable suggestions
```

Gemini should explain the data, not invent financial numbers.

## 11. AI Insight API

Create an endpoint such as:

```text
POST /api/ai/insights
```

It should:

1. Retrieve the relevant analytics.
2. Retrieve forecasting results if available.
3. Build a structured prompt.
4. Send the information to Gemini.
5. Return the AI-generated insights as JSON.

If Gemini is unavailable, the backend should return a clear error instead of crashing the application.

## 12. Security

Follow these rules:

* Never hard-code API keys.
* Use `.env`.
* Add `.env` to `.gitignore`.
* Validate all API input.
* Do not expose secrets in API responses.
* Handle API failures safely.
* Do not trust user-provided financial calculations; calculate them on the server.

## 13. Testing

Create tests for:

* Invoice creation
* Input validation
* GST calculation
* Profit calculation
* Invoice retrieval
* Analytics
* Forecasting
* Gemini integration

Use realistic sample data.

Also test edge cases such as:

* Zero quantity
* Zero cost
* Zero selling price
* Empty invoice
* Invalid GST
* Very large values
* Insufficient historical data

## 14. API Documentation

Document every API endpoint with:

* HTTP method
* URL
* Request JSON
* Response JSON
* Possible errors

Create a simple API documentation file such as:

```text
API_DOCUMENTATION.md
```

## 15. OpenCode Behavior

Act as my coding agent.

When I ask you to implement something:

* Inspect the existing project before changing files.
* Do not unnecessarily rewrite working code.
* Reuse existing modules.
* Keep the architecture modular.
* Explain important decisions briefly.
* Write clean, beginner-readable Python.
* Avoid unnecessary complexity.
* Test your changes.
* If an error occurs, diagnose the actual cause before changing code.
* Do not hide errors with random workarounds.
* Never expose API keys or secrets.
* Ask for clarification only when a requirement genuinely cannot be inferred.

## 16. Start Now

Do NOT start by writing the complete application.

First:

1. Analyze these requirements.
2. Propose the final architecture.
3. Show the folder structure.
4. Explain the database design.
5. Explain the API design.
6. Explain how Gemini will connect.
7. Explain how forecasting will work.
8. Identify potential problems or missing requirements.

Then wait for approval before implementing the first module.


do , both model diff in folder 
used postsql for data base 

