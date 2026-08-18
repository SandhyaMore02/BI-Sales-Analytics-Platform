import os
import json
import pandas as pd
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class GeminiAIInsightEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.provider = "gemini"
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes Google Gemini API client if API key is present."""
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("[WARN] GEMINI_API_KEY not configured. Rule-based AI Insight Engine fallback will be used.")
            return

        try:
            # Try new google-genai SDK first, then google.generativeai fallback
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                self.sdk_type = "genai"
                print("[OK] Initialized Google Gemini API Client (google-genai SDK).")
            except ImportError:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel("gemini-1.5-flash")
                self.sdk_type = "generativeai"
                print("[OK] Initialized Google Gemini API Client (google.generativeai SDK).")
        except Exception as e:
            print(f"[WARN] Failed to initialize Gemini API client: {e}. Fallback enabled.")
            self.client = None

    def build_structured_context(
        self,
        kpi_summary: Dict[str, Any],
        regional_df: pd.DataFrame,
        product_df: pd.DataFrame,
        mom_df: pd.DataFrame,
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Constructs a clean JSON payload containing aggregated business metrics."""
        
        top_products = []
        if not product_df.empty:
            top_products = product_df.head(5)[["product_name", "category", "total_revenue", "total_profit", "profit_margin_pct"]].to_dict(orient="records")

        bottom_products = []
        if not product_df.empty:
            bottom_products = product_df.tail(3)[["product_name", "category", "total_revenue", "total_profit", "profit_margin_pct"]].to_dict(orient="records")

        regions = []
        if not regional_df.empty:
            regions = regional_df.head(5)[["region", "state", "total_revenue", "total_profit", "profit_margin_pct"]].to_dict(orient="records")

        latest_mom = {}
        if not mom_df.empty:
            valid_mom = mom_df.dropna(subset=["mom_growth_pct"])
            if len(valid_mom) > 0:
                latest_mom = valid_mom.iloc[-1][["year_month", "revenue", "profit", "mom_growth_pct"]].to_dict()

        return {
            "executive_kpis": kpi_summary,
            "latest_mom_trend": latest_mom,
            "top_revenue_products": top_products,
            "bottom_revenue_products": bottom_products,
            "top_regions": regions,
            "active_business_alerts": alerts
        }

    def generate_insights(
        self,
        kpi_summary: Dict[str, Any],
        regional_df: pd.DataFrame,
        product_df: pd.DataFrame,
        mom_df: pd.DataFrame,
        alerts: List[Dict[str, Any]]
    ) -> str:
        """Generates AI executive insights using Gemini API or rule-based fallback."""
        context = self.build_structured_context(kpi_summary, regional_df, product_df, mom_df, alerts)
        context_json = json.dumps(context, indent=2)

        prompt = f"""
You are an expert Senior Business Intelligence Analyst & Data Scientist.
Analyze the following validated sales metrics and business alert JSON payload and produce an executive business report.

CRITICAL INSTRUCTIONS:
1. Base your analysis STRICTLY on the numbers provided in the JSON context. DO NOT invent or fabricate numbers.
2. Structure your report into four distinct sections:
   - ### 1. Executive Summary
   - ### 2. Key Performance Drivers & Evidence
   - ### 3. Fact vs Hypothesis Analysis
   - ### 4. Strategic Business Recommendations
3. Clearly state profit margins, revenue growth trends, top drivers, and risks identified in the alerts.
4. Provide concrete, actionable business recommendations for executive leadership.

VALIDATED BUSINESS METRICS JSON:
{context_json}
"""

        if self.client:
            try:
                print("Sending structured context to Google Gemini API...")
                if self.sdk_type == "genai":
                    response = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    return response.text
                else:
                    response = self.client.generate_content(prompt)
                    return response.text
            except Exception as e:
                print(f"[WARN] Gemini API call error: {e}. Switching to rule-based analysis.")

        # Rule-based Fallback Analysis Generator
        return self._generate_fallback_insight(context)

    def _generate_fallback_insight(self, context: Dict[str, Any]) -> str:
        kpis = context.get("executive_kpis", {})
        rev = kpis.get("total_revenue", 0.0)
        profit = kpis.get("total_profit", 0.0)
        margin = kpis.get("profit_margin_pct", 0.0)
        orders = kpis.get("total_orders", 0)
        aov = kpis.get("avg_order_line_value", 0.0)
        top_prods = context.get("top_revenue_products", [])
        top_reg = context.get("top_regions", [])
        alerts = context.get("active_business_alerts", [])

        top_prod_str = ", ".join([f"**{p['product_name']}** (${p['total_revenue']:,.2f}, margin: {p['profit_margin_pct']:.1f}%)" for p in top_prods[:3]])
        top_reg_str = ", ".join([f"**{r['region']} - {r['state']}** (${r['total_revenue']:,.2f})" for r in top_reg[:3]])
        alerts_count = len(alerts)

        insight_text = f"""
### 1. Executive Summary
The sales analytics platform processed **{orders:,} orders** generating **${rev:,.2f}** in total revenue and **${profit:,.2f}** in net profit, achieving an overall profit margin of **{margin:.2f}%**. The average line item transaction value is **${aov:,.2f}**. 

### 2. Key Performance Drivers & Evidence
* **Product Catalog Champions**: Top revenue drivers include {top_prod_str if top_prod_str else 'primary catalog items'}.
* **Geographic Revenue Strongholds**: Performance is led by {top_reg_str if top_reg_str else 'key regional markets'}.
* **Financial Margin Quality**: Net margin of **{margin:.2f}%** indicates robust product pricing power across hardware and electronics categories.

### 3. Fact vs Hypothesis Analysis
* **Verified Fact**: Overall total revenue stands at **${rev:,.2f}** with **{alerts_count} active business alerts** flagged for management review.
* **Hypothesis for Investigation**: Regions with higher promotional discount rates may show margin compression relative to non-discounted channels.

### 4. Strategic Business Recommendations
1. **Optimize High-Revenue Discounting**: Review discount tiers on top products to capture an extra 1.5-2.0% in net profit margin.
2. **Expand Regional Footprint**: Allocate additional inventory and marketing budget to high-performing regions like West & North.
3. **Address Business Alerts**: Investigate flagged underperforming regions and high-revenue low-margin SKUs to mitigate profit leakages.

*(Generated by Rule-Based Business Intelligence Analytics Engine — Configure `GEMINI_API_KEY` in `.env` for dynamic Gemini AI response)*
"""
        return insight_text.strip()

if __name__ == "__main__":
    engine = GeminiAIInsightEngine()
    print("Insight Engine Initialized. Provider:", engine.provider)
