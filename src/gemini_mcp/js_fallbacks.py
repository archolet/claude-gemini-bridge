"""Modular JavaScript fallback library for frontend components.

GAP 8: JS Fallback Expansion
- Intersection Observer for scroll animations
- Dropdown positioning with collision detection
- Modal focus trap
- Carousel/slider functionality
- Toast notifications
- Accordion behavior
- Tabs navigation

Usage:
    from gemini_mcp.js_fallbacks import inject_js_fallbacks, get_js_for_component

    # Get all JS for a component type
    js = get_js_for_component("modal")

    # Inject needed JS into HTML
    html_with_js = inject_js_fallbacks(html, detect_needed=True)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import re


@dataclass
class JSModule:
    """A JavaScript module with metadata."""
    name: str
    code: str
    dependencies: List[str]
    description: str
    auto_detect_patterns: List[str]  # Patterns that indicate this module is needed


# =============================================================================
# CORE UTILITY MODULES
# =============================================================================

JS_UTILS = JSModule(
    name="utils",
    code="""
// Utility Functions
const utils = {
    debounce(fn, delay = 150) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), delay);
        };
    },
    throttle(fn, limit = 100) {
        let inThrottle;
        return (...args) => {
            if (!inThrottle) {
                fn.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    qs: (sel, ctx = document) => ctx.querySelector(sel),
    qsa: (sel, ctx = document) => [...ctx.querySelectorAll(sel)],
    on: (el, evt, fn, opts) => el?.addEventListener(evt, fn, opts),
    off: (el, evt, fn, opts) => el?.removeEventListener(evt, fn, opts),
    addClass: (el, ...cls) => el?.classList.add(...cls),
    removeClass: (el, ...cls) => el?.classList.remove(...cls),
    toggleClass: (el, cls, force) => el?.classList.toggle(cls, force),
    hasClass: (el, cls) => el?.classList.contains(cls),
    attr: (el, name, val) => val !== undefined ? el?.setAttribute(name, val) : el?.getAttribute(name),
    emit: (el, name, detail = {}) => el?.dispatchEvent(new CustomEvent(name, { detail, bubbles: true })),
    // Safe DOM creation
    createElement: (tag, attrs = {}, children = []) => {
        const el = document.createElement(tag);
        Object.entries(attrs).forEach(([k, v]) => {
            if (k === 'className') el.className = v;
            else if (k === 'textContent') el.textContent = v;
            else el.setAttribute(k, v);
        });
        children.forEach(child => {
            if (typeof child === 'string') {
                el.appendChild(document.createTextNode(child));
            } else if (child) {
                el.appendChild(child);
            }
        });
        return el;
    },
    // Create SVG element safely
    createSvg: (paths, className = 'w-5 h-5') => {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', className);
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('viewBox', '0 0 24 24');
        paths.forEach(d => {
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('stroke-linecap', 'round');
            path.setAttribute('stroke-linejoin', 'round');
            path.setAttribute('stroke-width', '2');
            path.setAttribute('d', d);
            svg.appendChild(path);
        });
        return svg;
    }
};
""",
    dependencies=[],
    description="Core utility functions used by other modules",
    auto_detect_patterns=[],  # Always included if any module is used
)


# =============================================================================
# INTERSECTION OBSERVER - Scroll Animations
# =============================================================================

JS_INTERSECTION_OBSERVER = JSModule(
    name="intersection_observer",
    code="""
// Intersection Observer for Scroll Animations
const ScrollAnimator = {
    init(options = {}) {
        const defaults = {
            selector: '[data-animate]',
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px',
            once: true,
        };
        const config = { ...defaults, ...options };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const animation = el.dataset.animate || 'fadeIn';
                    const delay = el.dataset.delay || '0';

                    el.style.transitionDelay = delay + 'ms';
                    el.classList.add('animate-' + animation, 'animated');
                    el.classList.remove('animate-hidden');

                    if (config.once) observer.unobserve(el);
                }
            });
        }, {
            threshold: config.threshold,
            rootMargin: config.rootMargin,
        });

        utils.qsa(config.selector).forEach(el => {
            el.classList.add('animate-hidden');
            observer.observe(el);
        });

        return observer;
    },

    // Stagger animation for lists
    stagger(selector, delayStep = 100) {
        utils.qsa(selector).forEach((el, i) => {
            el.dataset.delay = String(i * delayStep);
        });
    }
};

