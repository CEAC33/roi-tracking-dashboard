import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions,
  TooltipItem,
  ChartEvent,
  ActiveElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface Alert {
  type: 'success' | 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

interface RawNumbers {
  subscription_cost: number;
  cumulative_savings: number;
  period_savings: number;
  cc_fee_savings: number;
  ach_costs: number;
  ach_savings: number;
  potential_cc_cost: number;
  actual_cc_cost: number;
}

interface ROIData {
  period: string;
  roi: number;
  forecast: number;
  raw_numbers: RawNumbers;
}

declare global {
  interface Window {
    env: {
      REACT_APP_API_URL?: string;
    };
  }
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const App: React.FC = () => {
  const [roiData, setRoiData] = useState<ROIData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<ROIData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPeriod, setCurrentPeriod] = useState(0);

  const loadNextPeriod = async () => {
    try {
      const apiUrl = window.env?.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/next-period`, {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.current_period;
    } catch (error) {
      console.error('Error advancing period:', error);
      return null;
    }
  };

  const resetPeriods = async () => {
    try {
      const apiUrl = window.env?.REACT_APP_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/reset-periods`, {
        method: 'POST'
      });
      setCurrentPeriod(0);
      setRoiData([]);
      setAlerts([]);
      setSelectedPeriod(null);
      startLoadingPeriods();
    } catch (error) {
      console.error('Error resetting periods:', error);
    }
  };

  const fetchData = async () => {
    try {
      const apiUrl = window.env?.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/roi`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRoiData(data.results);
      setAlerts(data.alerts);
      setCurrentPeriod(data.current_period);
      if (data.results.length > 0) {
        setSelectedPeriod(data.results[data.results.length - 1]);
      }
      setError(null);
      return data.current_period;
    } catch (error) {
      console.error('Error fetching ROI data:', error);
      setError('Failed to fetch ROI data. Please check the console for details.');
      return null;
    }
  };

  const startLoadingPeriods = async () => {
    setIsLoading(true);
    let keepLoading = true;
    let lastPeriod = 0;
    
    while (keepLoading) {
      const nextPeriod = await loadNextPeriod();
      if (nextPeriod === null || nextPeriod === lastPeriod) {
        keepLoading = false;
      } else {
        await fetchData();
        lastPeriod = nextPeriod;
        await new Promise(resolve => setTimeout(resolve, 10000)); // 10 second delay
      }
    }
    
    setIsLoading(false);
  };

  useEffect(() => {
    startLoadingPeriods();
    // No interval needed anymore since we're using manual progression
    return () => {};
  }, []);

  const chartData: ChartData<'line'> = {
    labels: roiData.map((d: ROIData) => d.period),
    datasets: [
      {
        label: 'Break-even Line',
        data: Array(roiData.length).fill(0),
        borderColor: 'rgba(0, 0, 0, 0.2)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        tension: 0,
        order: 3
      },
      {
        label: 'Actual ROI',
        data: roiData.map((d: ROIData) => d.roi),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        fill: true,
        tension: 0.1,
        order: 1
      },
      {
        label: 'Forecast',
        data: roiData.map((d: ROIData) => d.forecast),
        borderColor: 'rgb(255, 99, 132)',
        borderDash: [5, 5],
        tension: 0.1,
        order: 2
      }
    ]
  };

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1.5,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'ROI Tracking Dashboard'
      },
      tooltip: {
        callbacks: {
          label: (context: TooltipItem<'line'>) => {
            if (context.dataset.label === 'Break-even Line') return '';
            const value = context.raw as number;
            return `${context.dataset.label}: ${formatCurrency(value)}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'ROI ($)'
        },
        ticks: {
          callback: (value: number | string) => formatCurrency(Number(value))
        },
        grid: {
          color: (context) => {
            if (context.tick.value === 0) {
              return 'rgba(0, 0, 0, 0.2)';
            }
            return 'rgba(0, 0, 0, 0.1)';
          },
          lineWidth: (context) => {
            if (context.tick.value === 0) {
              return 2;
            }
            return 1;
          }
        }
      }
    },
    onClick: (_: ChartEvent, elements: ActiveElement[]) => {
      if (elements.length > 0) {
        const index = elements[0].index;
        setSelectedPeriod(roiData[index]);
      }
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>ROI Tracking Dashboard</h1>
        <button
          onClick={resetPeriods}
          style={{
            padding: '8px 16px',
            backgroundColor: '#4285f4',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Reset & Replay
        </button>
      </div>

      {isLoading && (
        <div style={{
          padding: '12px',
          backgroundColor: '#e8f0fe',
          borderRadius: '4px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <span>Loading periods... Currently at Period {currentPeriod}</span>
          <div style={{
            width: '20px',
            height: '20px',
            border: '2px solid #4285f4',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
        </div>
      )}
      
      {/* Alerts Section */}
      <div style={{ marginBottom: '20px' }}>
        {alerts.map((alert, index) => (
          <div
            key={index}
            style={{
              padding: '12px 16px',
              marginBottom: '8px',
              borderRadius: '4px',
              backgroundColor: alert.type === 'success' ? '#e6f4ea' :
                            alert.type === 'warning' ? '#fef7e6' :
                            alert.type === 'error' ? '#fde7e9' : '#e8f0fe',
              border: `1px solid ${
                alert.type === 'success' ? '#34a853' :
                alert.type === 'warning' ? '#fbbc04' :
                alert.type === 'error' ? '#ea4335' : '#4285f4'
              }`,
              color: alert.type === 'success' ? '#1e4620' :
                     alert.type === 'warning' ? '#8c4a03' :
                     alert.type === 'error' ? '#8c1d18' : '#1a3b82',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <strong style={{ marginRight: '8px' }}>
                {alert.type.charAt(0).toUpperCase() + alert.type.slice(1)}:
              </strong>
              {alert.message}
            </div>
            <div style={{ fontSize: '0.8em', color: '#666' }}>
              {new Date(alert.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>

      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          {error}
        </div>
      )}
      
      <div style={{ marginTop: '20px' }}>
        {roiData.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '20px' }}>
            <div>
              <Line data={chartData} options={options} />
            </div>
            
            {selectedPeriod && (
              <div style={{
                padding: '20px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                backgroundColor: '#f9f9f9',
                height: 'fit-content'
              }}>
                <h2 style={{ 
                  marginBottom: '15px',
                  fontSize: '1.2em',
                  borderBottom: '1px solid #ddd',
                  paddingBottom: '10px'
                }}>
                  Detailed Metrics for {selectedPeriod.period}
                </h2>
                <div style={{ 
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '15px'
                }}>
                  <div>
                    <h3 style={{ fontSize: '1em', color: '#666' }}>Investment</h3>
                    <p>Subscription Cost: {formatCurrency(selectedPeriod.raw_numbers.subscription_cost)}</p>
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1em', color: '#666' }}>Savings</h3>
                    <p>Period Savings: {formatCurrency(selectedPeriod.raw_numbers.period_savings)}</p>
                    <p>Cumulative Savings: {formatCurrency(selectedPeriod.raw_numbers.cumulative_savings)}</p>
                    <p style={{ 
                      fontWeight: 'bold',
                      color: selectedPeriod.roi >= 0 ? '#34a853' : '#ea4335'
                    }}>
                      Net ROI: {formatCurrency(selectedPeriod.roi)}
                    </p>
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1em', color: '#666' }}>Fee Analysis</h3>
                    <p>CC Fee Savings: {formatCurrency(selectedPeriod.raw_numbers.cc_fee_savings)}</p>
                    <p>ACH Costs: {formatCurrency(selectedPeriod.raw_numbers.ach_costs)}</p>
                    <p>ACH Savings: {formatCurrency(selectedPeriod.raw_numbers.ach_savings)}</p>
                    <p>Actual CC Cost: {formatCurrency(selectedPeriod.raw_numbers.actual_cc_cost)}</p>
                  </div>
                </div>
                <p style={{ 
                  marginTop: '15px',
                  fontSize: '0.9em',
                  color: '#666',
                  borderTop: '1px solid #ddd',
                  paddingTop: '10px'
                }}>
                  Click on any point in the chart to view its detailed metrics
                </p>
              </div>
            )}
          </div>
        ) : !error && (
          <div>Loading data...</div>
        )}
      </div>
    </div>
  );
};

export default App; 