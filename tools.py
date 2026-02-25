from crewai.tools import BaseTool
from langchain_community.document_loaders import PyPDFLoader
from crewai_tools import SerperDevTool
import re

search_tool = SerperDevTool()

class ReadDataTool(BaseTool):
    name: str = "read_data_tool"
    description: str = "Read financial data from a PDF file. Input should be the file path."

    def _run(self, path: str = "data/sample.pdf") -> str:
        loader = PyPDFLoader(path)
        docs = loader.load()
        full_report = ""

        for data in docs:
            content = data.page_content
            content = re.sub(r'\n+', '\n', content)
            full_report += content + "\n"

        # ✅ Increased to 5000 for better document coverage
        if len(full_report) > 5000:
            full_report = full_report[:5000] + "\n\n[Document truncated due to length...]"

        return full_report


class AnalyzeInvestmentTool(BaseTool):
    name: str = "analyze_investment_tool"
    description: str = "Analyze financial document data. Input should be the document text."

    def _run(self, financial_document_data: str) -> str:
        # ✅ Clean extra spaces efficiently
        processed_data = re.sub(r' +', ' ', financial_document_data)
        return processed_data


class CreateRiskAssessmentTool(BaseTool):
    name: str = "create_risk_assessment_tool"
    description: str = "Create a risk assessment from financial document data."

    def _run(self, financial_document_data: str) -> str:
        # ✅ Basic risk keywords scanner
        risk_keywords = ["debt", "loss", "liability", "risk", "decline", "deficit", "negative"]
        found_risks = [kw for kw in risk_keywords if kw.lower() in financial_document_data.lower()]

        if found_risks:
            return f"Potential risk indicators found in document: {', '.join(found_risks)}"
        return "No major risk indicators found in the document."


# ✅ Instantiate tools
read_data_tool = ReadDataTool()
analyze_investment_tool = AnalyzeInvestmentTool()
create_risk_assessment_tool = CreateRiskAssessmentTool()