// Modern JavaScript untuk SPK Diagnosis Penyakit Cabai

document.addEventListener("DOMContentLoaded", function () {
  console.log("SPK Diagnosis Penyakit Cabai - Sistem telah dimuat");

  // Initialize all components
  initGejalaCounter();
  initCheckboxEffects();
  initTooltips();
  initAnimations();
  initTableSorting();
  initParallaxEffects();
  initMathJax();
  initPrintButton();
  initSmoothScroll();
  initTeamCards();

  // Show welcome notification
  showWelcomeNotification();
});

// 1. Initialize gejala counter
function initGejalaCounter() {
  const checkboxes = document.querySelectorAll(".gejala-checkbox");
  const counter = document.getElementById("count-gejala");
  const submitBtn = document.getElementById("btn-diagnosa");

  if (checkboxes.length > 0) {
    updateGejalaCount();

    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", function () {
        updateGejalaCount();
        animateCheckbox(this);
      });
    });
  }

  function updateGejalaCount() {
    const checked = document.querySelectorAll(
      ".gejala-checkbox:checked",
    ).length;
    if (counter) {
      counter.textContent = checked;
      counter.classList.toggle("bg-success", checked > 0);
      counter.classList.toggle("bg-secondary", checked === 0);

      // Add pulse animation when symptoms are selected
      if (checked > 0) {
        counter.classList.add("animate-pulse");
      } else {
        counter.classList.remove("animate-pulse");
      }
    }

    if (submitBtn) {
      submitBtn.disabled = checked === 0;
      submitBtn.classList.toggle("btn-success", checked > 0);
      submitBtn.classList.toggle("btn-secondary", checked === 0);
    }
  }
}

// 2. Animate checkbox selection
function animateCheckbox(checkbox) {
  const label = checkbox.closest(".form-check");
  if (checkbox.checked) {
    label.style.transform = "scale(1.05)";
    setTimeout(() => {
      label.style.transform = "scale(1)";
    }, 200);
  }
}

// 3. Initialize tooltips
function initTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl, {
      trigger: "hover",
    });
  });
}

// 4. Initialize animations
function initAnimations() {
  // Add animation classes to cards
  const cards = document.querySelectorAll(".card");
  cards.forEach((card, index) => {
    card.classList.add("animate-fade-in-up");
    card.style.animationDelay = `${index * 0.1}s`;
  });

  // Add hover effects to team cards
  const teamCards = document.querySelectorAll(".team-card");
  teamCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-15px) scale(1.02)";
    });

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0) scale(1)";
    });
  });
}

// 5. Initialize table sorting
function initTableSorting() {
  const tableHeaders = document.querySelectorAll("th[data-sortable]");
  tableHeaders.forEach((header) => {
    header.style.cursor = "pointer";
    header.addEventListener("click", function () {
      const table = this.closest("table");
      const columnIndex = Array.from(this.parentNode.children).indexOf(this);
      sortTable(table, columnIndex);
    });
  });
}

function sortTable(table, columnIndex) {
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const isAscending = !table.classList.contains("sorted-asc");

  rows.sort((a, b) => {
    const aValue = a.children[columnIndex].textContent.trim();
    const bValue = b.children[columnIndex].textContent.trim();

    if (isAscending) {
      return aValue.localeCompare(bValue, undefined, { numeric: true });
    } else {
      return bValue.localeCompare(aValue, undefined, { numeric: true });
    }
  });

  // Remove existing rows
  while (tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
  }

  // Add sorted rows
  rows.forEach((row) => tbody.appendChild(row));

  // Update sort indicator
  table.classList.toggle("sorted-asc", isAscending);
  table.classList.toggle("sorted-desc", !isAscending);
}

// 6. Initialize parallax effects
function initParallaxEffects() {
  window.addEventListener("scroll", function () {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll(".parallax");

    parallaxElements.forEach((element) => {
      const speed = element.dataset.speed || 0.5;
      element.style.transform = `translateY(${scrolled * speed}px)`;
    });
  });
}

// 7. Initialize MathJax
function initMathJax() {
  if (typeof MathJax !== "undefined") {
    MathJax.Hub.Config({
      tex2jax: {
        inlineMath: [
          ["$", "$"],
          ["\\(", "\\)"],
        ],
        displayMath: [
          ["$$", "$$"],
          ["\\[", "\\]"],
        ],
        processEscapes: true,
        processEnvironments: true,
      },
      "HTML-CSS": {
        linebreaks: { automatic: true },
        scale: 100,
      },
    });

    MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
  }
}

// 8. Initialize print button
function initPrintButton() {
  const printButtons = document.querySelectorAll('[data-action="print"]');
  printButtons.forEach((button) => {
    button.addEventListener("click", function () {
      window.print();
    });
  });
}

