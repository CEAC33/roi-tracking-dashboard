# ROI Tracking System - Architecture & Approach

## System Overview

```mermaid
graph TB
    subgraph Frontend
        UI[React Dashboard]
        Chart[Chart.js Visualization]
        Metrics[Detailed Metrics]
        Alerts[Alert System]
    end

    subgraph Backend
        API[FastAPI Server]
        Engine[ROI Engine]
        Calculator[ROI Calculator]
        Forecaster[Linear Regression Forecaster]
    end

    subgraph Data Model
        TP[Transaction Period]
        ROI[ROI Results]
        Alert[Alert Data]
    end

    UI --> API
    API --> Engine
    Engine --> Calculator
    Engine --> Forecaster
    TP --> Engine
    Engine --> ROI
    Engine --> Alert
    ROI --> Chart
    ROI --> Metrics
    Alert --> Alerts
```

## Data Model

```mermaid
classDiagram
    class TransactionPeriod {
        +str period
        +float cc_volume
        +int cc_count
        +float ach_volume
        +int ach_count
        +float cc_rate
        +float conv_fee
    }

    class ROIResult {
        +str period
        +float roi
        +float forecast
        +RawNumbers raw_numbers
    }

    class RawNumbers {
        +float subscription_cost
        +float cumulative_savings
        +float period_savings
        +float cc_fee_savings
        +float conv_fee_revenue
    }

    class Alert {
        +str type
        +str message
        +datetime timestamp
    }

    TransactionPeriod --> ROIResult
    ROIResult --> RawNumbers
```

## Calculation Flow

```mermaid
flowchart TD
    A[Input Transaction Data] --> B[Calculate Potential CC Cost]
    B --> C[Calculate Actual CC Cost]
    C --> D[Calculate CC Fee Savings]
    A --> E[Calculate Conversion Fee Revenue]
    D --> F[Calculate Total Period Savings]
    E --> F
    F --> G[Update Cumulative Savings]
    G --> H[Calculate ROI Amount]
    H --> I[Generate Forecasts]
    I --> J[Linear Regression Model]
    J --> K[Update Forecasts]
    H --> L[Generate Alerts]
    K --> L
```

## System Approach

1. **Data Collection**
   - Collect transaction data per period
   - Track credit card and ACH volumes
   - Monitor processing fees and rates

2. **ROI Calculation**
   - Calculate potential costs (if all transactions were CC)
   - Calculate actual costs (with ACH adoption)
   - Compute savings from fee differentials
   - Track cumulative savings against subscription cost

3. **Forecasting**
   - Use linear regression for trend analysis
   - Project future ROI based on historical data
   - Update forecasts as new data arrives

4. **Alert System**
   - Monitor ROI trajectory
   - Track progress towards break-even
   - Provide real-time status updates
   - Alert on concerning trends

5. **Visualization**
   - Real-time dashboard updates
   - Interactive data exploration
   - Detailed period metrics
   - Clear status indicators

## Key Components

### ROI Engine
- Core calculation engine
- Manages transaction periods
- Calculates ROI metrics
- Generates forecasts
- Produces alerts

### API Layer
- RESTful endpoints
- Real-time data access
- Period management
- Status reporting

### Frontend Dashboard
- Interactive visualization
- Real-time updates
- Detailed metrics display
- Alert management

## Data Flow

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as API Layer
    participant Engine as ROI Engine
    participant Calc as Calculator
    participant Forecast as Forecaster

    FE->>API: Request ROI Data
    API->>Engine: Get Current Status
    Engine->>Calc: Calculate ROI
    Calc-->>Engine: Return Results
    Engine->>Forecast: Generate Predictions
    Forecast-->>Engine: Return Forecasts
    Engine-->>API: Complete Results
    API-->>FE: Return Data
    FE->>FE: Update Dashboard
``` 