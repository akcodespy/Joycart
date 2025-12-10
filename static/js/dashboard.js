
document.addEventListener('DOMContentLoaded', () => {

  const logoutEl = document.getElementById('logout');

  if (!logoutEl) {
   
    console.warn('dashboard.js: #logout element not found — skipping logout handler');
    return;
  }

  
  if (logoutEl.tagName === 'FORM') {
    logoutEl.addEventListener('submit', (e) => {
      
      e.preventDefault && e.preventDefault();
      localStorage.removeItem('username');
      localStorage.removeItem('access_token');
      
      window.location.href = '/';
    });
  } else {
    
    logoutEl.addEventListener('click', (e) => {
     
      if (e && typeof e.preventDefault === 'function') e.preventDefault();

      localStorage.removeItem('username');
      localStorage.removeItem('access_token');

     
      window.location.href = '/';
    });
  }
});
