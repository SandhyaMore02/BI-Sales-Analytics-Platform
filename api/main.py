import os
import shutil
import tempfile
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

from src.ingestion.ingest import DataIngestionEngine
from src.cleaning.clean import DataCleaningPipeline
from src.features.engineer import FeatureEngineeringPipeline
from src.database.connection import create_db_engine
from src.database.loader import StarSchemaETLLoader
from src.analytics.query_engine import SQLAnalyticsEngine
from src.analytics.alert_engine import BusinessAlertEngine
from src.analytics.forecast import SalesForecastingEngine
from src.analytics.rfm import RFMSegmentationEngine
from src.ai.insight_engine import GeminiAIInsightEngine

app = FastAPI(
    title="AI-Powered BI & Sales Analytics API",
    description="REST API for Data Ingestion, Star Schema Analytics, Business Alerts, Forecasting, RFM, and Gemini AI Insights",
    version="1.0.0"
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_db_engine()
sql_analytics = SQLAnalyticsEngine(engine=engine)
alert_engine = BusinessAlertEngine()
forecast_engine = SalesForecastingEngine(engine=engine)
rfm_engine = RFMSegmentationEngine(engine=engine)
ai_engine = GeminiAIInsightEngine()

class InsightRequest(BaseModel):
    custom_prompt: str = ""

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint returning system & database status."""
    return {
        "status": "healthy",
        "database": str(engine.url).split("@")[-1],
        "ai_provider": ai_engine.provider
    }

@app.get("/api/kpi", tags=["Analytics"])
def get_kpi_summary():
    """Returns top-level executive KPI metrics."""
    try:
        kpis = sql_analytics.get_kpi_summary()
        return {"status": "success", "kpis": kpis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

@app.get("/api/analytics/regional", tags=["Analytics"])
def get_regional_analytics():
    """Returns sales breakdown by region and state."""
    try:
        df = sql_analytics.get_regional_analytics()
        return {"status": "success", "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

@app.get("/api/analytics/products", tags=["Analytics"])
def get_product_analytics():
    """Returns product performance, ranking, and profit margins."""
    try:
        df = sql_analytics.get_product_performance()
        return {"status": "success", "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

@app.get("/api/analytics/mom", tags=["Analytics"])
def get_mom_growth():
    """Returns Month-over-Month revenue & profit growth trends."""
    try:
        df = sql_analytics.get_mom_growth()
        return {"status": "success", "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

@app.get("/api/forecast", tags=["Predictive Analytics"])
def get_sales_forecast(months: int = 3):
    """Returns 3-month forward sales revenue projections."""
    try:
        res = forecast_engine.generate_monthly_forecast(forecast_months=months)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting error: {str(e)}")

@app.get("/api/rfm", tags=["Predictive Analytics"])
def get_rfm_segmentation():
    """Returns Customer RFM (Recency, Frequency, Monetary) segmentation breakdown."""
    try:
        res = rfm_engine.compute_rfm_segmentation()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RFM Segmentation error: {str(e)}")

@app.get("/api/alerts", tags=["Business Alerts"])
def get_business_alerts():
    """Evaluates metrics and returns active business alerts."""
    try:
        kpis = sql_analytics.get_kpi_summary()
        reg_df = sql_analytics.get_regional_analytics()
        prod_df = sql_analytics.get_product_performance()
        mom_df = sql_analytics.get_mom_growth()

        alerts = alert_engine.evaluate_alerts(kpis, reg_df, prod_df, mom_df)
        return {"status": "success", "alert_count": len(alerts), "alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating alerts: {str(e)}")

@app.post("/api/insights", tags=["AI Engine"])
def generate_ai_insights(req: InsightRequest = None):
    """Triggers Google Gemini API to analyze database metrics and return executive insights."""
    try:
        kpis = sql_analytics.get_kpi_summary()
        reg_df = sql_analytics.get_regional_analytics()
        prod_df = sql_analytics.get_product_performance()
        mom_df = sql_analytics.get_mom_growth()
        alerts = alert_engine.evaluate_alerts(kpis, reg_df, prod_df, mom_df)

        insights_text = ai_engine.generate_insights(kpis, reg_df, prod_df, mom_df, alerts)
        return {"status": "success", "ai_insights": insights_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI insight generation error: {str(e)}")

@app.post("/upload", tags=["Data Pipeline"])
async def upload_sales_file(file: UploadFile = File(...)):
    """Uploads CSV/Excel file, executes ingestion, cleaning, feature engineering, and loads Star Schema DB."""
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV or Excel files allowed.")

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ingestor = DataIngestionEngine()
        df_raw, ing_report = ingestor.ingest(temp_path)

        cleaner = DataCleaningPipeline()
        df_clean, clean_report = cleaner.clean(df_raw)

        fe = FeatureEngineeringPipeline()
        df_featured = fe.add_features(df_clean)

        loader = StarSchemaETLLoader(engine=engine)
        loader.load_star_schema(df_featured)

        return {
            "status": "success",
            "message": f"Successfully processed '{file.filename}'",
            "ingestion_report": ing_report,
            "cleaning_report": clean_report,
            "processed_rows": len(df_featured)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline processing error: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
