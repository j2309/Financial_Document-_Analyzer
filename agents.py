import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, LLM
from tools import search_tool, read_data_tool

llm = LLM(
    model="groq/llama-3.3-70b-versatile",  # ✅ currently active model
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)
# ✅ Fixed Financial Analyst
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Analyze the financial document for query: {query} and provide accurate, evidence-based insights drawn from the document data.",
    verbose=True,
    memory=True,
    backstory=(
        "You have 20 years of experience in financial analysis. "
        "You rely strictly on verified data and do not speculate beyond what the documents support."
    ),
    tools=[read_data_tool, search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=1,
    allow_delegation=False
)

# ✅ Fixed Verifier
verifier = Agent(
    role="Financial Document Verifier",
    goal="Carefully verify that uploaded documents are genuine financial reports and flag anything suspicious or non-financial.",
    verbose=True,
    memory=True,
    backstory=(
        "You have a background in financial compliance and audit. "
        "You read every document thoroughly and only approve documents that meet financial reporting standards."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=1,
    allow_delegation=False
)

# ✅ Fixed Investment Advisor
investment_advisor = Agent(
    role="Certified Investment Advisor",
    goal="Provide transparent, client-focused investment recommendations grounded in the analyzed financial document. Always disclose risks.",
    verbose=True,
    backstory=(
        "You are a licensed financial planner with 15+ years of experience at reputable institutions. "
        "You prioritize client goals, risk tolerance, and regulatory compliance in every recommendation."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=1,
    allow_delegation=False
)

# ✅ Fixed Risk Assessor
risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal="Conduct a thorough, balanced risk assessment using established frameworks like VaR, Sharpe Ratio, and diversification principles.",
    verbose=True,
    backstory=(
        "You hold certifications in risk management (FRM/CFA) and have worked with institutional investors. "
        "You provide nuanced risk profiles — neither dismissing risk nor exaggerating it."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=1,
    allow_delegation=False
)