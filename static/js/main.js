// LeaveFlow Main JS

document.addEventListener('DOMContentLoaded', function () {

  // ── Theme Toggle ──
  const themeToggle = document.getElementById('themeToggle');
  const html = document.documentElement;

  const savedTheme = localStorage.getItem('theme') || 'light';
  html.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeIcon(next);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector('i');
    if (icon) {
      icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }

  // ── Sidebar Toggle ──
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  const sidebarToggle = document.getElementById('sidebarToggle');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle('open');
      } else {
        const collapsed = sidebar.classList.toggle('collapsed');
        if (collapsed) {
          sidebar.style.width = '64px';
          mainContent.style.marginLeft = '64px';
        } else {
          sidebar.style.width = '';
          mainContent.style.marginLeft = '';
        }
      }
    });
  }

  // ── Notification Dropdown ──
  const notifBtn = document.getElementById('notifBtn');
  const notifDropdown = document.getElementById('notifDropdown');

  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!notifDropdown.contains(e.target) && e.target !== notifBtn) {
        notifDropdown.classList.remove('show');
      }
    });
  }

  // ── Auto-dismiss alerts ──
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 300);
    });
  }, 5000);

  // ── Animate stat cards on load ──
  document.querySelectorAll('.stat-card, .card, .table-container').forEach((el, i) => {
    el.classList.add('fade-in');
    el.style.animationDelay = `${i * 0.05}s`;
  });

  // ── Progress bar animation ──
  document.querySelectorAll('.progress-bar[data-width]').forEach(bar => {
    setTimeout(() => {
      bar.style.width = bar.getAttribute('data-width') + '%';
    }, 300);
  });

  // ── Date range picker for leave apply ──
  const startDate = document.getElementById('id_start_date');
  const endDate = document.getElementById('id_end_date');
  const numDaysEl = document.getElementById('numDays');

  function calcDays() {
    if (startDate && endDate && startDate.value && endDate.value) {
      const start = new Date(startDate.value);
      const end = new Date(endDate.value);
      if (end >= start) {
        let count = 0;
        let cur = new Date(start);
        while (cur <= end) {
          const day = cur.getDay();
          if (day !== 0 && day !== 6) count++;
          cur.setDate(cur.getDate() + 1);
        }
        if (numDaysEl) numDaysEl.textContent = count + ' working day(s)';
      }
    }
  }

  if (startDate) startDate.addEventListener('change', calcDays);
  if (endDate) endDate.addEventListener('change', calcDays);

  // ── Confirm delete ──
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

});