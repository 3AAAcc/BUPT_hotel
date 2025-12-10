<template>
  <div class="carousel-card">
    <div class="carousel-container">
      <div class="carousel-wrapper" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
        <div
          v-for="(image, index) in hotelImages"
          :key="index"
          class="carousel-slide"
        >
          <img :src="image.src" :alt="image.alt" class="hotel-image" />
        </div>
      </div>

      <!-- 轮播指示器 -->
      <div class="carousel-indicators">
        <button
          v-for="(_, index) in hotelImages"
          :key="index"
          :class="['indicator', { active: currentSlide === index }]"
          @click="goToSlide(index)"
        ></button>
      </div>
    </div>

    <div class="carousel-overlay">
      <h2 class="carousel-title">
        尊享舒适住宿体验
      </h2>
      <p class="carousel-subtitle">
        为您提供优质的住宿环境和智能化的温控服务
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

// 酒店图片数据
const hotelImages = [
  {
    src: new URL('../../assets/homepage1.png', import.meta.url).href,
    alt: '送风设施'
  },
  {
    src: new URL('../../assets/homepage2.png', import.meta.url).href,
    alt: '豪华套房'
  },
  {
    src: new URL('../../assets/homepage3.png', import.meta.url).href,
    alt: '酒店大堂'
  },
  {
    src: new URL('../../assets/homepage4.png', import.meta.url).href,
    alt: '酒店餐厅'
  }
];

// 轮播控制
const currentSlide = ref(0);
let slideInterval: number | null = null;

// 切换到指定幻灯片
const goToSlide = (index: number) => {
  currentSlide.value = index;
};

// 自动轮播
const startAutoSlide = () => {
  slideInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % hotelImages.length;
  }, 4000);
};

const stopAutoSlide = () => {
  if (slideInterval) {
    clearInterval(slideInterval);
    slideInterval = null;
  }
};

// 生命周期
onMounted(() => {
  startAutoSlide();
});

onUnmounted(() => {
  stopAutoSlide();
});
</script>

<style scoped>
/* 图片轮播卡片 */
.carousel-card {
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 60px;
  position: relative;
  width: 100%;
  max-width: 1700px;
  margin-left: auto;
  margin-right: auto;
}

.carousel-container {
  position: relative;
  width: 100%;
  height: 500px;
  overflow: hidden;
}

.carousel-wrapper {
  display: flex;
  height: 100%;
  transition: transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.carousel-slide {
  min-width: 100%;
  height: 100%;
}

.hotel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.carousel-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.75));
  color: #ffffff;
  padding: 60px 40px 40px;
  text-align: center;
  pointer-events: none;
}

.carousel-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8),
               0 4px 16px rgba(0, 0, 0, 0.6);
  letter-spacing: 1px;
}

.carousel-subtitle {
  font-size: 1.1rem;
  margin: 0;
  color: #ffffff;
  line-height: 1.6;
  font-weight: 500;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.8),
               0 3px 12px rgba(0, 0, 0, 0.6);
  letter-spacing: 0.5px;
}

/* 轮播指示器 */
.carousel-indicators {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  outline: none;
}

.indicator.active {
  background: #ffffff;
  width: 6px;
  height: 6px;
}

.indicator:hover {
  background: rgba(255, 255, 255, 0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .carousel-container {
    height: 350px;
  }

  .carousel-overlay {
    padding: 40px 20px 30px;
  }

  .carousel-title {
    font-size: 1.5rem;
  }

  .carousel-subtitle {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .carousel-container {
    height: 280px;
  }

  .carousel-overlay {
    padding: 30px 16px 24px;
  }

  .carousel-title {
    font-size: 1.25rem;
  }

  .carousel-subtitle {
    font-size: 0.9rem;
  }
}
</style>
