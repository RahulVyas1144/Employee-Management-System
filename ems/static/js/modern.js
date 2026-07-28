document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.querySelector('[data-sidebar-toggle]');
  const sidebar = document.querySelector('[data-sidebar]');

  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  const themeToggle = document.querySelector('[data-theme-toggle]');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('dark-theme');
      const mode = document.body.classList.contains('dark-theme') ? 'Dark' : 'Light';
      themeToggle.setAttribute('aria-label', `${mode} mode`);
    });
  }
});
