const API_BASE_URL = "http://localhost:8500/api";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  if (!form) {
    console.error("Login form not found");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = document.getElementById("tokenInput").value.trim();
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
        localStorage.setItem("token", token);
        window.location.href = "/dashboard.html";
      } else {
        alert("Invalid token");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("Server error or connection issue.");
    }
  });
});
