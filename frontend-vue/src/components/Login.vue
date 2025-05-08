<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-6">
    <h1 class="text-3xl font-bold mb-6">VantaLedger Login</h1>
    <input
      v-model="accessToken"
      type="password"
      placeholder="Access Token"
      class="input-field max-w-xs mb-4 p-2 border border-gray-300 rounded"
      @keyup.enter="login"
    />
    <button
      @click="login"
      class="btn-primary px-6 py-3 rounded shadow hover:shadow-lg transition"
      :disabled="loading"
    >
      {{ loading ? 'Logging in...' : 'Login' }}
    </button>
    <p v-if="error" class="text-red-600 mt-4">{{ error }}</p>
    <div class="mt-6 space-x-4">
      <a href="/api" target="_blank" class="text-blue-600 hover:underline">API Root</a>
      <a href="/docs" target="_blank" class="text-blue-600 hover:underline">Swagger UI</a>
      <a href="/redoc" target="_blank" class="text-blue-600 hover:underline">ReDoc</a>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  data() {
    return {
      accessToken: '',
      loading: false,
      error: null,
    }
  },
  methods: {
    async login() {
      if (!this.accessToken) {
        this.error = 'Please enter an access token'
        return
      }
      this.loading = true
      this.error = null
      try {
        const response = await axios.post('/api/verify', null, {
          headers: { access_token: this.accessToken },
        })
        if (response.status === 200) {
          this.$emit('login-success', this.accessToken)
        } else {
          this.error = 'Invalid token'
        }
      } catch (err) {
        this.error = 'Login failed: ' + (err.response?.data?.detail || err.message)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.input-field {
  width: 100%;
  max-width: 320px;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
  transition: border-color 0.3s ease;
}
.input-field:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.5);
}
.btn-primary {
  background-color: #2563eb;
  color: white;
}
.btn-primary:hover {
  background-color: #1d4ed8;
}
</style>
