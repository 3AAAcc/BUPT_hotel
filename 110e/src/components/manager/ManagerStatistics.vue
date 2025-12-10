<template>
  <div class="manager-statistics">
    <div class="stats-header">
      <h1>统计报表系统</h1>
    </div>

    <!-- 时间范围选择 -->
    <TimeRangeSelector
      v-model:start-time="startTimeInput"
      v-model:end-time="endTimeInput"
      @generate="generateReport"
      @select-today="selectToday"
      @select-week="selectThisWeek"
      @select-month="selectThisMonth"
      @select-all="selectAll"
    />

    <!-- 统计报表 -->
    <div v-if="report" class="report-section">
      <div class="report-header">
        <h2>统计报表</h2>
        <button class="btn-print" @click="printReport">
          打印报表
        </button>
      </div>

      <!-- 总体统计 -->
      <StatisticsOverview
        :total-rooms="report.totalRooms"
        :total-requests="report.totalServiceRequests"
        :total-power="report.totalPowerConsumption"
        :total-cost="report.totalCost"
        :avg-cost="report.averageCostPerRoom"
      />

      <!-- 风速使用分布 -->
      <FanSpeedChart
        :high="report.fanSpeedDistribution.high"
        :medium="report.fanSpeedDistribution.medium"
        :low="report.fanSpeedDistribution.low"
      />

      <!-- 房间明细统计 -->
      <RoomDetailsTable :room-stats="report.roomStatistics" />

      <!-- 时间信息 -->
      <div class="report-footer">
        <div class="time-range-info">
          <strong>统计时间范围：</strong>
          <span>{{ formatDateTime(report.startTime) }}</span>
          <span> 至 </span>
          <span>{{ formatDateTime(report.endTime) }}</span>
        </div>
        <div class="generate-time">
          生成时间：{{ formatDateTime(Date.now()) }}
        </div>
      </div>
    </div>

    <div v-else class="no-report">
      <p>请选择时间范围并生成报表</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { StatisticsReport } from '../../types/index';
import TimeRangeSelector from './TimeRangeSelector.vue';
import StatisticsOverview from './StatisticsOverview.vue';
import FanSpeedChart from './FanSpeedChart.vue';
import RoomDetailsTable from './RoomDetailsTable.vue';
import { showWarning } from '../../composables/useDialog';

const props = defineProps<{
  onGenerateReport: (startTime: number, endTime: number) => Promise<StatisticsReport>;
}>();

const startTimeInput = ref('');
const endTimeInput = ref('');
const report = ref<StatisticsReport | null>(null);

const selectToday = () => {
  const now = new Date();
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);

  startTimeInput.value = formatInputDateTime(startOfDay);
  endTimeInput.value = formatInputDateTime(endOfDay);
};

const selectThisWeek = () => {
  const now = new Date();
  const dayOfWeek = now.getDay();
  const startOfWeek = new Date(now);
  startOfWeek.setDate(now.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
  startOfWeek.setHours(0, 0, 0, 0);

  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 6);
  endOfWeek.setHours(23, 59, 59);

  startTimeInput.value = formatInputDateTime(startOfWeek);
  endTimeInput.value = formatInputDateTime(endOfWeek);
};

const selectThisMonth = () => {
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);

  startTimeInput.value = formatInputDateTime(startOfMonth);
  endTimeInput.value = formatInputDateTime(endOfMonth);
};

const selectAll = () => {
  const now = new Date();
  // 限制最早时间为30天前，避免查询过多数据
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

  startTimeInput.value = formatInputDateTime(thirtyDaysAgo);
  endTimeInput.value = formatInputDateTime(now);
};

const generateReport = async () => {
  if (!startTimeInput.value || !endTimeInput.value) {
    showWarning('请选择时间范围');
    return;
  }

  const startTime = new Date(startTimeInput.value).getTime();
  const endTime = new Date(endTimeInput.value).getTime();

  if (startTime >= endTime) {
    showWarning('结束时间必须晚于开始时间');
    return;
  }

  report.value = await props.onGenerateReport(startTime, endTime);
};

const printReport = () => {
  if (!report.value) return;

  const printWindow = window.open('', '_blank');
  if (!printWindow) return;

  const reportHtml = generatePrintHTML(report.value);
  printWindow.document.write(reportHtml);
  printWindow.document.close();
  printWindow.print();
};