// CSS for animations (inject once)
(function() {
    if (document.getElementById('scroll-animation-styles')) return;
    const style = utils.createElement('style', { id: 'scroll-animation-styles' });
    style.textContent = [
        '.animate-hidden { opacity: 0; transform: translateY(20px); }',
        '.animated { transition: opacity 0.6s ease-out, transform 0.6s ease-out; }',
        '.animate-fadeIn { opacity: 1; transform: translateY(0); }',
        '.animate-fadeInUp { opacity: 1; transform: translateY(0); }',
        '.animate-fadeInDown { opacity: 1; transform: translateY(0); }',
        '.animate-fadeInLeft { opacity: 1; transform: translateX(0); }',
        '.animate-fadeInRight { opacity: 1; transform: translateX(0); }',
        '.animate-scaleIn { opacity: 1; transform: scale(1); }',
        '.animate-hidden.animate-fadeInLeft { transform: translateX(-20px); }',
        '.animate-hidden.animate-fadeInRight { transform: translateX(20px); }',
        '.animate-hidden.animate-scaleIn { transform: scale(0.9); }'
    ].join('\\n');
    document.head.appendChild(style);
})();

// Auto-init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => ScrollAnimator.init());
""",
    dependencies=["utils"],
    description="Scroll-triggered animations using Intersection Observer",
    auto_detect_patterns=[
        r'data-animate',
        r'animate-on-scroll',
        r'scroll-animation',
    ],
)


# =============================================================================
# DROPDOWN - With Collision Detection
# =============================================================================

JS_DROPDOWN = JSModule(
    name="dropdown",
    code="""
// Dropdown with Smart Positioning
const Dropdown = {
    activeDropdowns: new Set(),

    init(selector = '[data-dropdown]') {
        utils.qsa(selector).forEach(dropdown => {
            const trigger = utils.qs('[data-dropdown-trigger]', dropdown) || dropdown.firstElementChild;
            const panel = utils.qs('[data-dropdown-panel]', dropdown) || dropdown.lastElementChild;

            if (!trigger || !panel) return;

            // Click handler
            utils.on(trigger, 'click', (e) => {
                e.stopPropagation();
                this.toggle(dropdown, panel);
            });

            // Keyboard handler
            utils.on(trigger, 'keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggle(dropdown, panel);
                }
                if (e.key === 'Escape') {
                    this.close(dropdown, panel);
                }
            });
        });

        // Close on outside click
        utils.on(document, 'click', () => this.closeAll());
        utils.on(document, 'keydown', (e) => {
            if (e.key === 'Escape') this.closeAll();
        });
    },

    toggle(dropdown, panel) {
        const isOpen = utils.hasClass(panel, 'dropdown-open');

        if (isOpen) {
            this.close(dropdown, panel);
        } else {
            this.closeAll();
            this.open(dropdown, panel);
        }
    },

    open(dropdown, panel) {
        // Position panel
        this.position(dropdown, panel);

        // Show panel
        utils.addClass(panel, 'dropdown-open');
        utils.attr(panel, 'aria-hidden', 'false');

        // Track open dropdown
        this.activeDropdowns.add({ dropdown, panel });

        // Emit event
        utils.emit(dropdown, 'dropdown:open');
    },

    close(dropdown, panel) {
        utils.removeClass(panel, 'dropdown-open');
        utils.attr(panel, 'aria-hidden', 'true');
        this.activeDropdowns.delete({ dropdown, panel });
        utils.emit(dropdown, 'dropdown:close');
    },

    closeAll() {
        utils.qsa('[data-dropdown-panel].dropdown-open').forEach(panel => {
            utils.removeClass(panel, 'dropdown-open');
            utils.attr(panel, 'aria-hidden', 'true');
        });
        this.activeDropdowns.clear();
    },

    position(dropdown, panel) {
        const trigger = utils.qs('[data-dropdown-trigger]', dropdown) || dropdown.firstElementChild;
        const rect = trigger.getBoundingClientRect();
        const panelRect = panel.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;

        // Collision detection
        const spaceBelow = viewportHeight - rect.bottom;
        const spaceAbove = rect.top;
        const spaceRight = viewportWidth - rect.left;

        // Reset classes
        utils.removeClass(panel, 'dropdown-top', 'dropdown-bottom', 'dropdown-left', 'dropdown-right');

        // Vertical positioning
        if (spaceBelow < panelRect.height && spaceAbove > spaceBelow) {
            utils.addClass(panel, 'dropdown-top');
        } else {
            utils.addClass(panel, 'dropdown-bottom');
        }

        // Horizontal positioning
        if (spaceRight < panelRect.width) {
            utils.addClass(panel, 'dropdown-right');
        } else {
            utils.addClass(panel, 'dropdown-left');
        }
    }
};

