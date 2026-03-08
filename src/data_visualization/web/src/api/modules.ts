import apiClient from './index'

export const marketApi = {
  // 获取行情
  getTicker: (symbol: string, exchange?: string) =>
    apiClient.get(`/market/ticker/${symbol}`, { params: { exchange } }),

  // 获取多个行情
  getTickers: (params?: { exchange?: string; symbols?: string }) =>
    apiClient.get('/market/tickers', { params }),

  // 获取K线
  getKlines: (symbol: string, params: {
    interval?: string
    start_time?: string
    end_time?: string
    limit?: number
    exchange?: string
  }) => apiClient.get(`/market/klines/${symbol}`, { params }),

  // 获取深度
  getOrderBook: (symbol: string, limit?: number, exchange?: string) =>
    apiClient.get(`/market/depth/${symbol}`, { params: { limit, exchange } }),

  // 获取交易所列表
  getExchanges: () => apiClient.get('/market/exchanges'),

  // 获取链列表
  getChains: () => apiClient.get('/market/chains'),
}

export const tradesApi = {
  // 获取最近成交
  getRecentTrades: (params?: {
    symbol?: string
    source?: string
    limit?: number
  }) => apiClient.get('/trades/recent', { params }),

  // 获取交易统计
  getTradeStats: (symbol: string, params?: {
    start_time?: string
    end_time?: string
  }) => apiClient.get(`/trades/stats/${symbol}`, { params }),

  // 获取成交量分析
  getVolumeAnalysis: (symbol: string, params?: {
    interval?: string
    limit?: number
  }) => apiClient.get(`/trades/volume/${symbol}`, { params }),
}

export const alertsApi = {
  // 获取告警规则
  getRules: (params?: { is_active?: boolean; rule_type?: string }) =>
    apiClient.get('/alerts/rules', { params }),

  // 创建告警规则
  createRule: (data: any) => apiClient.post('/alerts/rules', data),

  // 获取告警历史
  getHistory: (params?: {
    status?: string
    severity?: string
    limit?: number
    offset?: number
  }) => apiClient.get('/alerts/history', { params }),

  // 确认告警
  acknowledgeAlert: (alertId: number) =>
    apiClient.post(`/alerts/history/${alertId}/acknowledge`),

  // 解决告警
  resolveAlert: (alertId: number) =>
    apiClient.post(`/alerts/history/${alertId}/resolve`),
}

export const analyticsApi = {
  // 获取技术指标
  getIndicators: (symbol: string, params?: {
    interval?: string
    indicators?: string
  }) => apiClient.get(`/analytics/indicators/${symbol}`, { params }),

  // 获取趋势分析
  getTrends: (symbol: string, params?: { period?: string }) =>
    apiClient.get(`/analytics/trends/${symbol}`, { params }),

  // 获取相关性分析
  getCorrelation: (params: { symbols: string; period?: string }) =>
    apiClient.get('/analytics/correlation', { params }),

  // 获取流动性分析
  getLiquidity: (symbol: string, params?: { exchange?: string }) =>
    apiClient.get(`/analytics/liquidity/${symbol}`, { params }),
}
