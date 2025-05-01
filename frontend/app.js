document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const tokenInput = document.getElementById('token-input');

  if (!form || !tokenInput) {
    console.error("Login form or token input not found");
    return;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const token = tokenInput.value.trim();

    if (!token) {
      alert("Please enter a token.");
      return;
    }

    try {
      const response = await fetch('/api/transactions', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        localStorage.setItem('token', token);
        window.location.href = '/dashboard.html'; // Adjust if your dashboard is elsewhere
      } else {
        alert("Invalid token.");
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("Server error or connection issue.");
    }
  });
});
