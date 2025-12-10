<template>
  <div class="step-content">
    <div class="step-header">
      <div class="header-content">
        <h3>第二步：填写客户信息</h3>
        <p class="step-description">
          请填写入住客户的真实信息
        </p>
      </div>
      <button class="btn-quick-fill" type="button" @click="fillDefaultGuest">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          style="margin-right: 6px;"
        >
          <path
            d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M8.5 11a4 4 0 100-8 4 4 0 000 8zM20 8v6M23 11h-6"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          />
        </svg>
        快速填充（张三）
      </button>
    </div>

    <div class="form-container">
      <div class="form-row">
        <div class="form-group required">
          <label>客户姓名：<span class="required-mark">*</span></label>
          <input
            v-model="formData.guestName"
            type="text"
            placeholder="请输入客户真实姓名"
            maxlength="20"
            required
          />
        </div>
        <div class="form-group required">
          <label>联系电话：<span class="required-mark">*</span></label>
          <input
            v-model="formData.guestPhone"
            type="tel"
            placeholder="请输入11位手机号"
            maxlength="11"
            pattern="[0-9]{11}"
            required
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>证件类型：</label>
          <select v-model="formData.idType">
            <option value="id_card">
              身份证
            </option>
            <option value="passport">
              护照
            </option>
            <option value="other">
              其他
            </option>
          </select>
        </div>
        <div class="form-group required">
          <label>证件号码：<span class="required-mark">*</span></label>
          <input
            v-model="formData.idNumber"
            type="text"
            placeholder="请输入证件号码"
            maxlength="30"
            required
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group required">
          <label>入住天数：<span class="required-mark">*</span></label>
          <input
            v-model.number="formData.stayDays"
            type="number"
            placeholder="请输入入住天数"
            min="1"
            max="365"
            required
          />
          <span class="input-hint">天</span>
        </div>
        <div class="form-group">
          <label>特殊需求：</label>
          <input
            v-model="formData.specialRequest"
            type="text"
            placeholder="如需高楼层、无烟房等"
            maxlength="100"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue';

interface GuestInfo {
  guestName: string;
  guestPhone: string;
  idType: string;
  idNumber: string;
  stayDays: number;
  specialRequest: string;
}

const props = defineProps<{
  modelValue: GuestInfo;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: GuestInfo];
}>();

const formData = reactive<GuestInfo>({
  guestName: props.modelValue?.guestName || '',
  guestPhone: props.modelValue?.guestPhone || '',
  idType: props.modelValue?.idType || 'id_card',
  idNumber: props.modelValue?.idNumber || '',
  stayDays: props.modelValue?.stayDays || 1,
  specialRequest: props.modelValue?.specialRequest || ''
});

// 监听数据变化并同步
watch(formData, (newValue) => {
  emit('update:modelValue', { ...newValue });
}, { deep: true });

// 快速填充默认客户
const fillDefaultGuest = () => {
  formData.guestName = '张三';
  formData.guestPhone = '13800138000';
  formData.idNumber = '110101199001011234';
  formData.idType = 'id_card';
  formData.stayDays = 2;
};
</script>

<style scoped>
.step-content {
  padding: 20px;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.step-description {
  font-size: 14px;
  color: #64748b;
}

.btn-quick-fill {
  padding: 8px 16px;
  background: linear-gradient(135deg, #a855f7, #9333ea);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.btn-quick-fill:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

.form-container {
  background: #f8fafc;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
}

.form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.required label::after {
  content: '';
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 4px;
}

.required-mark {
  color: #ef4444;
  font-weight: normal;
}

.form-group input,
.form-group select {
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  color: #334155;
  background: white;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input[type="number"] {
  appearance: textfield;
}

.input-hint {
  font-size: 14px;
  color: #64748b;
  padding-left: 8px;
}
</style>
