
const fastToken = localStorage.getItem("access_token");
console.log('register.js loaded — path:', window.location.pathname, 'token?', !!fastToken);

if (fastToken && window.location.pathname !== '/dashboard') {

  window.location.href = '/dashboard';

}


document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const msg = document.getElementById('msg');

  if (!form) {
    console.warn('register.js: register-form not found — maybe you opened a static copy or wrong page');
    return;
  }

  function setMsg(type, text) {
    if (!msg) return;
    msg.className = '';
    msg.textContent = text;
    if (type === 'error') msg.classList.add('error');
    else if (type === 'success') msg.classList.add('success');
    else msg.classList.add('status');
    msg.style.display = 'block';
  }

  function clearMsg() {
    if (!msg) return;
    msg.style.display = 'none';
    msg.className = '';
    msg.textContent = '';
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMsg();
    setMsg('status', 'Registering...');

    const payload = {
      username: form.username.value.trim(),
      email: form.email.value.trim(),
      password: form.password.value
    };

    try {
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      let body = null;
      try { body = await res.json(); } catch (err) { /* ignore parse errors */ }

      if (res.ok) {
        setMsg('success', 'Registration successful! Redirecting…');
        setTimeout(() => { location.href = '/'; }, 700);
        return;
      }

      setMsg('error', body?.detail || 'Registration failed. Please try again.');
    } catch (err) {
      console.error(err);
      setMsg('error', 'Network error. Try again.');
    }
  });
});
