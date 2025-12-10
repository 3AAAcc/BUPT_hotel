<template>
  <div class="view-container">
    <AdminMonitor
      :service-queue="serviceQueue"
      :waiting-queue="waitingQueue"
      :all-rooms="allRooms"
      :max-service-objects="maxServiceObjects"
      :on-turn-off-all="handleTurnOffAll"
      :on-turn-on-all="handleTurnOnAll"
      :on-clear-waiting-queue="handleClearWaitingQueue"
      :on-force-refresh="handleForceRefresh"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import AdminMonitor from '../admin/AdminMonitor.vue';
import type { IHvacService } from '../../services/ApiAdapter';
import type { RoomState, ServiceObject, WaitingObject } from '../../types/index';

const props = defineProps<{
  hvacService: IHvacService;
  serviceQueue: ServiceObject[];
  waitingQueue: WaitingObject[];
  allRooms: RoomState[];
  maxServiceObjects: number;
}>();

const emit = defineEmits<{
  refresh: [];
}>();

// 管理员页面的定时刷新器
let adminRefreshTimer: ReturnType<typeof setInterval> | null = null;

// 页面加载时启动实时监控
onMounted(async () => {
  if (props.hvacService.refreshQueues && props.hvacService.refreshRoomStates) {
    await Promise.all([
      props.hvacService.refreshQueues(),
      props.hvacService.refreshRoomStates()
    ]);
    emit('refresh');

    // 启动定时刷新（每秒）
    adminRefreshTimer = setInterval(async () => {
      if (props.hvacService.refreshQueues && props.hvacService.refreshRoomStates) {
        await Promise.all([
          props.hvacService.refreshQueues(),
          props.hvacService.refreshRoomStates()
        ]);
        emit('refresh');
      }
    }, 1000);
  }
});

// 清理定时器
onUnmounted(() => {
  if (adminRefreshTimer) {
    clearInterval(adminRefreshTimer);
  }
});

// 管理员操作
const handleTurnOffAll = async () => {
  if (props.hvacService.turnOffAll) {
    await props.hvacService.turnOffAll();
    emit('refresh');
  }
};

const handleTurnOnAll = async () => {
  if (props.hvacService.turnOnAll) {
    await props.hvacService.turnOnAll();
    emit('refresh');
  }
};

const handleClearWaitingQueue = async () => {
  if (props.hvacService.clearWaitingQueue) {
    await props.hvacService.clearWaitingQueue();
    emit('refresh');
  }
};

const handleForceRefresh = () => {
  if (props.hvacService.updateServiceMetrics) {
    props.hvacService.updateServiceMetrics();
  }
  emit('refresh');
};
</script>

<style scoped>
.view-container {
  width: 100%;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>

