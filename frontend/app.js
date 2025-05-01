// Base URL for backend API (same origin)
const API_BASE_URL = "/api";

// Function to get access token from input
function getAccessToken() {
  return document.getElementById("accessTokenInput").value.trim();
}

// Function to set Authorization header with API key
function getAuthHeaders() {
  const token = getAccessToken();
  return {
    "Content-Type": "application/json",
    "access_token": token
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

// Add transaction to table (refresh list)
function addTransactionToTable(transaction) {
  fetchTransactions();
}

// Update transaction in table (refresh list)
function updateTransactionInTable(transaction) {
  fetchTransactions();
}

// Remove transaction from table (refresh list)
function removeTransactionFromTable(transactionId) {
  fetchTransactions();
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
    const newTransaction = await response.json();
    addTransactionToTable(newTransaction);
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
    const updatedTransaction = await response.json();
    updateTransactionInTable(updatedTransaction);
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
    removeTransactionFromTable(transactionId);
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

// Handle login button
document.getElementById("loginButton").addEventListener("click", () => {
  fetchTransactions();
});

