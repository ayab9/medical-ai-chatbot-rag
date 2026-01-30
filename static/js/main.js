// =========================
// ANIMATIONS PAGE D'ACCUEIL
// =========================

// Animation des compteurs statistiques
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    const animateCounter = (counter) => {
        const target = parseInt(counter.dataset.target);
        const duration = 2000; // 2 secondes
        const increment = target / (duration / 16); // 60 FPS
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            
            if (current < target) {
                if (counter.dataset.target.includes('%')) {
                    counter.textContent = Math.floor(current) + '%';
                } else if (target >= 1000000) {
                    counter.textContent = (current / 1000000).toFixed(1) + 'M';
                } else if (target >= 1000) {
                    counter.textContent = (current / 1000).toFixed(0) + 'K';
                } else {
                    counter.textContent = Math.floor(current);
                }
                requestAnimationFrame(updateCounter);
            } else {
                if (counter.dataset.target.includes('%')) {
                    counter.textContent = target + '%';
                } else if (target >= 1000000) {
                    counter.textContent = (target / 1000000).toFixed(1) + 'M';
                } else if (target >= 1000) {
                    counter.textContent = (target / 1000).toFixed(0) + 'K';
                } else {
                    counter.textContent = target;
                }
            }
        };
        
        updateCounter();
    };
    
    // Intersection Observer pour déclencher l'animation au scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

// =========================
// GRAPHIQUE SURVIVAL RATES
// =========================

function createSurvivalChart() {
    const canvas = document.getElementById('survivalChart');
    
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Stage 0', 'Stage I', 'Stage II', 'Stage III', 'Stage IV'],
            datasets: [{
                label: '5-Year Survival Rate (%)',
                data: [99, 93, 85, 60, 22],
                backgroundColor: [
                    'rgba(255, 105, 180, 0.8)',
                    'rgba(255, 182, 193, 0.8)',
                    'rgba(255, 192, 203, 0.8)',
                    'rgba(255, 228, 225, 0.8)',
                    'rgba(199, 21, 133, 0.8)'
                ],
                borderColor: [
                    'rgba(255, 105, 180, 1)',
                    'rgba(255, 182, 193, 1)',
                    'rgba(255, 192, 203, 1)',
                    'rgba(255, 228, 225, 1)',
                    'rgba(199, 21, 133, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Early Detection Dramatically Improves Survival',
                    font: {
                        size: 16,
                        family: 'Poppins'
                    },
                    color: '#c71585'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// =========================
// SMOOTH SCROLL
// =========================

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// =========================
// PARALLAX EFFECT (Hero)
// =========================

function initParallax() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroContent = document.querySelector('.hero-content');
        if (heroContent) {
            heroContent.style.transform = `translateY(${scrolled * 0.5}px)`;
            heroContent.style.opacity = 1 - (scrolled / 600);
        }
    });
}

// =========================
// TEXTAREA AUTO-RESIZE
// =========================

function initTextareaAutoResize() {
    const textarea = document.getElementById('userInput');
    if (!textarea) return;
    
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

// =========================
// LOAD API STATS
// =========================

async function loadGlobalStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.global_stats) {
            // Mettre à jour les compteurs si nécessaire
            console.log('Global stats loaded:', data.global_stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// =========================
// EASTER EGG: RIBBON CLICK
// =========================

function initEasterEgg() {
    const ribbon = document.querySelector('.ribbon-icon');
    if (!ribbon) return;
    
    let clicks = 0;
    ribbon.addEventListener('click', () => {
        clicks++;
        if (clicks === 5) {
            ribbon.style.animation = 'spin 0.5s ease';
            setTimeout(() => {
                ribbon.style.animation = 'pulse 2s infinite';
            }, 500);
            
            // Afficher message d'encouragement
            const message = document.createElement('div');
            message.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: linear-gradient(135deg, #ff69b4, #c71585);
                color: white;
                padding: 30px 50px;
                border-radius: 20px;
                font-size: 1.5rem;
                z-index: 10000;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                animation: fadeIn 0.5s ease;
            `;
            message.innerHTML = '💖<br>You are strong!<br>You are brave!<br>You are not alone!<br>💖';
            document.body.appendChild(message);
            
            setTimeout(() => {
                message.style.animation = 'fadeOut 0.5s ease';
                setTimeout(() => message.remove(), 500);
            }, 3000);
            
            clicks = 0;
        }
    });
}

// =========================
// COPY TO CLIPBOARD (pour citations)
// =========================

function initCopyButtons() {
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('copy-btn')) {
            const text = e.target.dataset.text;
            navigator.clipboard.writeText(text).then(() => {
                e.target.textContent = '✓ Copied!';
                setTimeout(() => {
                    e.target.textContent = '📋 Copy';
                }, 2000);
            });
        }
    });
}

// =========================
// NOTIFICATION SYSTEM
// =========================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#ff69b4'};
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// =========================
// KEYBOARD SHORTCUTS
// =========================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K pour focus sur l'input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const input = document.getElementById('userInput');
            if (input) {
                input.focus();
            }
        }
    });
}

// =========================
// INIT ALL
// =========================

document.addEventListener('DOMContentLoaded', () => {
    // Page d'accueil
    animateCounters();
    createSurvivalChart();
    initSmoothScroll();
    initParallax();
    loadGlobalStats();
    initEasterEgg();
    
    // Chatbot page
    initTextareaAutoResize();
    initCopyButtons();
    initKeyboardShortcuts();
    
    console.log('💖 Breast Cancer AI Assistant - Ready to help');
});

// =========================
// EXPORTS (si utilisé comme module)
// =========================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        animateCounters,
        createSurvivalChart,
        showNotification
    };
}