// 9. Initialize smooth scroll
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();

      const targetId = this.getAttribute("href");
      if (targetId === "#") return;

      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 80,
          behavior: "smooth",
        });
      }
    });
  });
}

// 10. Initialize team cards with placeholder images
function initTeamCards() {
  const teamCards = document.querySelectorAll(".team-card");

  // Placeholder images based on gender/role (using placeholder service)
  const placeholderImages = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1494790108755-2616b612b786?w-400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1544725176-7c40e5a71c5e?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop",
  ];

  teamCards.forEach((card, index) => {
    const img = card.querySelector(".team-img");
    if (img && !img.src) {
      // Use modulo to cycle through placeholder images
      img.src = placeholderImages[index % placeholderImages.length];
      img.alt = "Foto Anggota Tim";

      // Add loading lazy
      img.loading = "lazy";
    }

    // Add click effect
    card.addEventListener("click", function () {
      this.style.transform = "scale(0.95)";
      setTimeout(() => {
        this.style.transform = "";
      }, 200);
    });
  });
}

// 11. Show welcome notification
function showWelcomeNotification() {
  if (!sessionStorage.getItem("welcomeShown")) {
    setTimeout(() => {
      createNotification(
        "Selamat datang di SPK Diagnosis Penyakit Cabai! 🌶️",
        "success",
      );
      sessionStorage.setItem("welcomeShown", "true");
    }, 1000);
  }
}

// 12. Create custom notification
function createNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `alert alert-${type} notification-alert`;
  notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-${type === "success" ? "check-circle" : type === "warning" ? "exclamation-triangle" : "info-circle"} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;

  // Add styles
  notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-radius: 10px;
        animation: slideInRight 0.3s ease-out;
    `;

  document.body.appendChild(notification);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.style.animation = "slideOutRight 0.3s ease-out";
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }
  }, 5000);
}

// 13. Confirm delete with sweet alert style
function confirmDelete(itemId, itemName, type) {
  const modal = document.createElement("div");
  modal.className = "modal fade show d-block";
  modal.style.backgroundColor = "rgba(0,0,0,0.5)";
  modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title text-danger">
                        <i class="bi bi-exclamation-triangle-fill"></i> Konfirmasi Hapus
                    </h5>
                </div>
                <div class="modal-body">
                    <p>Apakah Anda yakin ingin menghapus ${type} <strong>"${itemName}"</strong>?</p>
                    <p class="text-muted small">Tindakan ini tidak dapat dibatalkan.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal(this)">Batal</button>
                    <button type="button" class="btn btn-danger" onclick="performDelete('${itemId}', '${type}')">Ya, Hapus</button>
                </div>
            </div>
        </div>
    `;

  document.body.appendChild(modal);
  document.body.style.overflow = "hidden";
}

function closeModal(btn) {
  const modal = btn.closest(".modal");
  document.body.removeChild(modal);
  document.body.style.overflow = "";
}

function performDelete(itemId, type) {
  // In real implementation, this would be an AJAX call
  console.log(`Deleting ${type} with ID: ${itemId}`);

  // Simulate API call
  setTimeout(() => {
    createNotification(
      `${type.charAt(0).toUpperCase() + type.slice(1)} berhasil dihapus`,
      "success",
    );
    closeModal(document.querySelector(".modal .btn-danger"));

    // Reload or remove element from DOM
    const element = document.querySelector(`[data-id="${itemId}"]`);
    if (element) {
      element.style.opacity = "0";
      element.style.transform = "translateX(100px)";
      setTimeout(() => {
        element.remove();
      }, 300);
    }
  }, 1000);
}

// 14. Export data function
function exportData(format, type) {
  createNotification(
    `Mengekspor data ${type} dalam format ${format.toUpperCase()}...`,
    "info",
  );

  // Simulate export process
  setTimeout(() => {
    createNotification(`Data ${type} berhasil diekspor!`, "success");

    // Create and trigger download (simulated)
    const link = document.createElement("a");
    link.download = `data_${type}_${new Date().toISOString().split("T")[0]}.${format}`;
    link.href = "#";
    link.click();
  }, 2000);
}

// 15. Search and filter function
function filterTable(tableId, searchId) {
  const input = document.getElementById(searchId);
  const filter = input.value.toLowerCase();
  const table = document.getElementById(tableId);
  const rows = table.querySelectorAll("tbody tr");

  rows.forEach((row) => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(filter) ? "" : "none";
  });
}

// Add CSS for animations
const style = document.createElement("style");
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .notification-alert {
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-radius: 10px;
        animation: slideInRight 0.3s ease-out;
    }
    
    .sorted-asc::after {
        content: ' ↑';
    }
    
    .sorted-desc::after {
        content: ' ↓';
    }
    
    .parallax {
        will-change: transform;
    }
`;
document.head.appendChild(style);
