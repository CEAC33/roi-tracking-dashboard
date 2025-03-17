from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from roi_engine import ROIEngine, TransactionPeriod

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ROI Engine
roi_engine = ROIEngine()
current_period = 0  # Track the current period

class PeriodData(BaseModel):
    period: str
    cc_volume: float
    cc_count: int
    ach_volume: float
    ach_count: int
    cc_rate: float
    conv_fee: float

@app.post("/period")
async def add_period(period_data: PeriodData):
    try:
        transaction_period = TransactionPeriod(
            period=period_data.period,
            cc_volume=period_data.cc_volume,
            cc_count=period_data.cc_count,
            ach_volume=period_data.ach_volume,
            ach_count=period_data.ach_count,
            cc_rate=period_data.cc_rate,
            conv_fee=period_data.conv_fee
        )
        roi_engine.add_period(transaction_period)
        return {"message": "Period data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/periods")
async def delete_all_periods():
    """Delete all periods from the ROI engine"""
    try:
        roi_engine.periods.clear()
        return {"message": "All periods deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/roi")
async def get_roi():
    try:
        roi_data = roi_engine.calculate_roi(current_period)
        alerts = roi_engine.get_alerts(current_period)
        return {
            "results": roi_data,
            "alerts": alerts,
            "current_period": current_period
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/next-period")
async def load_next_period():
    """Load the next period of data"""
    global current_period
    try:
        if current_period < len(roi_engine.periods):
            current_period += 1
            return {"message": f"Advanced to period {current_period}", "current_period": current_period}
        else:
            return {"message": "All periods loaded", "current_period": current_period}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset-periods")
async def reset_periods():
    """Reset the current period counter"""
    global current_period
    try:
        current_period = 0
        return {"message": "Period counter reset", "current_period": current_period}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 