// Dropdown styles
(function() {
    if (document.getElementById('dropdown-styles')) return;
    const style = utils.createElement('style', { id: 'dropdown-styles' });
    style.textContent = [
        '[data-dropdown-panel] {',
        '    position: absolute; z-index: 50; opacity: 0; visibility: hidden;',
        '    transform: scale(0.95) translateY(-4px);',
        '    transition: opacity 0.15s ease, transform 0.15s ease, visibility 0.15s;',
        '}',
        '[data-dropdown-panel].dropdown-open { opacity: 1; visibility: visible; transform: scale(1) translateY(0); }',
        '[data-dropdown-panel].dropdown-top { bottom: 100%; top: auto; margin-bottom: 0.5rem; }',
        '[data-dropdown-panel].dropdown-bottom { top: 100%; bottom: auto; margin-top: 0.5rem; }',
        '[data-dropdown-panel].dropdown-right { right: 0; left: auto; }',
        '[data-dropdown-panel].dropdown-left { left: 0; right: auto; }'
    ].join('\\n');
    document.head.appendChild(style);
})();

document.addEventListener('DOMContentLoaded', () => Dropdown.init());
""",
    dependencies=["utils"],
    description="Dropdown menus with smart collision detection",
    auto_detect_patterns=[
        r'data-dropdown',
        r'dropdown-trigger',
        r'dropdown-panel',
    ],
)


# =============================================================================
# MODAL - With Focus Trap
# =============================================================================

JS_MODAL = JSModule(
    name="modal",
    code="""
// Modal with Focus Trap
const Modal = {
    activeModal: null,
    previousFocus: null,

    init(selector = '[data-modal]') {
        // Modal triggers
        utils.qsa('[data-modal-open]').forEach(trigger => {
            utils.on(trigger, 'click', () => {
                const modalId = trigger.dataset.modalOpen;
                const modal = utils.qs('[data-modal="' + modalId + '"]');
                if (modal) this.open(modal);
            });
        });

        // Close buttons
        utils.qsa('[data-modal-close]').forEach(btn => {
            utils.on(btn, 'click', () => this.close());
        });

        // Backdrop click
        utils.qsa(selector).forEach(modal => {
            utils.on(modal, 'click', (e) => {
                if (e.target === modal) this.close();
            });
        });

        // Escape key
        utils.on(document, 'keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.close();
            }
        });
    },

    open(modal) {
        if (this.activeModal) this.close();

        // Store previous focus
        this.previousFocus = document.activeElement;
        this.activeModal = modal;

        // Show modal
        utils.addClass(modal, 'modal-open');
        utils.attr(modal, 'aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        // Focus trap
        this.trapFocus(modal);

        // Focus first focusable element
        const firstFocusable = this.getFocusableElements(modal)[0];
        if (firstFocusable) {
            setTimeout(() => firstFocusable.focus(), 50);
        }

        utils.emit(modal, 'modal:open');
    },

    close() {
        if (!this.activeModal) return;

        const modal = this.activeModal;

        utils.removeClass(modal, 'modal-open');
        utils.attr(modal, 'aria-hidden', 'true');
        document.body.style.overflow = '';

        // Restore focus
        if (this.previousFocus) {
            this.previousFocus.focus();
        }

        this.activeModal = null;
        this.previousFocus = null;

        utils.emit(modal, 'modal:close');
    },

    getFocusableElements(container) {
        const focusableSelectors = [
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            '[tabindex]:not([tabindex="-1"])',
        ];
        return utils.qsa(focusableSelectors.join(','), container);
    },

    trapFocus(modal) {
        const focusHandler = (e) => {
            if (e.key !== 'Tab') return;

            const focusable = this.getFocusableElements(modal);
            const first = focusable[0];
            const last = focusable[focusable.length - 1];

            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                if (last) last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                if (first) first.focus();
            }
        };

        // Remove old handler if exists
        if (modal._focusTrapHandler) utils.off(modal, 'keydown', modal._focusTrapHandler);

        // Add new handler
        modal._focusTrapHandler = focusHandler;
        utils.on(modal, 'keydown', focusHandler);
    }
};

