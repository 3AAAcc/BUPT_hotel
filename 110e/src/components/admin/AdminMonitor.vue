<template>
  <div class="admin-monitor">
    <div class="monitor-header">
      <h1>空调管理员监控面板</h1>
      <div class="refresh-info">
        <span>自动刷新中...</span>
      </div>
    </div>

    <!-- 管理功能按钮 -->
    <div class="admin-actions">
      <button class="action-btn btn-danger" title="关闭所有房间的空调" @click="handleTurnOffAll">
        一键关机
      </button>
      <button class="action-btn btn-success" title="开启所有房间的空调" @click="handleTurnOnAll">
        一键开机
      </button>
      <button
        class="action-btn btn-warning"
        :disabled="waitingQueue.length === 0"
        title="清空等待队列"
        @click="handleClearWaitingQueue"
      >
        清空队列
      </button>
      <button class="action-btn btn-info" title="强制刷新所有数据" @click="handleForceRefresh">
        刷新数据
      </button>
    </div>

    <!-- 系统概览 -->
    <SystemOverview
      :total-rooms="allRooms.length"
      :serving-rooms="servingRooms"
      :waiting-rooms="waitingQueue.length"
      :total-cost="totalCost"
    />

    <!-- 服务队列 -->
    <QueueList
      title="服务队列"
      :items="servingRoomsList"
      :max-count="maxServiceObjects"
      queue-type="serving"
      empty-message="暂无房间正在服务中"
      left-label="服务时长"
      right-label="累计费用"
      :left-value="formatServiceDuration"
      :right-value="formatCost"
      :get-progress="getRoomProgressPercent"
    />

    <!-- 等待队列 -->
    <QueueList
      title="等待队列"
      :items="waitingRoomsList"
      queue-type="waiting"
      empty-message="等待队列为空"
      left-label="已等待"
      right-label="分配时长"
      :left-value="formatWaitDuration"
      :right-value="formatAssignedWaitTime"
      :get-progress="getWaitProgress"
    />

    <!-- 所有房间状态 -->
    <RoomStatusGrid :all-rooms="allRooms" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { ServiceObject, WaitingObject, RoomState } from '../../types/index';
import { RoomStatus } from '../../types/index';
import SystemOverview from './SystemOverview.vue';
import QueueList from './QueueList.vue';
import RoomStatusGrid from './RoomStatusGrid.vue';
import { showConfirm } from '../../composables/useDialog';

const props = defineProps<{
  serviceQueue: ServiceObject[];
  waitingQueue: WaitingObject[];
  allRooms: RoomState[];
  maxServiceObjects: number;
  onTurnOffAll?: () => void;
  onTurnOnAll?: () => void;
  onClearWaitingQueue?: () => void;
  onForceRefresh?: () => void;
}>();

const servingRoomsList = computed(() =>
  props.allRooms.filter(r => r.status === RoomStatus.SERVING).map(room => {
    const service = props.serviceQueue.find(s => s.roomId === room.roomId);
    return { ...room, serviceDuration: service?.serviceDuration || 0 };
  })
);

const waitingRoomsList = computed(() =>
  props.allRooms.filter(r => r.status === RoomStatus.WAITING).map(room => {
    const waiting = props.waitingQueue.find(w => w.roomId === room.roomId);
    return {
      ...room,
      waitDuration: waiting?.waitDuration || 0,
      assignedWaitTime: waiting?.assignedWaitTime || 120
    };
  })
);

const servingRooms = computed(() => servingRoomsList.value.length);

const totalCost = computed(() =>
  props.allRooms.reduce((sum, room) => sum + room.totalCost, 0)
);

const formatServiceDuration = (item: any): string => {
  const seconds = item.serviceDuration || 0;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return mins > 0 ? `${mins}分${secs}秒` : `${secs}秒`;
};

const formatCost = (item: any): string => {
  return `¥${item.totalCost.toFixed(2)}`;
};

const formatWaitDuration = (item: any): string => {
  return `${item.waitDuration || 0}秒`;
};

const formatAssignedWaitTime = (item: any): string => {
  return `${item.assignedWaitTime || 120}秒`;
};

const getRoomProgressPercent = (room: RoomState): number => {
  const tempDiff = Math.abs(room.initialTemp - room.targetTemp);
  if (tempDiff < 0.1) return 100;

  const tempChange = Math.abs(room.initialTemp - room.currentTemp);
  const progress = (tempChange / tempDiff) * 100;

  return Math.min(Math.max(progress, 0), 100);
};

const getWaitProgress = (item: any): number => {
  const waitDuration = item.waitDuration || 0;
  const assignedWaitTime = item.assignedWaitTime || 120;
  return Math.min((waitDuration / assignedWaitTime) * 100, 100);
};

const handleTurnOffAll = async () => {
  const confirmed = await showConfirm(
    '确认操作',
    '确定要关闭所有房间的空调吗？'
  );
  if (confirmed) {
    props.onTurnOffAll?.();
  }
};

const handleTurnOnAll = async () => {
  const confirmed = await showConfirm(
    '确认操作',
    '确定要开启所有房间的空调吗？'
  );
  if (confirmed) {
    props.onTurnOnAll?.();
  }
};

const handleClearWaitingQueue = async () => {
  const confirmed = await showConfirm(
    '清空等待队列',
    '确定要清空等待队列吗？所有等待中的房间将停止等待。'
  );
  if (confirmed) {
    props.onClearWaitingQueue?.();
  }
};

const handleForceRefresh = () => {
  props.onForceRefresh?.();
};
</script>

<style scoped>
.admin-monitor {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 16px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.monitor-header h1 {
  margin: 0;
  color: #1e293b;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.refresh-info {
  color: #059669;
  font-size: 14px;
  font-weight: 500;
}

.admin-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 28px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn:active:not(:disabled) {
  transform: translateY(0);
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.btn-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
}

.btn-info {
  background: linear-gradient(135deg, #067ef5 0%, #0369a1 100%);
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #2563eb;
}
</style>
