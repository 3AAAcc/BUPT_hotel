<template>
  <div class="control-section">
    <h3 class="section-title">
      目标温度
    </h3>
    <div class="temp-control-box">
      <div class="target-temp-display">
        {{ temperature }}°C
      </div>
      <div class="temp-buttons">
        <button class="btn-temp-adjust" @click="handleDecrease">
          -
        </button>
        <button class="btn-temp-adjust" @click="handleIncrease">
          +
        </button>
      </div>
      <input
        type="range"
        :value="temperature"
        :min="minTemp"
        :max="maxTemp"
        :step="step"
        class="temp-slider"
        @input="handleSliderChange"
      />
      <div class="temp-range-label">
        <span>{{ minTemp }}°C</span>
        <span>{{ maxTemp }}°C</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  temperature: number;
  minTemp: number;
  maxTemp: number;
  step: number;
}>();

const emit = defineEmits<{
  update: [temp: number];
}>();

const handleIncrease = () => {
  const newTemp = props.temperature + props.step;
  if (newTemp <= props.maxTemp) {
    emit('update', Math.round(newTemp * 2) / 2);
  }
};

const handleDecrease = () => {
  const newTemp = props.temperature - props.step;
  if (newTemp >= props.minTemp) {
    emit('update', Math.round(newTemp * 2) / 2);
  }
};

const handleSliderChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update', Number(target.value));
};
</script>

<style scoped>
.control-section {
  background: #ffffff;
  padding: 24px;
  border-radius: 12px;
  border: 2px solid #f0f9ff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: #334155;
  text-align: center;
}

.temp-control-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.target-temp-display {
  font-size: 56px;
  font-weight: 700;
  color: #067ef5;
  text-align: center;
  letter-spacing: -1px;
}

.temp-buttons {
  display: flex;
  gap: 24px;
  align-items: center;
}

.btn-temp-adjust {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 2px solid #e0f2fe;
  background: #f0f9ff;
  color: #067ef5;
  font-size: 24px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.btn-temp-adjust:hover {
  background: #067ef5;
  color: white;
  border-color: #067ef5;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(2, 132, 199, 0.2);
}

.temp-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #e0f2fe;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
}

.temp-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #067ef5;
  cursor: pointer;
  border: 4px solid white;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
  transition: all 0.2s;
}

.temp-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.temp-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #067ef5;
  cursor: pointer;
  border: 4px solid white;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
}

.temp-range-label {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}
</style>

