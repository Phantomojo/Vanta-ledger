// Base URL for backend API (same origin)
const API_BASE_URL = "/api";

// On page load, check for token in localStorage
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  if (token) {
    // Verify token by fetching transactions
    verifyToken(token);
  } else {
    showLogin();
  }
});

function showLogin() {
  document.getElementById("loginSection").style.display = "block";
  document.getElementById("appSection").style.display = "none";
  document.getElementById("loginError").style.display = "none";
}

function showApp() {
  document.getElementById("loginSection").style.display = "none";
  document.getElementById("appSection").style.display = "block";
  document.getElementById("loginError").style.display = "none";
  fetchTransactions();
}

function showLoading(show) {
  const loading = document.getElementById("loadingSpinner");
  if (loading) {
    loading.style.display = show ? "block" : "none";
  }
}

function showError(message) {
  const errorElem = document.getElementById("loginError");
  if (errorElem) {
    errorElem.textContent = message;
    errorElem.style.display = "block";
  }
}

// Verify token by calling protected endpoint
async function verifyToken(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: "GET",
      headers: {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
      }
    });
    if (response.ok) {
      localStorage.setItem("token", token);
      showApp();
    } else {
      localStorage.removeItem("token");
      showLogin();
      showError("Invalid access token");
    }
  } catch (error) {
    console.error(error);
    showLogin();
    showError("Error verifying token");
  }
}

// Handle login form submit
document.getElementById("loginButton").addEventListener("click", () => {
  const tokenInput = document.getElementById("accessTokenInput");
  const token = tokenInput.value.trim();
  if (!token) {
    showError("Please enter access token");
    return;
  }
  showLoading(true);
  verifyToken(token).finally(() => showLoading(false));
});

// Logout button handler
document.getElementById("logoutButton")?.addEventListener("click", () => {
  localStorage.removeItem("token");
  showLogin();
});

// Get auth headers with token from localStorage
function getAuthHeaders() {
  const token = localStorage.getItem("token");
  return {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
  };
}

// Render transactions in table
function renderTransactions(transactions) {
  const tbody = document.getElementById("transactionsTableBody");
  tbody.innerHTML = "";
  transactions.forEach(tx => {
    const tr = document.createElement("tr");
    tr.className = "table-row";

    tr.innerHTML = `
      <td class="p-3">${tx.id}</td>
      <td class="p-3 capitalize">${tx.type}</td>
      <td class="p-3">$${tx.amount.toFixed(2)}</td>
      <td class="p-3">${tx.description}</td>
      <td class="p-3">${new Date(tx.date).toLocaleDateString()}</td>
      <td class="p-3 space-x-2">
        <button class="text-blue-600 hover:underline" onclick="editTransaction(${tx.id})">Edit</button>
        <button class="text-red-600 hover:underline" onclick="deleteTransaction(${tx.id})">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Fetch transactions from backend
async function fetchTransactions() {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: "GET",
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`Error fetching transactions: ${response.statusText}`);
    }
    const transactions = await response.json();
    renderTransactions(transactions);
  } catch (error) {
    console.error(error);
    alert(error.message);
  }
}

// Create a new transaction
async function createTransaction(transaction) {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(transaction)
    });
    if (!response.ok) {
      throw new Error(`Error saving transaction: ${response.statusText}`);
    }
    fetchTransactions();
    resetForm();
  } catch (error) {
    console.error(error);
    alert(error.message);
  }
}

// Update a transaction
async function updateTransaction(transactionId, transaction) {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions/${transactionId}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(transaction)
    });
    if (!response.ok) {
      throw new Error(`Error updating transaction: ${response.statusText}`);
    }
    fetchTransactions();
    resetForm();
  } catch (error) {
    console.error(error);
    alert(error.message);
  }
}

// Delete a transaction
async function deleteTransaction(transactionId) {
  if (!confirm("Are you sure you want to delete this transaction?")) return;
  try {
    const response = await fetch(`${API_BASE_URL}/transactions/${transactionId}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`Error deleting transaction: ${response.statusText}`);
    }
    fetchTransactions();
  } catch (error) {
    console.error(error);
    alert(error.message);
  }
}

// Edit transaction: populate form with existing data
async function editTransaction(transactionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: "GET",
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`Error fetching transactions: ${response.statusText}`);
    }
    const transactions = await response.json();
    const tx = transactions.find(t => t.id === transactionId);
    if (!tx) {
      alert("Transaction not found");
      return;
    }
    document.getElementById("transactionId").value = tx.id;
    document.getElementById("type").value = tx.type;
    document.getElementById("amount").value = tx.amount;
    document.getElementById("description").value = tx.description;
    document.getElementById("date").value = tx.date.split("T")[0];
  } catch (error) {
    console.error(error);
    alert(error.message);
  }
}

// Reset form
function resetForm() {
  document.getElementById("transactionId").value = "";
  document.getElementById("type").value = "";
  document.getElementById("amount").value = "";
  document.getElementById("description").value = "";
  document.getElementById("date").value = "";
}

// Handle form submit
document.getElementById("transactionForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const transactionId = document.getElementById("transactionId").value;
  const transaction = {
    type: document.getElementById("type").value,
    amount: parseFloat(document.getElementById("amount").value),
    description: document.getElementById("description").value,
    date: document.getElementById("date").value
  };
  if (transactionId) {
    updateTransaction(parseInt(transactionId), transaction);
  } else {
    createTransaction(transaction);
  }
});

// Handle cancel button
document.getElementById("cancelButton").addEventListener("click", () => {
  resetForm();
});
