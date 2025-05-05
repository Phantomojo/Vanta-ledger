const API_BASE_URL = "http://localhost:8500/api";

document.addEventListener("DOMContentLoaded", () => {
  const loginButton = document.getElementById("loginButton");
  const accessTokenInput = document.getElementById("accessTokenInput");
  const transactionsTableBody = document.getElementById("transactionsTableBody");
  const transactionForm = document.getElementById("transactionForm");
  const cancelButton = document.getElementById("cancelButton");

  let authToken = null;
  let editingTransactionId = null;

  // Login handler
  loginButton.addEventListener("click", async () => {
    const token = accessTokenInput.value.trim();
    if (!token) {
      alert("Please enter an access token");
      return;
    }
    try {
      const res = await fetch(API_BASE_URL + "/verify", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
          "Content-Type": "application/json",
        },
      });
      if (res.ok) {
        authToken = token;
        accessTokenInput.disabled = true;
        loginButton.disabled = true;
        loadTransactions();
      } else {
        alert("Invalid token");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("Server error or connection issue.");
    }
  });

  // Load transactions from backend
  async function loadTransactions() {
    if (!authToken) return;
    try {
      const res = await fetch(API_BASE_URL + "/transactions", {
        headers: { Authorization: "Bearer " + authToken },
      });
      if (res.ok) {
        const transactions = await res.json();
        renderTransactions(transactions);
      } else {
        alert("Failed to load transactions");
      }
    } catch (error) {
      console.error("Load transactions error:", error);
      alert("Server error or connection issue.");
    }
  }

  // Render transactions in table
  function renderTransactions(transactions) {
    transactionsTableBody.innerHTML = "";
    transactions.forEach((tx) => {
      const tr = document.createElement("tr");
      tr.classList.add("table-row");
      tr.innerHTML = `
        <td class="p-3">${tx.id}</td>
        <td class="p-3 capitalize">${tx.type}</td>
        <td class="p-3">$${tx.amount.toFixed(2)}</td>
        <td class="p-3">${tx.description}</td>
        <td class="p-3">${new Date(tx.date).toLocaleDateString()}</td>
        <td class="p-3 space-x-2">
          <button class="edit-btn text-blue-600 hover:underline" data-id="${tx.id}">Edit</button>
          <button class="delete-btn text-red-600 hover:underline" data-id="${tx.id}">Delete</button>
        </td>
      `;
      transactionsTableBody.appendChild(tr);
    });

    // Attach event listeners for edit and delete buttons
    document.querySelectorAll(".edit-btn").forEach((btn) =>
      btn.addEventListener("click", (e) => {
        const id = e.target.getAttribute("data-id");
        startEditTransaction(id);
      })
    );
    document.querySelectorAll(".delete-btn").forEach((btn) =>
      btn.addEventListener("click", (e) => {
        const id = e.target.getAttribute("data-id");
        deleteTransaction(id);
      })
    );
  }

  // Start editing a transaction
  async function startEditTransaction(id) {
    if (!authToken) return;
    try {
      const res = await fetch(`${API_BASE_URL}/transactions/${id}`, {
        headers: { Authorization: "Bearer " + authToken },
      });
      if (res.ok) {
        const tx = await res.json();
        editingTransactionId = tx.id;
        transactionForm.transactionId.value = tx.id;
        transactionForm.type.value = tx.type;
        transactionForm.amount.value = tx.amount;
        transactionForm.description.value = tx.description;
        transactionForm.date.value = tx.date.split("T")[0];
      } else {
        alert("Failed to load transaction");
      }
    } catch (error) {
      console.error("Edit transaction error:", error);
      alert("Server error or connection issue.");
    }
  }

  // Delete a transaction
  async function deleteTransaction(id) {
    if (!authToken) return;
    if (!confirm("Are you sure you want to delete this transaction?")) return;
    try {
      const res = await fetch(`${API_BASE_URL}/transactions/${id}`, {
        method: "DELETE",
        headers: { Authorization: "Bearer " + authToken },
      });
      if (res.ok) {
        loadTransactions();
      } else {
        alert("Failed to delete transaction");
      }
    } catch (error) {
      console.error("Delete transaction error:", error);
      alert("Server error or connection issue.");
    }
  }

  // Handle form submit for add/update
  transactionForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!authToken) {
      alert("Please login first");
      return;
    }
    const txData = {
      amount: parseFloat(transactionForm.amount.value),
      type: transactionForm.type.value,
      description: transactionForm.description.value,
      date: transactionForm.date.value,
    };
    try {
      let res;
      if (editingTransactionId) {
        res = await fetch(`${API_BASE_URL}/transactions/${editingTransactionId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + authToken,
          },
          body: JSON.stringify(txData),
        });
      } else {
        res = await fetch(`${API_BASE_URL}/transactions`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + authToken,
          },
          body: JSON.stringify(txData),
        });
      }
      if (res.ok) {
        resetForm();
        loadTransactions();
      } else {
        alert("Failed to save transaction");
      }
    } catch (error) {
      console.error("Save transaction error:", error);
      alert("Server error or connection issue.");
    }
  });

  // Reset form and editing state
  function resetForm() {
    editingTransactionId = null;
    transactionForm.reset();
  }

  // Cancel button handler
  cancelButton.addEventListener("click", () => {
    resetForm();
  });
});
