<template>
  <div class="flex flex-col min-h-screen">
    <header class="header p-4 flex justify-between items-center shadow-md">
      <h1 class="text-2xl font-semibold">VantaLedger</h1>
      <div class="flex items-center space-x-4">
        <button @click="$emit('logout')" class="btn-primary px-4 py-2 rounded shadow hover:shadow-lg transition">
          Logout
        </button>
        <button @click="exportTransactions" class="ml-4 px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700 transition" aria-label="Export Transactions">
          Export
        </button>
        <button @click="toggleDarkMode" class="ml-4 px-3 py-2 rounded bg-gray-300 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-400 dark:hover:bg-gray-600 transition" aria-label="Toggle Dark Mode">
          <i :class="darkMode ? 'fas fa-sun' : 'fas fa-moon'"></i>
        </button>
        <a href="/api" target="_blank" class="ml-4 text-blue-300 hover:underline">API Root</a>
        <a href="/docs" target="_blank" class="ml-4 text-blue-300 hover:underline">Swagger UI</a>
        <a href="/redoc" target="_blank" class="ml-4 text-blue-300 hover:underline">ReDoc</a>
      </div>
    </header>

    <main class="flex-grow container mx-auto p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
      <section class="md:col-span-2">
        <h2 class="text-xl font-semibold mb-4">Transactions</h2>
        <div class="overflow-x-auto">
          <table class="w-full border-collapse shadow rounded overflow-hidden">
            <thead class="table-header">
              <tr>
                <th class="p-3 text-left">ID</th>
                <th class="p-3 text-left">Type</th>
                <th class="p-3 text-left">Amount</th>
                <th class="p-3 text-left">Description</th>
                <th class="p-3 text-left">Date</th>
                <th class="p-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="transactions.length === 0">
                <td colspan="6" class="p-3 text-center text-gray-500">No transactions found.</td>
              </tr>
              <tr v-for="tx in transactions" :key="tx.id" class="table-row">
                <td class="p-3">{{ tx.id }}</td>
                <td class="p-3 capitalize">{{ tx.type }}</td>
                <td class="p-3">${{ tx.amount.toFixed(2) }}</td>
                <td class="p-3">{{ tx.description }}</td>
                <td class="p-3">{{ formatDate(tx.date) }}</td>
                <td class="p-3 space-x-2">
                  <button @click="startEditTransaction(tx)" class="text-blue-600 hover:underline">Edit</button>
                  <button @click="deleteTransaction(tx.id)" class="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="bg-white dark:bg-gray-800 p-4 rounded shadow max-h-[600px] overflow-y-auto">
        <h2 class="text-xl font-semibold mb-4">{{ editingTransaction ? 'Update' : 'Add' }} Transaction</h2>
        <form @submit.prevent="submitTransaction" class="space-y-4">
          <input type="hidden" v-model="transactionForm.id" />
          <div>
            <label for="type" class="block font-medium mb-1">Type</label>
            <select id="type" v-model="transactionForm.type" class="input-field" required>
              <option value="" disabled>Select type</option>
              <option value="sale">Sale</option>
              <option value="expenditure">Expenditure</option>
            </select>
          </div>
          <div>
            <label for="amount" class="block font-medium mb-1">Amount</label>
            <input id="amount" type="number" v-model.number="transactionForm.amount" step="0.01" min="0" class="input-field" required />
          </div>
          <div>
            <label for="description" class="block font-medium mb-1">Description</label>
            <input id="description" type="text" v-model="transactionForm.description" maxlength="255" class="input-field" required />
          </div>
          <div>
            <label for="date" class="block font-medium mb-1">Date</label>
            <input id="date" type="date" v-model="transactionForm.date" class="input-field" required />
          </div>
          <div class="flex space-x-4">
            <button type="submit" class="btn-primary px-4 py-2 rounded shadow hover:shadow-lg transition">
              {{ editingTransaction ? 'Update' : 'Save' }}
            </button>
            <button type="button" @click="resetForm" class="px-4 py-2 rounded border border-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
              Cancel
            </button>
          </div>
        </form>
      </section>
    </main>
  </div>
</template>

<script>
import axios from 'axios'
import { ref, reactive } from 'vue'

export default {
  name: 'Dashboard',
  props: {
    authToken: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const transactions = ref([])
    const editingTransaction = ref(false)
    const transactionForm = reactive({
      id: null,
      type: '',
      amount: null,
      description: '',
      date: '',
    })
    const darkMode = ref(false)

    function formatDate(dateStr) {
      return new Date(dateStr).toLocaleDateString()
    }

    async function loadTransactions() {
      try {
        const res = await axios.get('/api/transactions', {
          headers: { access_token: props.authToken },
        })
        transactions.value = res.data
      } catch (error) {
        alert('Failed to load transactions')
        console.error(error)
      }
    }

    function startEditTransaction(tx) {
      editingTransaction.value = true
      transactionForm.id = tx.id
      transactionForm.type = tx.type
      transactionForm.amount = tx.amount
      transactionForm.description = tx.description
      transactionForm.date = tx.date.split('T')[0]
    }

    async function deleteTransaction(id) {
      if (!confirm('Are you sure you want to delete this transaction?')) return
      try {
        await axios.delete(`/api/transactions/${id}`, {
          headers: { access_token: props.authToken },
        })
        await loadTransactions()
      } catch (error) {
        alert('Failed to delete transaction')
        console.error(error)
      }
    }

    async function submitTransaction() {
      try {
        if (editingTransaction.value) {
          await axios.put(`/api/transactions/${transactionForm.id}`, {
            amount: transactionForm.amount,
            type: transactionForm.type,
            description: transactionForm.description,
            date: transactionForm.date,
          }, {
            headers: { access_token: props.authToken },
          })
        } else {
          await axios.post('/api/transactions', {
            amount: transactionForm.amount,
            type: transactionForm.type,
            description: transactionForm.description,
            date: transactionForm.date,
          }, {
            headers: { access_token: props.authToken },
          })
        }
        resetForm()
        await loadTransactions()
      } catch (error) {
        alert('Failed to save transaction')
        console.error(error)
      }
    }

    function resetForm() {
      editingTransaction.value = false
      transactionForm.id = null
      transactionForm.type = ''
      transactionForm.amount = null
      transactionForm.description = ''
      transactionForm.date = ''
    }

    function toggleDarkMode() {
      darkMode.value = !darkMode.value
      if (darkMode.value) {
        document.body.classList.add('dark')
      } else {
        document.body.classList.remove('dark')
      }
    }

    loadTransactions()

    return {
      transactions,
      editingTransaction,
      transactionForm,
      formatDate,
      startEditTransaction,
      deleteTransaction,
      submitTransaction,
      resetForm,
      toggleDarkMode,
      darkMode,
    }
  },
}
</script>

<style scoped>
.input-field {
  width: 100%;
  max-width: 100%;
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
.table-header {
  background-color: #e0e7ff;
}
body.dark .table-header {
  background-color: #374151;
}
.table-row:hover {
  background-color: #f3f4f6;
}
body.dark .table-row:hover {
  background-color: #4b5563;
}
</style>
