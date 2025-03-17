import React, { useState, useEffect } from 'react';
import { Container, Paper, Typography, Grid, Alert } from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ROIData {
  period_id: number;
  period_savings: number;
  cumulative_savings: number;
  cc_to_ach_ratio: number;
}

interface Alert {
  type: 'success' | 'warning';
  message: string;
  timestamp: string;
}

function App() {
  const [roiData, setRoiData] = useState<ROIData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [forecast, setForecast] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/roi');
        setRoiData(response.data.roi_data);
        setAlerts(response.data.alerts);
        setForecast(response.data.forecast);
      } catch (error) {
        console.error('Error fetching ROI data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);

    return () => clearInterval(interval);
  }, []);

  const chartData = {
    labels: roiData.map(d => `Period ${d.period_id}`),
    datasets: [
      {
        label: 'Cumulative ROI',
        data: roiData.map(d => d.cumulative_savings),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
      {
        label: 'Period Savings',
        data: roiData.map(d => d.period_savings),
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
      },
      {
        label: 'ACH Adoption Rate',
        data: roiData.map(d => d.cc_to_ach_ratio * 100),
        borderColor: 'rgb(54, 162, 235)',
        tension: 0.1,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'ROI Tracking Dashboard',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography component="h1" variant="h4" color="primary" gutterBottom>
              ROI Tracking Dashboard
            </Typography>
            
            {/* Alerts Section */}
            {alerts.map((alert, index) => (
              <Alert key={index} severity={alert.type} sx={{ mb: 2 }}>
                {alert.message}
              </Alert>
            ))}

            {/* ROI Chart */}
            <Paper sx={{ p: 2, height: 400 }}>
              <Line options={chartOptions} data={chartData} />
            </Paper>

            {/* Forecast Information */}
            {forecast && (
              <Paper sx={{ p: 2, mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Forecast Details
                </Typography>
                <Typography>
                  Current ROI: ${forecast.current_roi?.toFixed(2)}
                </Typography>
                {forecast.periods_to_target && (
                  <Typography>
                    Estimated periods to positive ROI: {forecast.periods_to_target}
                  </Typography>
                )}
              </Paper>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App; 