// static/js/script.js

document.addEventListener("DOMContentLoaded", () => {
  // --- Profile Dropdown Toggle ---
  const profileBtn = document.querySelector(".profile-btn");
  const dropdownMenu = document.querySelector(".dropdown-menu");

  if (profileBtn && dropdownMenu) {
    profileBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      dropdownMenu.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".profile-container")) {
        dropdownMenu.classList.remove("show");
      }
    });
  }

  // --- Animate on scroll ---
  const animateOnScroll = () => {
    document.querySelectorAll(".animate-on-scroll").forEach((el) => {
      const boxTop = el.getBoundingClientRect().top;
      if (boxTop < window.innerHeight * 0.85) {
        el.classList.add("visible");
      }
    });
  };
  window.addEventListener("scroll", animateOnScroll);
  animateOnScroll(); // Run on load

  // --- Chart.js Initializations ---
  // Helper function to create a line chart
  const createLineChart = (id, data, color) => {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    new Chart(ctx.getContext("2d"), {
      type: "line",
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
        datasets: [
          {
            label: "Engagement",
            data: data,
            borderColor: color,
            backgroundColor: "rgba(0, 0, 0, 0.1)",
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: color,
            pointRadius: 3,
            pointHoverRadius: 5,
          },
        ],
      },
      options: chartOptions(),
    });
  };

  // Helper function to create a bar chart
  const createBarChart = (id, data, label, color) => {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    new Chart(ctx.getContext("2d"), {
      type: "bar",
      data: {
        labels: ["Q1", "Q2", "Q3", "Q4"],
        datasets: [
          {
            label: label,
            data: data,
            backgroundColor: color,
            borderColor: color,
            borderWidth: 1,
          },
        ],
      },
      options: chartOptions(),
    });
  };

  // Common chart options
  const chartOptions = () => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: "rgba(255, 255, 255, 0.1)" },
        ticks: { color: "rgba(255, 255, 255, 0.6)" },
      },
      x: {
        grid: { color: "rgba(255, 255, 255, 0.1)" },
        ticks: { color: "rgba(255, 255, 255, 0.6)" },
      },
    },
  });

  // Initialize all charts
  createLineChart(
    "akshatChart",
    [65, 59, 80, 81, 56, 55, 40],
    "rgba(0, 247, 255, 0.8)"
  );
  createLineChart(
    "bhaveshChart",
    [28, 48, 40, 19, 86, 27, 90],
    "rgba(0, 168, 255, 0.8)"
  );
  createLineChart(
    "chaitanyaChart",
    [75, 45, 60, 35, 70, 55, 65],
    "rgba(0, 230, 118, 0.8)"
  );
  createLineChart(
    "darshChart",
    [90, 60, 45, 70, 50, 80, 95],
    "rgba(255, 145, 0, 0.8)"
  );
  createBarChart(
    "conversionChart",
    [20, 25, 28, 32],
    "Conversion Rate %",
    "rgba(0, 247, 255, 0.6)"
  );
  createLineChart(
    "loyaltyChart",
    [30, 35, 38, 42, 45],
    "rgba(0, 168, 255, 0.6)"
  );

  // --- Leaderboard Tabs ---
  const tabs = document.querySelectorAll(".leaderboard-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      tabs.forEach((t) => t.classList.remove("active"));
      this.classList.add("active");
    });
  });
});