// Modal styles
(function() {
    if (document.getElementById('modal-styles')) return;
    const style = utils.createElement('style', { id: 'modal-styles' });
    style.textContent = [
        '[data-modal] {',
        '    position: fixed; inset: 0; z-index: 100;',
        '    display: flex; align-items: center; justify-content: center;',
        '    opacity: 0; visibility: hidden; transition: opacity 0.2s ease, visibility 0.2s;',
        '}',
        '[data-modal].modal-open { opacity: 1; visibility: visible; }',
        '[data-modal] > *:not(.modal-backdrop) {',
        '    transform: scale(0.95) translateY(10px); transition: transform 0.2s ease;',
        '}',
        '[data-modal].modal-open > *:not(.modal-backdrop) { transform: scale(1) translateY(0); }'
    ].join('\\n');
    document.head.appendChild(style);
})();

document.addEventListener('DOMContentLoaded', () => Modal.init());
""",
    dependencies=["utils"],
    description="Modal dialogs with focus trap for accessibility",
    auto_detect_patterns=[
        r'data-modal',
        r'modal-open',
        r'modal-close',
    ],
)


# =============================================================================
# CAROUSEL / SLIDER
# =============================================================================

JS_CAROUSEL = JSModule(
    name="carousel",
    code="""
// Carousel / Slider
const Carousel = {
    instances: new Map(),

    init(selector = '[data-carousel]') {
        utils.qsa(selector).forEach((carousel, index) => {
            const id = carousel.dataset.carousel || ('carousel-' + index);
            this.create(carousel, id);
        });
    },

    create(carousel, id) {
        const track = utils.qs('[data-carousel-track]', carousel);
        const slides = utils.qsa('[data-carousel-slide]', carousel);
        const prevBtn = utils.qs('[data-carousel-prev]', carousel);
        const nextBtn = utils.qs('[data-carousel-next]', carousel);
        const dots = utils.qs('[data-carousel-dots]', carousel);

        if (!track || slides.length === 0) return;

        const instance = {
            carousel,
            track,
            slides,
            currentIndex: 0,
            autoplay: carousel.dataset.autoplay !== undefined,
            interval: parseInt(carousel.dataset.interval) || 5000,
            loop: carousel.dataset.loop !== 'false',
            autoplayTimer: null,
        };

        // Create dots if container exists
        if (dots) {
            slides.forEach((_, i) => {
                const dot = utils.createElement('button', {
                    className: 'carousel-dot',
                    'aria-label': 'Go to slide ' + (i + 1)
                });
                utils.on(dot, 'click', () => this.goTo(id, i));
                dots.appendChild(dot);
            });
        }

        // Button handlers
        if (prevBtn) {
            utils.on(prevBtn, 'click', () => this.prev(id));
        }
        if (nextBtn) {
            utils.on(nextBtn, 'click', () => this.next(id));
        }

        // Keyboard navigation
        utils.on(carousel, 'keydown', (e) => {
            if (e.key === 'ArrowLeft') this.prev(id);
            if (e.key === 'ArrowRight') this.next(id);
        });

        // Touch/swipe support
        let touchStart = 0;
        utils.on(carousel, 'touchstart', (e) => {
            touchStart = e.touches[0].clientX;
            this.stopAutoplay(id);
        }, { passive: true });

        utils.on(carousel, 'touchend', (e) => {
            const touchEnd = e.changedTouches[0].clientX;
            const diff = touchStart - touchEnd;
            if (Math.abs(diff) > 50) {
                diff > 0 ? this.next(id) : this.prev(id);
            }
            if (instance.autoplay) this.startAutoplay(id);
        }, { passive: true });

        this.instances.set(id, instance);
        this.updateUI(id);

        if (instance.autoplay) {
            this.startAutoplay(id);
        }

        return instance;
    },

    goTo(id, index) {
        const instance = this.instances.get(id);
        if (!instance) return;

        const { slides, loop } = instance;
        const maxIndex = slides.length - 1;

        if (loop) {
            instance.currentIndex = index < 0 ? maxIndex : index > maxIndex ? 0 : index;
        } else {
            instance.currentIndex = Math.max(0, Math.min(index, maxIndex));
        }

        this.updateUI(id);
        utils.emit(instance.carousel, 'carousel:change', { index: instance.currentIndex });
    },

    next(id) {
        const instance = this.instances.get(id);
        if (instance) this.goTo(id, instance.currentIndex + 1);
    },

    prev(id) {
        const instance = this.instances.get(id);
        if (instance) this.goTo(id, instance.currentIndex - 1);
    },

    updateUI(id) {
        const instance = this.instances.get(id);
        if (!instance) return;

        const { track, slides, carousel, currentIndex } = instance;

        // Move track
        track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';

        // Update slides
        slides.forEach((slide, i) => {
            utils.toggleClass(slide, 'carousel-slide-active', i === currentIndex);
            slide.setAttribute('aria-hidden', i !== currentIndex);
        });

        // Update dots
        const dotElements = utils.qsa('.carousel-dot', carousel);
        dotElements.forEach((dot, i) => {
            utils.toggleClass(dot, 'carousel-dot-active', i === currentIndex);
        });

        // Update buttons
        const prevBtn = utils.qs('[data-carousel-prev]', carousel);
        const nextBtn = utils.qs('[data-carousel-next]', carousel);

        if (!instance.loop) {
            if (prevBtn) prevBtn.disabled = currentIndex === 0;
            if (nextBtn) nextBtn.disabled = currentIndex === slides.length - 1;
        }
    },

    startAutoplay(id) {
        const instance = this.instances.get(id);
        if (!instance) return;

        this.stopAutoplay(id);
        instance.autoplayTimer = setInterval(() => this.next(id), instance.interval);
    },

    stopAutoplay(id) {
        const instance = this.instances.get(id);
        if (instance && instance.autoplayTimer) {
            clearInterval(instance.autoplayTimer);
            instance.autoplayTimer = null;
        }
    }
};

