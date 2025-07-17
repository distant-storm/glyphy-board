// PWA Installation and Service Worker Registration
let deferredPrompt;

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Handle PWA installation
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt = e;
  // Show install button
  showInstallPromotion();
});

function showInstallPromotion() {
  const installButton = document.getElementById('install-button');
  if (installButton) {
    installButton.style.display = 'block';
    installButton.addEventListener('click', installApp);
  }
}

function installApp() {
  const installButton = document.getElementById('install-button');
  if (installButton) {
    installButton.style.display = 'none';
  }
  
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      deferredPrompt = null;
    });
  }
}

// Handle app installation
window.addEventListener('appinstalled', (evt) => {
  console.log('Glyphy Board was installed');
});

// Show splash screen
function showSplashScreen() {
  const splash = document.getElementById('splash-screen');
  if (splash) {
    splash.style.display = 'flex';
    setTimeout(() => {
      splash.style.opacity = '0';
      setTimeout(() => {
        splash.style.display = 'none';
      }, 500);
    }, 2000);
  }
}

// Initialize splash screen on page load
document.addEventListener('DOMContentLoaded', () => {
  // Show splash screen only on first load or if app is launched from home screen
  if (window.matchMedia('(display-mode: standalone)').matches || 
      document.referrer === '' || 
      !sessionStorage.getItem('splashShown')) {
    showSplashScreen();
    sessionStorage.setItem('splashShown', 'true');
  }
});

// Handle network status
window.addEventListener('online', () => {
  document.body.classList.remove('offline');
  showToast('Back online', 'success');
});

window.addEventListener('offline', () => {
  document.body.classList.add('offline');
  showToast('You are offline', 'warning');
});

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('show');
  }, 100);
  
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 3000);
} 