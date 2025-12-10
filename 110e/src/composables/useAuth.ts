import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import type { UserRole } from '../components/views/Login.vue';

type ViewType = 'room' | 'admin' | 'frontdesk' | 'manager';

// 角色权限映射
const rolePermissions: Record<UserRole, ViewType[]> = {
  guest: ['room'],
  admin: ['admin'],
  frontdesk: ['frontdesk'],
  manager: ['manager'],
  superadmin: ['room', 'admin', 'frontdesk', 'manager']
};

// 角色名称映射
const roleNames: Record<UserRole, string> = {
  guest: '房客',
  admin: '管理员',
  frontdesk: '前台',
  manager: '经理',
  superadmin: '超级管理员'
};

export function useAuth() {
  const router = useRouter();
  const route = useRoute();

  const currentUser = ref<UserRole | null>(null);
  const userName = ref<string>('');

  // 当前视图从路由中获取
  const currentView = computed(() => {
    const routeName = route.name as string;
    if (['room', 'admin', 'frontdesk', 'manager'].includes(routeName)) {
      return routeName as ViewType;
    }
    return 'room';
  });

  // 登录处理
  const handleLogin = async (role: UserRole) => {
    currentUser.value = role;
    userName.value = roleNames[role] || '';

    // 根据角色自动跳转到对应的默认视图
    const permissions = rolePermissions[role];
    if (permissions && permissions.length > 0 && permissions[0]) {
      const defaultView = permissions[0];
      await router.push(`/app/${defaultView}`);
    }
  };

  // 登出处理
  const handleLogout = async () => {
    currentUser.value = null;
    userName.value = '';
    await router.push('/');
  };

  // 检查权限
  const hasPermission = (view: ViewType): boolean => {
    if (!currentUser.value) return false;
    const permissions = rolePermissions[currentUser.value];
    return permissions ? permissions.includes(view) : false;
  };

  // 可访问的视图
  const availableViews = computed(() => {
    if (!currentUser.value) return [];
    return rolePermissions[currentUser.value];
  });

  // 切换视图（使用路由跳转）
  const switchView = async (view: ViewType) => {
    await router.push(`/app/${view}`);
  };

  return {
    currentUser,
    userName,
    currentView,
    availableViews,
    handleLogin,
    handleLogout,
    hasPermission,
    switchView
  };
}

