import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { marketApi, tradesApi, alertsApi, analyticsApi } from '@/api/modules'

export const useMarketStore = defineStore('market', () => {
  // State
  const tickers = ref<any[]>([])
  const klines = ref<any[]>([])
  const orderBook = ref<any>(null)
  const loading = ref(false)

  // Getters
  const tickerCount = computed(() => tickers.value.length)

  // Actions
  const fetchTickers = async (params?: any) => {
    loading.value = true
    try {
      const response: any = await marketApi.getTickers(params)
      tickers.value = response || []
      return tickers.value
    } finally {
      loading.value = false
    }
  }

  const fetchKlines = async (symbol: string, params?: any) => {
    loading.value = true
    try {
      const response: any = await marketApi.getKlines(symbol, params)
      klines.value = response || []
      return klines.value
    } finally {
      loading.value = false
    }
  }

  const fetchOrderBook = async (symbol: string, params?: any) => {
    const response: any = await marketApi.getOrderBook(symbol, params?.limit, params?.exchange)
    orderBook.value = response
    return response
  }

  return {
    tickers,
    klines,
    orderBook,
    loading,
    tickerCount,
    fetchTickers,
    fetchKlines,
    fetchOrderBook,
  }
})

export const useAlertStore = defineStore('alert', () => {
  // State
  const rules = ref<any[]>([])
  const alerts = ref<any[]>([])
  const loading = ref(false)

  // Actions
  const fetchRules = async (params?: any) => {
    loading.value = true
    try {
      const response: any = await alertsApi.getRules(params)
      rules.value = response || []
      return rules.value
    } finally {
      loading.value = false
    }
  }

  const fetchAlerts = async (params?: any) => {
    loading.value = true
    try {
      const response: any = await alertsApi.getHistory(params)
      alerts.value = response || []
      return alerts.value
    } finally {
      loading.value = false
    }
  }

  const createRule = async (data: any) => {
    return await alertsApi.createRule(data)
  }

  return {
    rules,
    alerts,
    loading,
    fetchRules,
    fetchAlerts,
    createRule,
  }
})