// Carousel styles
(function() {
    if (document.getElementById('carousel-styles')) return;
    const style = utils.createElement('style', { id: 'carousel-styles' });
    style.textContent = [
        '[data-carousel] { position: relative; overflow: hidden; }',
        '[data-carousel-track] { display: flex; transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1); }',
        '[data-carousel-slide] { flex: 0 0 100%; }',
        '.carousel-dot {',
        '    width: 8px; height: 8px; border-radius: 50%;',
        '    background: rgba(0,0,0,0.3); border: none; cursor: pointer;',
        '    transition: background 0.2s, transform 0.2s;',
        '}',
        '.carousel-dot:hover { transform: scale(1.2); }',
        '.carousel-dot-active { background: currentColor; }'
    ].join('\\n');
    document.head.appendChild(style);
})();

document.addEventListener('DOMContentLoaded', () => Carousel.init());
""",
    dependencies=["utils"],
    description="Carousel/slider with touch support and autoplay",
    auto_detect_patterns=[
        r'data-carousel',
        r'carousel-track',
        r'carousel-slide',
    ],
)


# =============================================================================
# TABS
# =============================================================================

JS_TABS = JSModule(
    name="tabs",
    code="""
// Tabs Component
const Tabs = {
    init(selector = '[data-tabs]') {
        utils.qsa(selector).forEach(tabContainer => {
            const tabs = utils.qsa('[role="tab"]', tabContainer);
            const panels = utils.qsa('[role="tabpanel"]', tabContainer);

            tabs.forEach((tab, index) => {
                // Click handler
                utils.on(tab, 'click', () => this.activate(tabContainer, index));

                // Keyboard navigation
                utils.on(tab, 'keydown', (e) => {
                    let newIndex = index;

                    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                        newIndex = (index + 1) % tabs.length;
                    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                        newIndex = (index - 1 + tabs.length) % tabs.length;
                    } else if (e.key === 'Home') {
                        newIndex = 0;
                    } else if (e.key === 'End') {
                        newIndex = tabs.length - 1;
                    } else {
                        return;
                    }

                    e.preventDefault();
                    this.activate(tabContainer, newIndex);
                    tabs[newIndex].focus();
                });
            });

            // Activate first tab by default
            const activeIndex = tabs.findIndex(t => t.getAttribute('aria-selected') === 'true');
            this.activate(tabContainer, activeIndex >= 0 ? activeIndex : 0);
        });
    },

    activate(container, index) {
        const tabs = utils.qsa('[role="tab"]', container);
        const panels = utils.qsa('[role="tabpanel"]', container);

        tabs.forEach((tab, i) => {
            const isActive = i === index;
            tab.setAttribute('aria-selected', isActive);
            tab.setAttribute('tabindex', isActive ? '0' : '-1');
            utils.toggleClass(tab, 'tab-active', isActive);
        });

        panels.forEach((panel, i) => {
            const isActive = i === index;
            panel.hidden = !isActive;
            utils.toggleClass(panel, 'tabpanel-active', isActive);
        });

        utils.emit(container, 'tabs:change', { index });
    }
};

