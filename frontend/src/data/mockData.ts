export const portfolioSummary = {
  totalValue: 100000.0,
  cash: 47200.53,
  investedPercent: 52.8,
}

export const portfolioHistory = [
  { day: "Mon", value: 98200 },
  { day: "Tue", value: 98950 },
  { day: "Wed", value: 99520 },
  { day: "Thu", value: 100430 },
  { day: "Fri", value: 100000 },
]

export const allocationData = [
  { name: "Cash", value: 47.2 },
  { name: "AAPL", value: 2.45 },
  { name: "MSFT", value: 21.16 },
  { name: "ETH-USD", value: 24.13 },
  { name: "GLD", value: 5.06 },
]

export const positions = [
  {
    symbol: "AAPL",
    quantity: 9.79,
    avgCost: 249.94,
    currentWeight: 2.45,
    status: "Active",
  },
  {
    symbol: "MSFT",
    quantity: 52.12,
    avgCost: 398.21,
    currentWeight: 21.16,
    status: "Active",
  },
  {
    symbol: "ETH-USD",
    quantity: 12.84,
    avgCost: 1879.44,
    currentWeight: 24.13,
    status: "Active",
  },
  {
    symbol: "GLD",
    quantity: 10.42,
    avgCost: 485.31,
    currentWeight: 5.06,
    status: "Active",
  },
]

export const predictions = [
  {
    symbol: "AAPL",
    predictedReturn: 0.000719,
    sentiment: 0.1301,
    finalScore: 0.000979,
    action: "HOLD",
  },
  {
    symbol: "MSFT",
    predictedReturn: 0.008231,
    sentiment: 0.1167,
    finalScore: 0.008465,
    action: "HOLD",
  },
  {
    symbol: "NVDA",
    predictedReturn: -0.014822,
    sentiment: 0.3541,
    finalScore: -0.014114,
    action: "HOLD",
  },
  {
    symbol: "BTC-USD",
    predictedReturn: -0.01454,
    sentiment: 0.0124,
    finalScore: -0.014515,
    action: "HOLD",
  },
  {
    symbol: "ETH-USD",
    predictedReturn: 0.010196,
    sentiment: -0.2713,
    finalScore: 0.009653,
    action: "HOLD",
  },
  {
    symbol: "GLD",
    predictedReturn: 0.001633,
    sentiment: 0.1949,
    finalScore: 0.002023,
    action: "HOLD",
  },
]

export const trades = [
  {
    asset: "AAPL",
    action: "BUY",
    amount: 2448.19,
    time: "2026-04-09 14:03",
    status: "Executed",
  },
  {
    asset: "MSFT",
    action: "BUY",
    amount: 1161.69,
    time: "2026-04-09 14:03",
    status: "Executed",
  },
  {
    asset: "ETH-USD",
    action: "BUY",
    amount: 24132.67,
    time: "2026-04-09 14:03",
    status: "Executed",
  },
  {
    asset: "GLD",
    action: "BUY",
    amount: 5056.91,
    time: "2026-04-09 14:03",
    status: "Executed",
  },
]

export const explanations = [
  {
    symbol: "AAPL",
    predictedReturn: 0.000719,
    reasons: [
      {
        feature: "return_1d",
        value: -0.016874,
        shap: -0.002651,
        direction: "DOWN",
      },
      {
        feature: "momentum_7d",
        value: -9.94,
        shap: 0.001773,
        direction: "UP",
      },
      {
        feature: "rsi_14",
        value: 20.53778,
        shap: 0.001546,
        direction: "UP",
      },
    ],
    summary:
      "AAPL shows a slightly positive prediction. Recent daily weakness pushed the forecast down, while oversold and rebound-related signals pushed it back up.",
  },
  {
    symbol: "MSFT",
    predictedReturn: 0.008231,
    reasons: [
      {
        feature: "return_1d",
        value: -0.019078,
        shap: 0.003065,
        direction: "UP",
      },
      {
        feature: "rsi_14",
        value: 41.05568,
        shap: 0.001191,
        direction: "UP",
      },
      {
        feature: "ma_7",
        value: 399.88572,
        shap: 0.000847,
        direction: "UP",
      },
    ],
    summary:
      "MSFT is one of the strongest positive assets. Short-term return behavior, RSI, and moving-average structure all support a bullish forecast.",
  },
  {
    symbol: "ETH-USD",
    predictedReturn: 0.010196,
    reasons: [
      {
        feature: "return_1d",
        value: -0.051598,
        shap: 0.009799,
        direction: "UP",
      },
      {
        feature: "volatility_7d",
        value: 0.041038,
        shap: -0.005238,
        direction: "DOWN",
      },
      {
        feature: "ma_30",
        value: 2030.07459,
        shap: 0.00143,
        direction: "UP",
      },
    ],
    summary:
      "ETH-USD remains attractive mainly due to rebound and trend-related signals, although elevated volatility reduces confidence.",
  },
]