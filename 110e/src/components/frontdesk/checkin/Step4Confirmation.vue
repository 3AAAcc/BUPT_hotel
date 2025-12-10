<template>
  <div class="step-content">
    <div class="step-header">
      <h3>第四步：确认信息与押金</h3>
      <p class="step-description">
        请核对入住信息并收取押金
      </p>
    </div>

    <div class="summary-container">
      <!-- 入住信息 -->
      <div class="summary-section">
        <h4>入住信息</h4>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="label">房间号：</span>
            <span class="value">{{ formData.roomId }}</span>
          </div>
          <div class="summary-item">
            <span class="label">客户姓名：</span>
            <span class="value">{{ formData.guestName }}</span>
          </div>
          <div class="summary-item">
            <span class="label">联系电话：</span>
            <span class="value">{{ formData.guestPhone }}</span>
          </div>
          <div class="summary-item">
            <span class="label">证件类型：</span>
            <span class="value">{{ getIdTypeText(formData.idType) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">证件号码：</span>
            <span class="value">{{ maskIdNumber(formData.idNumber) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">入住天数：</span>
            <span class="value">{{ formData.stayDays }} 天</span>
          </div>
          <div class="summary-item">
            <span class="label">空调模式：</span>
            <span class="value">{{ formData.mode === 'COOLING' ? '制冷' : '制热' }}</span>
          </div>
          <div v-if="formData.specialRequest" class="summary-item full-width">
            <span class="label">特殊需求：</span>
            <span class="value">{{ formData.specialRequest }}</span>
          </div>
        </div>
      </div>

      <!-- 费用明细 -->
      <div class="summary-section payment">
        <h4>费用明细</h4>
        <div class="payment-details">
          <div class="payment-item">
            <span>房费</span>
            <span>¥{{ (roomPrice * formData.stayDays).toFixed(2) }}</span>
          </div>
          <div class="payment-item">
            <span>服务费</span>
            <span>¥0.00</span>
          </div>
          <div class="payment-item total">
            <span>预计总费用</span>
            <span>¥{{ (roomPrice * formData.stayDays).toFixed(2) }}</span>
          </div>

          <div class="divider"></div>

          <div class="deposit-section">
            <div class="deposit-header">
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M12 2v20M17 5H9.5a3.5 3.5 0 100 7h5a3.5 3.5 0 110 7H6"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
              <span>押金信息</span>
            </div>
            <div class="deposit-amount">
              <span>应收押金</span>
              <span class="amount">¥200.00</span>
            </div>
            <label class="deposit-checkbox">
              <input v-model="depositPaid" type="checkbox" />
              <span>已收取押金</span>
            </label>
          </div>
        </div>
      </div>

      <!-- 确认按钮 -->
      <div class="action-buttons">
        <button type="button" class="btn-secondary" @click="$emit('prev')">
          返回上一步
        </button>
        <button
          type="button"
          class="btn-primary"
          :disabled="!depositPaid"
          @click="handleConfirm"
        >
          确认办理入住
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface CheckInFormData {
  roomId: string;
  guestName: string;
  guestPhone: string;
  idType: string;
  idNumber: string;
  stayDays: number;
  specialRequest: string;
  mode: string;
}

const { formData, roomPrice } = defineProps<{
  formData: CheckInFormData;
  roomPrice: number;
}>();

const emit = defineEmits<{
  'confirm': [];
  'prev': [];
}>();

const depositPaid = ref(false);

// 获取证件类型文字
const getIdTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    'id_card': '身份证',
    'passport': '护照',
    'other': '其他'
  };
  return typeMap[type] || '身份证';
};

// 掩码处理证件号码
const maskIdNumber = (idNumber: string): string => {
  if (!idNumber) return '';
  if (idNumber.length <= 8) {
    return idNumber;
  }
  const start = idNumber.slice(0, 4);
  const end = idNumber.slice(-4);
  const middle = '*'.repeat(idNumber.length - 8);
  return `${start}${middle}${end}`;
};

// 确认办理
const handleConfirm = () => {
  if (!depositPaid.value) {
    alert('请先收取押金');
    return;
  }
  emit('confirm');
};
</script>

<style scoped>
.step-content {
  padding: 20px;
}

.step-header {
  margin-bottom: 24px;
}

.step-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.step-description {
  font-size: 14px;
  color: #64748b;
}

.summary-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.summary-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.summary-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.summary-item.full-width {
  grid-column: span 2;
}

.summary-item .label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.summary-item .value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 600;
  text-align: right;
}

.payment-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.payment-item span:first-child {
  color: #64748b;
}

.payment-item span:last-child {
  color: #1e293b;
  font-weight: 500;
}

.payment-item.total {
  font-size: 16px;
  font-weight: 600;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.payment-item.total span:last-child {
  color: #ef4444;
  font-size: 18px;
}

.divider {
  height: 1px;
  background: #e2e8f0;
  margin: 16px 0;
}

.deposit-section {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 8px;
  padding: 16px;
}

.deposit-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #78350f;
}

.deposit-header svg {
  stroke: #78350f;
}

.deposit-amount {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
}

.deposit-amount .amount {
  font-size: 18px;
  font-weight: 600;
  color: #dc2626;
}

.deposit-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #78350f;
  cursor: pointer;
}

.deposit-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 24px;
}

.btn-secondary,
.btn-primary {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-secondary {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f8fafc;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  flex: 1;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
