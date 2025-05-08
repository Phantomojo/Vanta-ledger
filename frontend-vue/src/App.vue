<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <Login v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
    <Dashboard v-else @logout="handleLogout" :authToken="authToken" />
  </div>
</template>

<script>
import { ref } from 'vue'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'

export default {
  components: {
    Login,
    Dashboard,
  },
  setup() {
    const isAuthenticated = ref(false)
    const authToken = ref(null)

    function handleLoginSuccess(token) {
      authToken.value = token
      isAuthenticated.value = true
    }

    function handleLogout() {
      authToken.value = null
      isAuthenticated.value = false
    }

    return {
      isAuthenticated,
      authToken,
      handleLoginSuccess,
      handleLogout,
    }
  },
}
</script>

<style>
/* Global styles can go here */
</style>