// Tab styles
(function() {
    if (document.getElementById('tabs-styles')) return;
    const style = utils.createElement('style', { id: 'tabs-styles' });
    style.textContent = [
        '[role="tab"] { cursor: pointer; transition: color 0.2s, border-color 0.2s, background 0.2s; }',
        '[role="tab"]:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }',
        '[role="tabpanel"] { animation: tabFadeIn 0.2s ease; }',
        '[role="tabpanel"][hidden] { display: none; }',
        '@keyframes tabFadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }'
    ].join('\\n');
    document.head.appendChild(style);
})();

document.addEventListener('DOMContentLoaded', () => Tabs.init());
""",
    dependencies=["utils"],
    description="Accessible tabs with keyboard navigation",
    auto_detect_patterns=[
        r'data-tabs',
        r'role="tablist"',
        r'role="tab"',
    ],
)


# =============================================================================
# ACCORDION
# =============================================================================

JS_ACCORDION = JSModule(
    name="accordion",
    code="""
// Accordion Component
const Accordion = {
    init(selector = '[data-accordion]') {
        utils.qsa(selector).forEach(accordion => {
            const items = utils.qsa('[data-accordion-item]', accordion);
            const allowMultiple = accordion.dataset.multiple !== undefined;

            items.forEach((item) => {
                const trigger = utils.qs('[data-accordion-trigger]', item);
                const content = utils.qs('[data-accordion-content]', item);

                if (!trigger || !content) return;

                // Set initial state
                const isOpen = item.dataset.open !== undefined;
                this.setItemState(item, isOpen);

                // Click handler
                utils.on(trigger, 'click', () => {
                    const currentlyOpen = item.dataset.open !== undefined;

                    if (!allowMultiple && !currentlyOpen) {
                        // Close others
                        items.forEach(other => {
                            if (other !== item) this.setItemState(other, false);
                        });
                    }

                    this.setItemState(item, !currentlyOpen);
                });

                // Keyboard handler
                utils.on(trigger, 'keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        trigger.click();
                    }
                });
            });
        });
    },

    setItemState(item, open) {
        const trigger = utils.qs('[data-accordion-trigger]', item);
        const content = utils.qs('[data-accordion-content]', item);

        if (open) {
            item.dataset.open = '';
            if (trigger) trigger.setAttribute('aria-expanded', 'true');
            if (content) {
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        } else {
            delete item.dataset.open;
            if (trigger) trigger.setAttribute('aria-expanded', 'false');
            if (content) {
                content.style.maxHeight = '0px';
            }
        }

        utils.emit(item, 'accordion:toggle', { open });
    }
};

// Accordion styles
(function() {
    if (document.getElementById('accordion-styles')) return;
    const style = utils.createElement('style', { id: 'accordion-styles' });
    style.textContent = [
        '[data-accordion-content] { overflow: hidden; max-height: 0; transition: max-height 0.3s ease-out; }',
        '[data-accordion-trigger] { cursor: pointer; user-select: none; }',
        '[data-accordion-trigger]:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }',
        '[data-accordion-item] [data-accordion-icon] { transition: transform 0.3s ease; }',
        '[data-accordion-item][data-open] [data-accordion-icon] { transform: rotate(180deg); }'
    ].join('\\n');
    document.head.appendChild(style);
})();

document.addEventListener('DOMContentLoaded', () => Accordion.init());
""",
    dependencies=["utils"],
    description="Accordion/collapsible sections with smooth animations",
    auto_detect_patterns=[
        r'data-accordion',
        r'accordion-trigger',
        r'accordion-content',
    ],
)


# =============================================================================
# TOAST NOTIFICATIONS
# =============================================================================

JS_TOAST = JSModule(
    name="toast",
    code="""
