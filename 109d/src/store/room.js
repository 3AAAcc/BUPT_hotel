/**
 * 房间状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAllRooms } from '@/api/hotel'

export const useRoomStore = defineStore('room', () => {
  const rooms = ref([])
  const loading = ref(false)

  // 获取所有房间
  async function fetchAllRooms() {
    loading.value = true
    try {
      const data = await getAllRooms()
      rooms.value = data
      return data
    } catch (error) {
      console.error('获取房间列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 根据ID获取房间
  function getRoomById(roomId) {
    return rooms.value.find(room => room.id === roomId)
  }

  return {
    rooms,
    loading,
    fetchAllRooms,
    getRoomById
  }
})

