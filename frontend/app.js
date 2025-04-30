document.addEventListener('DOMContentLoaded', () => {
  const API_BASE_URL = '/api'; // Adjust if backend is served differently
  const API_KEY_NAME = 'access_token';
  const API_KEY = 'supersecretadmintoken'; // Should match backend token

  // Elements
  const loginSection = document.getElementById('login-section');
  const appSection = document.getElementById('app-section');
  const apiKeyInput = document.getElementById('api-key-input');
  const loginBtn = document.getElementById('login-btn');
  const loginError = document.getElementById('login-error');

  const totalSalesEl = document.getElementById('total-sales');
  const totalExpendituresEl = document.getElementById('total-expenditures');
  const netTotalEl = document.getElementById('net-total');

  const transactionForm = document.getElementById('transaction-form');
  const transactionIdInput = document.getElementById('transaction-id');
  const amountInput = document.getElementById('amount');
  const typeInput = document.getElementById('type');
  const descriptionInput = document.getElementById('description');
  const dateInput = document.getElementById('date');
  const cancelBtn = document.getElementById('cancel-btn');

  const filterType = document.getElementById('filter-type');
  const filterStartDate = document.getElementById('filter-start-date');
  const filterEndDate = document.getElementById('filter-end-date');
  const filterBtn = document.getElementById('filter-btn');
  const clearFilterBtn = document.getElementById('clear-filter-btn');
  const exportCsvBtn = document.getElementById('export-csv-btn');
  const transactionTableBody = document.getElementById('transaction-table-body');

  let transactions = [];

  // Login handler
  loginBtn.addEventListener('click', () => {
    const enteredKey = apiKeyInput.value.trim();
    if (enteredKey === API_KEY) {
      loginError.classList.add('hidden');
      loginSection.classList.add('hidden');
      appSection.classList.remove('hidden');
      loadTransactions();
    } else {
      loginError.classList.remove('hidden');
    }
  });

  // Fetch transactions from API
  async function loadTransactions() {
    try {
      const res = await fetch(\`\${API_BASE_URL}/transactions?skip=0&limit=100\`, {
        headers: {
          [API_KEY_NAME]: API_KEY
        }
      });
      if (!res.ok) throw new Error('Failed to fetch transactions');
      transactions = await res.json();
      renderDashboard();
      renderTransactionTable();
    } catch (err) {
      alert('Error loading transactions: ' + err.message);
    }
  }

  // Render dashboard totals
  function renderDashboard() {
    const totalSales = transactions
      .filter(t => t.type === 'sale')
      .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const totalExpenditures = transactions
      .filter(t => t.type === 'expenditure')
      .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const netTotal = totalSales - totalExpenditures;

    totalSalesEl.textContent = formatCurrency(totalSales);
    totalExpendituresEl.textContent = formatCurrency(totalExpenditures);
    netTotalEl.textContent = formatCurrency(netTotal);
  }

  // Format number as currency string
  function formatCurrency(amount) {
    return '$' + amount.toFixed(2);
  }

  // Render transaction table with optional filters
  function renderTransactionTable() {
    const filtered = applyFilters(transactions);
    transactionTableBody.innerHTML = '';
    if (filtered.length === 0) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 5;
      td.className = 'text-center p-4 text-gray-500';
      td.textContent = 'No transactions found.';
      tr.appendChild(td);
      transactionTableBody.appendChild(tr);
      return;
    }
    filtered.forEach(t => {
      const tr = document.createElement('tr');
      tr.className = 'border-b';

      const dateTd = document.createElement('td');
      dateTd.className = 'py-2 px-4';
      dateTd.textContent = t.date;
      tr.appendChild(dateTd);

      const typeTd = document.createElement('td');
      typeTd.className = 'py-2 px-4 capitalize';
      typeTd.textContent = t.type;
      tr.appendChild(typeTd);

      const descTd = document.createElement('td');
      descTd.className = 'py-2 px-4';
      descTd.textContent = t.description;
      tr.appendChild(descTd);

      const amountTd = document.createElement('td');
      amountTd.className = 'py-2 px-4 text-right';
      amountTd.textContent = formatCurrency(parseFloat(t.amount));
      tr.appendChild(amountTd);

      const actionsTd = document.createElement('td');
      actionsTd.className = 'py-2 px-4 text-center space-x-2';

      // Edit button
      const editBtn = document.createElement('button');
      editBtn.className = 'text-indigo-600 hover:text-indigo-900';
      editBtn.title = 'Edit';
      editBtn.innerHTML = '<i class="fas fa-edit"></i>';
      editBtn.addEventListener('click', () => {
        populateFormForEdit(t.id);
      });
      actionsTd.appendChild(editBtn);

      // Delete button
      const deleteBtn = document.createElement('button');
      deleteBtn.className = 'text-red-600 hover:text-red-900';
      deleteBtn.title = 'Delete';
      deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
      deleteBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to delete this transaction?')) {
          deleteTransaction(t.id);
        }
      });
      actionsTd.appendChild(deleteBtn);

      tr.appendChild(actionsTd);

      transactionTableBody.appendChild(tr);
    });
  }

  // Apply filters to transactions
  function applyFilters(transactionsList) {
    let filtered = [...transactionsList];
    const typeVal = filterType.value;
    const startDateVal = filterStartDate.value;
    const endDateVal = filterEndDate.value;

    if (typeVal !== 'all') {
      filtered = filtered.filter(t => t.type === typeVal);
    }
    if (startDateVal) {
      filtered = filtered.filter(t => t.date >= startDateVal);
    }
    if (endDateVal) {
      filtered = filtered.filter(t => t.date <= endDateVal);
    }
    return filtered.sort((a, b) => b.date.localeCompare(a.date));
  }

  // Populate form for editing a transaction
  function populateFormForEdit(id) {
    const t = transactions.find(tr => tr.id === id);
    if (!t) return;
    transactionIdInput.value = t.id;
    amountInput.value = t.amount;
    typeInput.value = t.type;
    descriptionInput.value = t.description;
    dateInput.value = t.date;
    scrollToForm();
  }

  // Scroll to form section
  function scrollToForm() {
    transactionForm.scrollIntoView({ behavior: 'smooth' });
  }

  // Delete transaction by id
  async function deleteTransaction(id) {
    try {
      const res = await fetch(\`\${API_BASE_URL}/transactions/\${id}\`, {
        method: 'DELETE',
        headers: {
          [API_KEY_NAME]: API_KEY
        }
      });
      if (!res.ok) throw new Error('Failed to delete transaction');
      transactions = transactions.filter(t => t.id !== id);
      renderDashboard();
      renderTransactionTable();
    } catch (err) {
      alert('Error deleting transaction: ' + err.message);
    }
  }

  // Clear form inputs
  function clearForm() {
    transactionIdInput.value = '';
    amountInput.value = '';
    typeInput.value = 'sale';
    descriptionInput.value = '';
    dateInput.value = '';
  }

  // Handle form submit for add/edit
  transactionForm.addEventListener('submit', async e => {
    e.preventDefault();
    const id = transactionIdInput.value;
    const amount = parseFloat(amountInput.value);
    const type = typeInput.value;
    const description = descriptionInput.value.trim();
    const date = dateInput.value;

    if (!amount || amount <= 0) {
      alert('Please enter a valid amount greater than zero.');
      return;
    }
    if (!description) {
      alert('Please enter a description.');
      return;
    }
    if (!date) {
      alert('Please select a date.');
      return;
    }

    try {
      if (id) {
        // Edit existing
        const res = await fetch(\`\${API_BASE_URL}/transactions/\${id}\`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            [API_KEY_NAME]: API_KEY
          },
          body: JSON.stringify({ amount, type, description, date })
        });
        if (!res.ok) throw new Error('Failed to update transaction');
        const updated = await res.json();
        const index = transactions.findIndex(t => t.id === updated.id);
        if (index !== -1) transactions[index] = updated;
      } else {
        // Add new
        const res = await fetch(\`\${API_BASE_URL}/transactions\`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            [API_KEY_NAME]: API_KEY
          },
          body: JSON.stringify({ amount, type, description, date })
        });
        if (!res.ok) throw new Error('Failed to add transaction');
        const added = await res.json();
        transactions.push(added);
      }
      renderDashboard();
      renderTransactionTable();
      clearForm();
    } catch (err) {
      alert('Error saving transaction: ' + err.message);
    }
  });

  // Cancel button clears form
  cancelBtn.addEventListener('click', () => {
    clearForm();
  });

  // Filter button
  filterBtn.addEventListener('click', () => {
    renderTransactionTable();
  });

  // Clear filter button
  clearFilterBtn.addEventListener('click', () => {
    filterType.value = 'all';
    filterStartDate.value = '';
    filterEndDate.value = '';
    renderTransactionTable();
  });

  // Export CSV button
  exportCsvBtn.addEventListener('click', () => {
    exportTransactionsToCSV();
  });

  // Export transactions to CSV
  function exportTransactionsToCSV() {
    if (!transactions.length) {
      alert('No transactions to export.');
      return;
    }
    const filtered = applyFilters(transactions);
    if (!filtered.length) {
      alert('No transactions match the current filters.');
      return;
    }
    const headers = ['Date', 'Type', 'Description', 'Amount'];
    const rows = filtered.map(t => [t.date, t.type, t.description, t.amount.toFixed(2)]);
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += headers.join(',') + '\\n';
    rows.forEach(row => {
      csvContent += row.map(field => '"' + field.replace(/"/g, '""') + '"').join(',') + '\\n';
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    const filename = 'vantaledger_transactions_' + new Date().toISOString().slice(0,10) + '.csv';
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
});