// Toast Notifications
const Toast = {
    container: null,
    svgPaths: {
        info: ['M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'],
        success: ['M5 13l4 4L19 7'],
        warning: ['M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'],
        error: ['M6 18L18 6M6 6l12 12']
    },

    init() {
        if (!this.container) {
            this.container = utils.createElement('div', {
                id: 'toast-container',
                className: 'fixed bottom-4 right-4 z-50 flex flex-col gap-2',
                role: 'alert',
                'aria-live': 'polite'
            });
            document.body.appendChild(this.container);
        }
    },

    show(message, options = {}) {
        this.init();

        const defaults = {
            type: 'info', // info, success, warning, error
            duration: 5000,
            dismissible: true,
            icon: true,
        };
        const config = { ...defaults, ...options };

        // Create toast element
        const toast = utils.createElement('div', { className: 'toast toast-' + config.type });

        // Add icon
        if (config.icon && this.svgPaths[config.type]) {
            const iconContainer = utils.createElement('span', { className: 'toast-icon' });
            iconContainer.appendChild(utils.createSvg(this.svgPaths[config.type], 'w-5 h-5'));
            toast.appendChild(iconContainer);
        }

        // Add message
        const msgSpan = utils.createElement('span', { className: 'toast-message', textContent: message });
        toast.appendChild(msgSpan);

        // Add close button
        if (config.dismissible) {
            const closeBtn = utils.createElement('button', {
                className: 'toast-close',
                'aria-label': 'Close',
                textContent: '\\u00d7'
            });
            utils.on(closeBtn, 'click', () => this.dismiss(toast));
            toast.appendChild(closeBtn);
        }

        // Add to container
        this.container.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('toast-show');
        });

        // Auto dismiss
        if (config.duration > 0) {
            setTimeout(() => this.dismiss(toast), config.duration);
        }

        return toast;
    },

    dismiss(toast) {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-hide');

        setTimeout(() => {
            toast.remove();
        }, 300);
    },

    // Convenience methods
    info: function(msg, opts) { return Toast.show(msg, { ...opts, type: 'info' }); },
    success: function(msg, opts) { return Toast.show(msg, { ...opts, type: 'success' }); },
    warning: function(msg, opts) { return Toast.show(msg, { ...opts, type: 'warning' }); },
    error: function(msg, opts) { return Toast.show(msg, { ...opts, type: 'error' }); }
};

// Toast styles
(function() {
    if (document.getElementById('toast-styles')) return;
    const style = utils.createElement('style', { id: 'toast-styles' });
    style.textContent = [
        '.toast {',
        '    display: flex; align-items: center; gap: 0.75rem;',
        '    padding: 0.75rem 1rem; border-radius: 0.5rem;',
        '    background: white;',
        '    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);',
        '    transform: translateX(100%); opacity: 0;',
        '    transition: transform 0.3s ease, opacity 0.3s ease;',
        '}',
        '.toast-show { transform: translateX(0); opacity: 1; }',
        '.toast-hide { transform: translateX(100%); opacity: 0; }',
        '.toast-info { border-left: 4px solid #3B82F6; }',
        '.toast-success { border-left: 4px solid #10B981; }',
        '.toast-warning { border-left: 4px solid #F59E0B; }',
        '.toast-error { border-left: 4px solid #EF4444; }',
        '.toast-icon { flex-shrink: 0; }',
        '.toast-info .toast-icon { color: #3B82F6; }',
        '.toast-success .toast-icon { color: #10B981; }',
        '.toast-warning .toast-icon { color: #F59E0B; }',
        '.toast-error .toast-icon { color: #EF4444; }',
        '.toast-message { flex: 1; }',
        '.toast-close {',
        '    flex-shrink: 0; width: 1.5rem; height: 1.5rem;',
        '    border: none; background: transparent; cursor: pointer;',
        '    opacity: 0.5; transition: opacity 0.2s;',
        '}',
        '.toast-close:hover { opacity: 1; }',
        '@media (prefers-color-scheme: dark) { .toast { background: #1E293B; color: #F1F5F9; } }'
    ].join('\\n');
    document.head.appendChild(style);
})();

