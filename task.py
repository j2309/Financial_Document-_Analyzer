## Importing libraries and files
from crewai import Task
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, read_data_tool

## Task 1 — Analyze the financial document
analyze_financial_document = Task(
    description="""
Analyze the financial document and answer the user's query: {query}.
Read the PDF file located at: {file_path}
Use the financial data from the PDF and external market information if needed.
Base your analysis ONLY on actual data from the document.
Do not invent sources, URLs, or statistics.
Provide accurate financial insights and recommendations.
""",
    expected_output="""A professional financial analysis including:
- Summary of the financial document contents
- Key financial metrics and ratios found in the document
- Data-backed investment insights
- Clear and honest recommendations based strictly on document data
- Any limitations or caveats in the analysis""",
    agent=financial_analyst,
    tools=[read_data_tool, search_tool],
    async_execution=False,
)

## Task 2 — Investment analysis
investment_analysis = Task(
    description="""
Review the financial data from the document at {file_path} and answer: {query}
Provide grounded investment analysis based strictly on the financial report.
Identify real investment opportunities and risks supported by the document data.
Do not recommend products unrelated to the document findings.
Always disclose risks associated with any recommendation.
""",
    expected_output="""A clear investment analysis including:
- Data-driven investment opportunities identified from the document
- Specific financial ratios and metrics supporting each recommendation
- Risk disclosure for every recommendation
- Conservative, moderate, and aggressive investment options if applicable
- Sources and reasoning behind each suggestion""",
    agent=investment_advisor,
    tools=[read_data_tool],
    async_execution=False,
)

## Task 3 — Risk assessment
risk_assessment = Task(
    description="""
Conduct a thorough risk assessment based on the financial document at {file_path}.
User query: {query}
Use established risk frameworks such as VaR, Sharpe Ratio, and diversification analysis.
Only reference real, verifiable risk models and financial institutions.
Be balanced — do not exaggerate or downplay risks.
""",
    expected_output="""A balanced risk assessment including:
- Overall risk profile of the entity in the document (low/medium/high)
- Specific risk factors identified from the document data
- Recommended risk mitigation strategies with clear reasoning
- Realistic timelines and targets based on document findings
- References to established risk frameworks used in the analysis""",
    agent=risk_assessor,
    tools=[read_data_tool],
    async_execution=False,
)

## Task 4 — Document verification
verification = Task(
    description="""
Carefully verify whether the uploaded document at {file_path} is a genuine financial report.
Read the document thoroughly using the read_data_tool.
Check for standard financial report elements such as:
- Balance sheets, income statements, cash flow statements
- Financial ratios and metrics
- Audit signatures or certifications
- Reporting period and entity information
Flag clearly if the document does NOT appear to be a financial report.
""",
    expected_output="""A verification report including:
- Confirmation of whether this is a valid financial document (Yes/No)
- List of financial elements found in the document
- Any suspicious, missing, or non-standard elements flagged
- Confidence level in the verification (High/Medium/Low)
- Recommendation on whether to proceed with financial analysis""",
    agent=verifier,
    tools=[read_data_tool],
    async_execution=False
)