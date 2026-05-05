document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    //  SIDEBAR
    // =========================================================================
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const sidebarClose = document.getElementById('sidebarClose');

    function openSidebar() {
        sidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

    // =========================================================================
    //  SIDEBAR ACCORDION (Collections)
    // =========================================================================
    const collectionsToggle = document.getElementById('collectionsToggle');
    const collectionsContent = document.getElementById('collectionsContent');

    if (collectionsToggle && collectionsContent) {
        collectionsToggle.addEventListener('click', () => {
            collectionsToggle.classList.toggle('active');
            collectionsContent.classList.toggle('open');
        });
    }

    // =========================================================================
    //  SEARCH OVERLAY
    // =========================================================================
    const searchToggle = document.getElementById('searchToggle');
    const searchOverlay = document.getElementById('searchOverlay');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');

    function openSearch() {
        searchOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        setTimeout(() => { if (searchInput) searchInput.focus(); }, 300);
    }

    function closeSearch() {
        searchOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (searchToggle) searchToggle.addEventListener('click', openSearch);
    if (searchClose) searchClose.addEventListener('click', closeSearch);
    if (searchOverlay) {
        searchOverlay.addEventListener('click', (e) => {
            if (e.target === searchOverlay) closeSearch();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeSearch();
            closeCartSidebar();
            closeSidebar();
        }
    });

    // =========================================================================
    //  CART SIDEBAR
    // =========================================================================
    const cartSidebarToggle = document.getElementById('cartSidebarToggle');
    const cartSidebar = document.getElementById('cartSidebar');
    const cartSidebarOverlay = document.getElementById('cartSidebarOverlay');
    const cartSidebarClose = document.getElementById('cartSidebarClose');
    const sidebarCartOpen = document.getElementById('sidebarCartOpen');

    function openCartSidebar() {
        closeSidebar();
        cartSidebar.classList.add('active');
        cartSidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        fetchCartData();
    }

    function closeCartSidebar() {
        cartSidebar.classList.remove('active');
        cartSidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (cartSidebarToggle) cartSidebarToggle.addEventListener('click', openCartSidebar);
    if (cartSidebarClose) cartSidebarClose.addEventListener('click', closeCartSidebar);
    if (cartSidebarOverlay) cartSidebarOverlay.addEventListener('click', closeCartSidebar);
    if (sidebarCartOpen) sidebarCartOpen.addEventListener('click', openCartSidebar);

    function fetchCartData() {
        fetch('/shop/cart-sidebar-data/')
            .then(r => r.json())
            .then(data => {
                const itemsContainer = document.getElementById('cartSidebarItems');
                const emptyEl = document.getElementById('cartSidebarEmpty');
                const footerEl = document.getElementById('cartSidebarFooter');
                const countEl = document.getElementById('cartSidebarCount');
                const subtotalEl = document.getElementById('cartSubtotal');

                if (!itemsContainer) return;

                // Clear previous items (keep empty placeholder)
                itemsContainer.querySelectorAll('.cart-sb-item').forEach(el => el.remove());

                if (data.count === 0) {
                    if (emptyEl) emptyEl.style.display = 'flex';
                    if (footerEl) footerEl.style.display = 'none';
                } else {
                    if (emptyEl) emptyEl.style.display = 'none';
                    if (footerEl) footerEl.style.display = 'block';

                    data.items.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'cart-sb-item';
                        div.innerHTML = `
                            <img class="cart-sb-img" src="${item.image}" alt="${item.name}">
                            <div class="cart-sb-info">
                                <span class="cart-sb-name">${item.name}</span>
                                <span class="cart-sb-meta">Qty: ${item.quantity}</span>
                            </div>
                            <span class="cart-sb-price">&#2547; ${item.total.toFixed(2)}</span>
                        `;
                        itemsContainer.insertBefore(div, emptyEl);
                    });

                    if (countEl) countEl.textContent = data.count + ' item' + (data.count !== 1 ? 's' : '');
                    if (subtotalEl) subtotalEl.textContent = '৳ ' + data.subtotal.toFixed(2);
                }
            })
            .catch(() => {});
    }

    // =========================================================================
    //  USER DROPDOWN
    // =========================================================================
    const userToggle = document.getElementById('userToggle');
    const dropdownContent = document.getElementById('dropdownContent');

    if (userToggle && dropdownContent) {
        userToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownContent.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (!dropdownContent.contains(e.target) && e.target !== userToggle) {
                dropdownContent.classList.remove('show');
            }
        });
    }

    // =========================================================================
    //  ROTATING HERO SLIDER
    // =========================================================================
    const slides = document.querySelectorAll('.hero-slide');
    const prevBtn = document.getElementById('rotSliderPrev');
    const nextBtn = document.getElementById('rotSliderNext');
    let currentSlide = 0;
    let autoSlideTimer;

    function goToSlide(index) {
        if (slides.length === 0) return;
        
        // Remove active and add exit to current slide for animation
        slides[currentSlide].classList.remove('active');
        slides[currentSlide].classList.add('exit');
        
        const previousSlide = slides[currentSlide];
        setTimeout(() => {
            previousSlide.classList.remove('exit');
        }, 1400);

        currentSlide = (index + slides.length) % slides.length;
        slides[currentSlide].classList.add('active');
    }

    function startAutoSlide() {
        autoSlideTimer = setInterval(() => goToSlide(currentSlide + 1), 6000);
    }

    function resetAutoSlide() {
        clearInterval(autoSlideTimer);
        startAutoSlide();
    }

    if (slides.length > 0) {
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                goToSlide(currentSlide + 1);
                resetAutoSlide();
            });
        }
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                goToSlide(currentSlide - 1);
                resetAutoSlide();
            });
        }
        startAutoSlide();
    }

    // =========================================================================
    //  THEME TOGGLE (Dark / Light)
    // =========================================================================
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('aura-theme') || 'dark';

    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcons(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('aura-theme', next);
            updateThemeIcons(next);
        });
    }

    function updateThemeIcons(theme) {
        const lightIcons = document.querySelectorAll('.theme-icon-light');
        const darkIcons = document.querySelectorAll('.theme-icon-dark');
        if (theme === 'dark') {
            lightIcons.forEach(i => i.style.display = 'none');
            darkIcons.forEach(i => i.style.display = 'inline');
        } else {
            lightIcons.forEach(i => i.style.display = 'inline');
            darkIcons.forEach(i => i.style.display = 'none');
        }
        // Update button text
        if (themeToggle) {
            const span = themeToggle.querySelector('span');
            if (span) span.textContent = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
        }
    }

    // =========================================================================
    //  TOAST AUTO-DISMISS
    // =========================================================================
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach((toast, i) => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(40px)';
            setTimeout(() => toast.remove(), 400);
        }, 3500 + i * 500);
    });

    // =========================================================================
    //  SCROLL REVEAL (IntersectionObserver)
    // =========================================================================
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
});
