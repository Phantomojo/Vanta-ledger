// Base URL for backend API
const API_BASE_URL = "http://localhost:8500/api";

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

// Add event listeners and initialize UI
document.getElementById("loginButton").addEventListener("click", () => {
  fetchTransactions();
});

// Other UI functions like renderTransactions, addTransactionToTable, updateTransactionInTable, removeTransactionFromTable should be defined here or imported