const generatePrintHTML = (rep: StatisticsReport): string => {
  const getFanSpeedText = (speed: string) => {
    const map: Record<string, string> = { low: '低风', medium: '中风', high: '高风' };
    return map[speed] || '未知';
  };

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>统计报表</title>
      <style>
        body { font-family: 'Microsoft YaHei', sans-serif; padding: 20px; max-width: 1000px; margin: 0 auto; }
        .header { text-align: center; border-bottom: 3px solid #333; padding-bottom: 15px; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px; }
        .summary-item { padding: 15px; background: #f5f5f5; border-radius: 8px; text-align: center; }
        .summary-item .value { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
        .summary-item .label { color: #666; font-size: 14px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: center; }
        th { background: #333; color: white; }
        .time-range { margin-top: 30px; padding-top: 20px; border-top: 2px solid #ccc; text-align: center; color: #666; }
      </style>
    </head>
    <body>
      <div class="header"><h1>空调系统统计报表</h1></div>
      <div class="summary">
        <div class="summary-item"><div class="value">${rep.totalRooms}</div><div class="label">使用房间数</div></div>
        <div class="summary-item"><div class="value">${rep.totalServiceRequests}</div><div class="label">服务请求次数</div></div>
        <div class="summary-item"><div class="value">${rep.totalPowerConsumption.toFixed(2)}</div><div class="label">总耗电量(度)</div></div>
        <div class="summary-item"><div class="value">¥${rep.totalCost.toFixed(2)}</div><div class="label">总费用</div></div>
        <div class="summary-item"><div class="value">¥${rep.averageCostPerRoom.toFixed(2)}</div><div class="label">平均费用/房间</div></div>
      </div>
      <h3>风速使用统计</h3>
      <p>高风：${rep.fanSpeedDistribution.high} 次 | 中风：${rep.fanSpeedDistribution.medium} 次 | 低风：${rep.fanSpeedDistribution.low} 次</p>
      <h3>房间明细统计</h3>
      <table>
        <thead>
          <tr><th>房间号</th><th>服务次数</th><th>总耗电(度)</th><th>总费用(元)</th><th>平均温度</th><th>常用风速</th></tr>
        </thead>
        <tbody>
          ${rep.roomStatistics.map(stat => `
            <tr>
              <td>${stat.roomId}</td>
              <td>${stat.serviceCount}</td>
              <td>${stat.totalPowerConsumption.toFixed(2)}</td>
              <td>¥${stat.totalCost.toFixed(2)}</td>
              <td>${stat.averageTemp.toFixed(1)}°C</td>
              <td>${getFanSpeedText(stat.mostUsedFanSpeed)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      <div class="time-range">
        <p>统计时间范围：${formatDateTime(rep.startTime)} 至 ${formatDateTime(rep.endTime)}</p>
        <p>生成时间：${formatDateTime(Date.now())}</p>
      </div>
    </body>
    </html>
  `;
};

const formatDateTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleString('zh-CN');
};

const formatInputDateTime = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};
</script>

<style scoped>
.manager-statistics {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 16px;
}

.stats-header {
  margin-bottom: 24px;
  padding: 32px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.stats-header h1 {
  margin: 0;
  color: #1e293b;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.report-section {
  margin-bottom: 24px;
  padding: 32px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e2e8f0;
}

h2 {
  margin: 0;
  color: #1e293b;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.btn-print {
  padding: 12px 28px;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 8px rgba(5, 150, 105, 0.2);
}

.btn-print:hover {
  background: linear-gradient(135deg, #047857 0%, #065f46 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(5, 150, 105, 0.3);
}

.btn-print:active {
  transform: translateY(0);
}

.report-footer {
  margin-top: 40px;
  padding: 24px;
  background: #f8fafc;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  text-align: center;
  color: #64748b;
}

.time-range-info {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
}

.time-range-info strong {
  color: #475569;
}

.time-range-info span {
  color: #067ef5;
  font-weight: 600;
}

.no-report {
  text-align: center;
  padding: 80px 40px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 2px dashed #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  color: #94a3b8;
  font-size: 16px;
  font-weight: 500;
}

.generate-time {
  font-size: 13px;
  color: #94a3b8;
}
</style>