// Make Toast globally available
window.Toast = Toast;
""",
    dependencies=["utils"],
    description="Toast notification system with auto-dismiss",
    auto_detect_patterns=[
        r'Toast\.',
        r'toast-container',
        r'data-toast',
    ],
)


# =============================================================================
# MODULE REGISTRY
# =============================================================================

JS_MODULES: Dict[str, JSModule] = {
    "utils": JS_UTILS,
    "intersection_observer": JS_INTERSECTION_OBSERVER,
    "dropdown": JS_DROPDOWN,
    "modal": JS_MODAL,
    "carousel": JS_CAROUSEL,
    "tabs": JS_TABS,
    "accordion": JS_ACCORDION,
    "toast": JS_TOAST,
}


# Component to module mapping
COMPONENT_JS_REQUIREMENTS: Dict[str, List[str]] = {
    "dropdown": ["dropdown"],
    "modal": ["modal"],
    "carousel": ["carousel"],
    "slider": ["carousel"],
    "tabs": ["tabs"],
    "accordion": ["accordion"],
    "faq": ["accordion"],
    "hero": ["intersection_observer"],
    "features": ["intersection_observer"],
    "testimonials": ["carousel", "intersection_observer"],
    "pricing": ["tabs", "intersection_observer"],
    "navbar": ["dropdown"],
    "sidebar": ["accordion"],
    "notification": ["toast"],
    "alert": ["toast"],
}


# =============================================================================
# PUBLIC API
# =============================================================================

def get_js_module(module_name: str) -> Optional[str]:
    """Get JavaScript code for a specific module.

    Args:
        module_name: Name of the module (e.g., 'modal', 'dropdown')

    Returns:
        JavaScript code string or None if not found
    """
    module = JS_MODULES.get(module_name)
    if not module:
        return None

    # Get dependencies first
    code_parts = []
    for dep in module.dependencies:
        dep_module = JS_MODULES.get(dep)
        if dep_module:
            code_parts.append(f"// === {dep.upper()} ===\n{dep_module.code}")

    # Add main module
    code_parts.append(f"// === {module_name.upper()} ===\n{module.code}")

    return "\n\n".join(code_parts)


def get_js_for_component(component_type: str) -> str:
    """Get all JavaScript needed for a component type.

    Args:
        component_type: Component type (e.g., 'modal', 'carousel', 'navbar')

    Returns:
        Combined JavaScript code string
    """
    modules_needed = COMPONENT_JS_REQUIREMENTS.get(component_type.lower(), [])

    if not modules_needed:
        return ""

    # Collect unique modules including dependencies
    all_modules: Set[str] = set()

    def add_with_deps(name: str):
        if name not in all_modules:
            module = JS_MODULES.get(name)
            if module:
                for dep in module.dependencies:
                    add_with_deps(dep)
                all_modules.add(name)

    for module_name in modules_needed:
        add_with_deps(module_name)

    # Generate code in dependency order
    code_parts = []

    # Utils always first if needed
    if "utils" in all_modules:
        code_parts.append(JS_MODULES["utils"].code)
        all_modules.remove("utils")

    # Then rest of modules
    for name in all_modules:
        module = JS_MODULES.get(name)
        if module:
            code_parts.append(f"// === {name.upper()} ===\n{module.code}")

    return "\n\n".join(code_parts)


def detect_needed_modules(html: str) -> Set[str]:
    """Detect which JS modules are needed based on HTML content.

    Args:
        html: HTML content to analyze

    Returns:
        Set of module names that are needed
    """
    needed = set()

    for name, module in JS_MODULES.items():
        for pattern in module.auto_detect_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                needed.add(name)
                # Add dependencies
                for dep in module.dependencies:
                    needed.add(dep)
                break

    return needed


def inject_js_fallbacks(
    html: str,
    modules: Optional[List[str]] = None,
    detect_needed: bool = True,
) -> str:
    """Inject JavaScript fallbacks into HTML.

    Args:
        html: HTML content
        modules: Specific modules to inject (optional)
        detect_needed: Auto-detect needed modules from HTML

    Returns:
        HTML with JavaScript injected before </body>
    """
    # Determine which modules to include
    modules_to_inject: Set[str] = set()

    if modules:
        for m in modules:
            modules_to_inject.add(m)
            # Add dependencies
            module = JS_MODULES.get(m)
            if module:
                modules_to_inject.update(module.dependencies)

    if detect_needed:
        modules_to_inject.update(detect_needed_modules(html))

    if not modules_to_inject:
        return html

    # Build JS code
    code_parts = []

    # Utils first
    if "utils" in modules_to_inject:
        code_parts.append(JS_MODULES["utils"].code)
        modules_to_inject.remove("utils")

    for name in sorted(modules_to_inject):
        module = JS_MODULES.get(name)
        if module:
            code_parts.append(module.code)

    js_code = "\n\n".join(code_parts)

    # Wrap in script tag
    script_tag = f"""
<script>
(function() {{
{js_code}
}})();
</script>
"""

    # Inject before </body> or at end
    if "</body>" in html.lower():
        # Use lambda to avoid regex escape issues in JS code
        html = re.sub(
            r"(</body>)",
            lambda m: f"{script_tag}{m.group(1)}",
            html,
            flags=re.IGNORECASE,
        )
    else:
        html = html + script_tag

    return html


def get_all_module_names() -> List[str]:
    """Get list of all available module names."""
    return list(JS_MODULES.keys())


def get_module_info(module_name: str) -> Optional[Dict]:
    """Get information about a specific module.

    Args:
        module_name: Name of the module

    Returns:
        Dict with module info or None
    """
    module = JS_MODULES.get(module_name)
    if not module:
        return None

    return {
        "name": module.name,
        "description": module.description,
        "dependencies": module.dependencies,
        "auto_detect_patterns": module.auto_detect_patterns,
        "code_size": len(module.code),
    }
