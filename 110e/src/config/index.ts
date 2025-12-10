/**
 * 应用配置
 */

// API 基础地址
// 优先使用环境变量，如果没有则使用默认值
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// 环境配置
export const config = {
  apiBaseUrl: API_BASE_URL,
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD
};

export default config;

