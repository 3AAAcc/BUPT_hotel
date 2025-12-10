/**
 * 空调状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getACState } from '@/api/ac'

export const useACStore = defineStore('ac', () => {
  const currentRoomId = ref(null)
  const roomState = ref(null)
  const loading = ref(false)

  // 获取房间状态
  async function fetchRoomState(roomId) {
    loading.value = true
    try {
      const data = await getACState(roomId)
      roomState.value = data
      currentRoomId.value = roomId
      return data
    } catch (error) {
      console.error('获取房间状态失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 刷新当前房间状态
  async function refreshState() {
    if (currentRoomId.value) {
      return await fetchRoomState(currentRoomId.value)
    }
  }

  return {
    currentRoomId,
    roomState,
    loading,
    fetchRoomState,
    refreshState
  }
})

