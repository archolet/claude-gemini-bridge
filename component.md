# Enterprise UI Component Direktifleri: 7 Agent İçin Kapsamlı Rehber

Multi-agent sistemindeki her agent için enterprise-grade UI komponentlerinin oluşturulmasında kullanılacak **direktifler, TODO listeleri ve best practice'ler** bu raporda derlenmiştir. HTML5, TailwindCSS ve Alpine.js stack'i üzerinde odaklanılmıştır.

---

## Strategist Agent Direktifleri

Strategist, komponent DNA'sını çıkararak planlama ve section analizi yapar.

### Yeni Direktifler

**Komponent Kompleksite Sınıflandırması:**
- **Tier 1 (Basit):** Button, Badge, Avatar, Toggle - tek state, minimal etkileşim
- **Tier 2 (Orta):** Dropdown, Modal, Tabs, Toast - çoklu state, keyboard nav
- **Tier 3 (Kompleks):** Data Grid, Tree Grid, Form Builder - nested state, virtual scroll, CRUD
- **Tier 4 (Enterprise):** Pivot Table, Dashboard Builder, Command Palette - drag-drop, aggregation, real-time

**DNA Extraction Template:**
```yaml
component_dna:
  category: [data-display|data-entry|navigation|feedback|layout]
  tier: [1-4]
  features:
    - core: [required_features]
    - optional: [enhancement_features]
  dependencies:
    - alpine_plugins: [intersect|focus|persist|anchor]
    - external_libs: []
  accessibility_level: [A|AA|AAA]
  performance_concern: [none|moderate|high]
```

### TODO List

- [ ] Her komponent için complexity tier belirleme algoritması ekle
- [ ] Komponent bağımlılık grafiği oluştur (hangi komponent hangi alt komponenti kullanır)
- [ ] Feature flag sistemi tasarla (Progressive Enhancement için)
- [ ] Responsive breakpoint stratejisi belirle (mobile-first vs desktop-first)
- [ ] Section analizi için ARIA landmark mapping'i tanımla

### Anti-Patterns
- ❌ Tüm özellikleri aynı anda implement etmeye çalışma
- ❌ Komponent bağımlılıklarını göz ardı etme
- ❌ Mobile/touch desteğini sonraya bırakma

---

## Architect Agent Direktifleri

Architect, HTML yapısı, semantik markup ve ARIA attributes'tan sorumludur.

### Yeni Direktifler

**Semantik HTML Referans Tablosu:**

| Komponent | Ana Element | ARIA Role | Kritik Attributes |
|-----------|------------|-----------|-------------------|
| Data Grid | `div` | `grid` | `aria-rowcount`, `aria-colcount`, `aria-sort` |
| Tree Grid | `div` | `treegrid` | `aria-expanded`, `aria-level`, `aria-setsize` |
| Pivot Table | `table` | `grid` | `aria-labelledby`, group headers |
| Form Builder | `form` | - | `novalidate`, `aria-describedby` |
| Autocomplete | `div` | `combobox` | `aria-autocomplete`, `aria-activedescendant` |
| Modal | `dialog`/`div` | `dialog` | `aria-modal`, `aria-labelledby` |
| Toast | `div` | `alert` | `aria-live="assertive"`, `aria-atomic` |
| Tab Panel | `div` | `tablist`+`tab`+`tabpanel` | `aria-selected`, `aria-controls` |
| Menu | `nav>ul` | `menubar`+`menu`+`menuitem` | `aria-haspopup`, `aria-expanded` |
| Progress | `div` | `progressbar` | `aria-valuenow`, `aria-valuemin`, `aria-valuemax` |
| Slider | `div` | `slider` | `aria-valuenow`, `aria-valuetext` |
| Switch | `button` | `switch` | `aria-checked` |

**Grid/Table Markup Pattern:**
```html
<div role="grid" aria-label="[Grid Name]" aria-rowcount="[total]" aria-colcount="[total]">
  <div role="rowgroup"> <!-- Header -->
    <div role="row" aria-rowindex="1">
      <div role="columnheader" aria-colindex="1" aria-sort="[ascending|descending|none]" tabindex="0">
        Column Name
      </div>
    </div>
  </div>
  <div role="rowgroup"> <!-- Body -->
    <div role="row" aria-rowindex="2" aria-selected="false">
      <div role="gridcell" aria-colindex="1" tabindex="-1">Cell Content</div>
    </div>
  </div>
</div>
```

**Form Field Pattern:**
```html
<div class="field-group">
  <label for="[id]" id="[id]-label">[Label]</label>
  <input 
    type="[type]" 
    id="[id]"
    aria-labelledby="[id]-label"
    aria-describedby="[id]-error [id]-hint"
    aria-invalid="[true|false]"
    aria-required="[true|false]"
  />
  <span id="[id]-hint" class="hint">[Helper text]</span>
  <span id="[id]-error" role="alert" aria-live="polite">[Error message]</span>
</div>
```

**Live Region Pattern:**
```html
<!-- Status announcements -->
<div aria-live="polite" aria-atomic="true" class="sr-only" id="status-region"></div>

<!-- Error announcements (urgent) -->
<div aria-live="assertive" aria-atomic="true" class="sr-only" id="error-region"></div>
```

### TODO List

- [ ] Her komponent için tam ARIA role/attribute checklist oluştur
- [ ] Keyboard navigation markup şablonları hazırla
- [ ] Roving tabindex vs aria-activedescendant seçim kriterleri belirle
- [ ] Landmark region hierarchy tanımla (main, navigation, complementary, contentinfo)
- [ ] Skip link pattern'ını tüm kompleks komponentlere ekle
- [ ] Data attribute convention'ı standartlaştır (`data-*` for Alpine.js binding)
- [ ] Nested dialog/modal markup stratejisi belirle
- [ ] Table vs Grid vs Treegrid seçim kriterleri dokümante et

### Best Practices
- ✅ Native HTML elementlerini tercih et (`<button>`, `<dialog>`, `<details>`)
- ✅ Her interactive element için visible focus indicator sağla
- ✅ `aria-describedby` ile ek bağlam sağla
- ✅ Form validation için `aria-invalid` ve `aria-errormessage` kullan
- ✅ Virtual scrolling'de `aria-rowindex`/`aria-colindex` zorunlu

### Anti-Patterns
- ❌ `<div>` veya `<span>` ile interactive element oluşturma
- ❌ `tabindex > 0` kullanma (doğal sırayı bozar)
- ❌ `aria-expanded` leaf node'lara ekleme
- ❌ Placeholder'ı label yerine kullanma
- ❌ Focus outline'ı tamamen kaldırma

---

## Alchemist Agent Direktifleri

Alchemist, CSS/TailwindCSS styling ve tema uygulamasından sorumludur.

### Yeni Direktifler

**Component State Class Patterns:**
```html
<!-- Base + State variants -->
<button class="
  px-4 py-2 rounded-md font-medium transition-colors duration-150
  bg-blue-600 text-white
  hover:bg-blue-700
  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  disabled:bg-gray-300 disabled:cursor-not-allowed
  active:bg-blue-800
">

<!-- Data attribute styling (for Alpine.js state) -->
<div class="
  data-[selected=true]:bg-blue-50 
  data-[selected=true]:border-blue-500
  data-[loading=true]:animate-pulse
  data-[error=true]:border-red-500
">

<!-- ARIA state styling -->
<button class="
  aria-expanded:bg-gray-100
  aria-selected:border-blue-500
  aria-checked:bg-blue-600
  aria-invalid:border-red-500
">
```

**Frozen Column/Row Pattern (Sticky Positioning):**
```html
<!-- Sticky header -->
<thead class="sticky top-0 z-10 bg-white dark:bg-gray-800">

<!-- Frozen first column -->
<th class="sticky left-0 z-20 bg-white shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]">

<!-- Corner cell (frozen header + column intersection) -->
<th class="sticky top-0 left-0 z-30 bg-gray-100">
```

**Dark Mode Variant System:**
```html
<div class="
  bg-white dark:bg-slate-800
  text-gray-900 dark:text-gray-100
  border-gray-200 dark:border-gray-700
  shadow-sm dark:shadow-slate-700/30
">
```

**Animation/Transition Classes:**
```html
<!-- Enter/Leave transitions (for x-show) -->
<div
  x-transition:enter="transition ease-out duration-200"
  x-transition:enter-start="opacity-0 translate-y-1"
  x-transition:enter-end="opacity-100 translate-y-0"
  x-transition:leave="transition ease-in duration-150"
  x-transition:leave-start="opacity-100 translate-y-0"
  x-transition:leave-end="opacity-0 translate-y-1"
>

<!-- Reduced motion support -->
<div class="transition-all duration-300 motion-reduce:transition-none motion-reduce:animate-none">
```

**Skeleton Loader Pattern:**
```css
/* Shimmer effect */
.skeleton-shimmer {
  @apply relative overflow-hidden bg-slate-200 dark:bg-slate-700;
}
.skeleton-shimmer::after {
  @apply absolute inset-0 -translate-x-full;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: shimmer 1.5s infinite;
  content: '';
}
@keyframes shimmer {
  100% { transform: translateX(100%); }
}
```

**Z-Index Scale:**
```javascript
// tailwind.config.js
zIndex: {
  'dropdown': '100',
  'sticky': '200', 
  'fixed': '300',
  'modal-backdrop': '400',
  'modal': '500',
  'popover': '600',
  'tooltip': '700',
  'toast': '800',
}
```

### TODO List

- [ ] Component-specific utility class extraction (`@apply` patterns) dokümante et
- [ ] Responsive breakpoint strategy belirle (container queries vs media queries)
- [ ] Color semantic token sistemi oluştur (success, warning, error, info)
- [ ] Focus ring standardı belirle (ring-2 ring-offset-2 ring-[color]-500)
- [ ] Animation timing functions standardize et (ease-out for enter, ease-in for leave)
- [ ] Touch target minimum boyut enforce et (min-h-11 min-w-11 = 44px)
- [ ] Scrollbar styling patterns (scrollbar-hide, custom scrollbar)
- [ ] Print stylesheet considerations

### Best Practices
- ✅ `focus-visible:` tercih et (sadece keyboard focus için)
- ✅ `motion-reduce:` variant'ları her animasyonda kullan
- ✅ Semantic color tokens kullan (primary, secondary vs blue, red)
- ✅ CSS containment kullan (`contain: layout style paint`)
- ✅ `content-visibility: auto` large lists için

### Anti-Patterns
- ❌ Arbitrary values overuse (`z-[9999]`, `w-[137px]`)
- ❌ `!important` kullanımı
- ❌ Inline style ile Tailwind karıştırma
- ❌ Aşırı `@apply` kullanımı (utility-first amacını bozar)

---

## Physicist Agent Direktifleri

Physicist, JavaScript/Alpine.js interaktivite ve state management'tan sorumludur.

### Yeni Direktifler

**Data Grid State Structure:**
```javascript
Alpine.data('dataGrid', () => ({
  // Data
  allData: [],
  columns: [],
  
  // Sorting (multi-column)
  sortColumns: [], // [{key: 'name', direction: 'asc'}]
  
  // Filtering
  filters: {},
  searchTerm: '',
  
  // Selection
  selectedRows: new Set(),
  activeCell: { row: 0, col: 0 },
  selectionMode: 'single', // single, multiple, range
  
  // Virtual Scrolling
  scrollTop: 0,
  containerHeight: 600,
  rowHeight: 40,
  overscan: 5,
  
  // Editing
  editingCell: null,
  editValue: '',
  
  // Computed
  get visibleRows() {
    const start = Math.max(0, Math.floor(this.scrollTop / this.rowHeight) - this.overscan);
    const end = Math.min(this.filteredData.length, 
      Math.ceil((this.scrollTop + this.containerHeight) / this.rowHeight) + this.overscan);
    return this.filteredData.slice(start, end);
  }
}));
```

**Form Validation Pattern:**
```javascript
Alpine.data('validatedForm', () => ({
  formData: {},
  errors: {},
  touched: {},
  submitting: false,
  
  rules: {
    email: [
      v => !!v || 'Email is required',
      v => /.+@.+\..+/.test(v) || 'Email must be valid'
    ],
    password: [
      v => !!v || 'Password is required',
      v => v.length >= 8 || 'Password must be at least 8 characters'
    ]
  },
  
  validate(field) {
    const value = this.formData[field];
    const fieldRules = this.rules[field] || [];
    
    for (const rule of fieldRules) {
      const result = rule(value);
      if (result !== true) {
        this.errors[field] = result;
        return false;
      }
    }
    this.errors[field] = null;
    return true;
  },
  
  async validateAsync(field, url) {
    this.validating = true;
    const result = await fetch(`${url}?value=${this.formData[field]}`).then(r => r.json());
    this.errors[field] = result.valid ? null : result.message;
    this.validating = false;
  }
}));
```

**Global Store Pattern:**
```javascript
document.addEventListener('alpine:init', () => {
  // Toast notifications store
  Alpine.store('toasts', {
    items: [],
    counter: 0,
    
    add(message, type = 'info', duration = 5000) {
      const id = this.counter++;
      this.items.push({ id, message, type, visible: true });
      if (duration > 0) setTimeout(() => this.remove(id), duration);
      return id;
    },
    
    remove(id) {
      const item = this.items.find(t => t.id === id);
      if (item) {
        item.visible = false;
        setTimeout(() => {
          this.items = this.items.filter(t => t.id !== id);
        }, 300);
      }
    }
  });
  
  // Modal stack store
  Alpine.store('modals', {
    stack: [],
    open(id) { this.stack.push(id); document.body.style.overflow = 'hidden'; },
    close(id) { 
      this.stack = this.stack.filter(m => m !== id); 
      if (this.stack.length === 0) document.body.style.overflow = '';
    },
    get active() { return this.stack[this.stack.length - 1]; }
  });
  
  // Theme store with persistence
  Alpine.store('theme', {
    current: localStorage.getItem('theme') || 'system',
    set(theme) {
      this.current = theme;
      localStorage.setItem('theme', theme);
      this.apply();
    },
    apply() {
      const isDark = this.current === 'dark' || 
        (this.current === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
      document.documentElement.classList.toggle('dark', isDark);
    }
  });
});
```

**Keyboard Navigation Pattern:**
```javascript
// W3C APG Grid keyboard navigation
handleKeydown(e) {
  const { row, col } = this.activeCell;
  const lastRow = this.filteredData.length - 1;
  const lastCol = this.columns.length - 1;
  
  const actions = {
    'ArrowRight': () => this.activeCell.col = Math.min(col + 1, lastCol),
    'ArrowLeft': () => this.activeCell.col = Math.max(col - 1, 0),
    'ArrowDown': () => this.activeCell.row = Math.min(row + 1, lastRow),
    'ArrowUp': () => this.activeCell.row = Math.max(row - 1, 0),
    'Home': () => e.ctrlKey ? this.activeCell = {row: 0, col: 0} : this.activeCell.col = 0,
    'End': () => e.ctrlKey ? this.activeCell = {row: lastRow, col: lastCol} : this.activeCell.col = lastCol,
    'PageDown': () => this.activeCell.row = Math.min(row + 10, lastRow),
    'PageUp': () => this.activeCell.row = Math.max(row - 10, 0),
    'Enter': () => this.startEdit(),
    'F2': () => this.startEdit(),
    'Escape': () => this.cancelEdit(),
    ' ': () => this.toggleSelection(this.filteredData[row].id)
  };
  
  if (actions[e.key]) {
    e.preventDefault();
    actions[e.key]();
    this.ensureVisible();
    this.announcePosition();
  }
}
```

**Debounce/Throttle Utilities:**
```javascript
// Alpine.js native debounce
x-model.debounce.300ms="searchQuery"
@input.debounce.500ms="validate()"

// Custom implementation
Alpine.magic('debounce', () => (fn, wait = 300) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, args), wait);
  };
});

// Throttle for scroll events
Alpine.magic('throttle', () => (fn, limit = 100) => {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
});
```

**Focus Trap Implementation:**
```javascript
Alpine.directive('trap', (el, { modifiers }) => {
  const focusable = el.querySelectorAll(
    'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  
  el.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
  
  first?.focus();
});
```

### TODO List

- [ ] Virtual scrolling component template oluştur
- [ ] Drag-drop state management pattern belirle
- [ ] Undo/redo history management implement et
- [ ] Optimistic update pattern'ları dokümante et
- [ ] URL state synchronization helper yaz
- [ ] Custom Alpine.js directives library oluştur (`x-trap`, `x-clickoutside`, `x-shortcut`)
- [ ] WebSocket/real-time update integration pattern
- [ ] Form wizard multi-step state management

### Best Practices
- ✅ `$nextTick()` kullan DOM update sonrası işlemler için
- ✅ `$watch()` ile reactive state changes izle
- ✅ `$persist` plugin ile localStorage persistence
- ✅ `$dispatch()` ile cross-component communication
- ✅ Cleanup: setTimeout/setInterval temizliği yap

### Anti-Patterns
- ❌ Component-local state için `$store` kullanma
- ❌ `x-data` içinde doğrudan DOM manipulation
- ❌ Deeply nested reactive state (performance)
- ❌ Missing `x-cloak` (FOUC)
- ❌ Event listener cleanup yapmama

---

## Critic Agent Direktifleri

Critic, kalite değerlendirme ve scoring'den sorumludur.

### Yeni Direktifler

**Komponent Kalite Scoring Matrix:**

| Kriter | Ağırlık | 0 Puan | 50 Puan | 100 Puan |
|--------|---------|--------|---------|----------|
| Semantik HTML | 15% | div soup | Kısmi semantic | Full semantic |
| ARIA Compliance | 20% | Eksik/yanlış | Temel ARIA | Complete ARIA pattern |
| Keyboard Nav | 15% | Yok | Tab only | Full W3C APG |
| Focus Management | 10% | Görünmez | Varsayılan | Custom visible ring |
| Dark Mode | 5% | Yok | Partial | Full support |
| Responsive | 10% | Yok | Breakpoint | Fluid/container |
| Performance | 10% | Blocking | Lazy load | Virtual + optimized |
| State Management | 10% | Spaghetti | Organized | $store + computed |
| Error Handling | 5% | Yok | Basic try/catch | Full user feedback |

**Accessibility Audit Checklist:**
```markdown
## WCAG 2.1 AA Compliance Check

### Perceivable
- [ ] All images have alt text
- [ ] Color contrast >= 4.5:1 (text), >= 3:1 (UI)
- [ ] Focus indicator contrast >= 3:1
- [ ] Content readable at 200% zoom

### Operable  
- [ ] All functionality keyboard accessible
- [ ] No keyboard traps
- [ ] Focus visible on all interactive elements
- [ ] Touch targets >= 44x44px
- [ ] Skip links present

### Understandable
- [ ] Labels associated with inputs
- [ ] Error messages descriptive
- [ ] Consistent navigation
- [ ] Language declared

### Robust
- [ ] Valid HTML
- [ ] ARIA roles/states correct
- [ ] Live regions for dynamic content
```

**Performance Metrics Thresholds:**
- **First Contentful Paint:** < 1.8s
- **Largest Contentful Paint:** < 2.5s
- **Cumulative Layout Shift:** < 0.1
- **Interaction to Next Paint:** < 200ms
- **JavaScript bundle size per component:** < 10KB gzipped

### TODO List

- [ ] Automated accessibility scoring tool entegrasyonu (axe-core)
- [ ] Visual regression testing setup (Playwright)
- [ ] Performance budget enforcement
- [ ] Component complexity metric (cyclomatic complexity for Alpine.js)
- [ ] Code review checklist generator
- [ ] ARIA usage validator
- [ ] Dark mode coverage checker

### Scoring Formula
```javascript
const score = (
  semanticScore * 0.15 +
  ariaScore * 0.20 +
  keyboardScore * 0.15 +
  focusScore * 0.10 +
  darkModeScore * 0.05 +
  responsiveScore * 0.10 +
  performanceScore * 0.10 +
  stateScore * 0.10 +
  errorHandlingScore * 0.05
) * 100;

// Grade: A (90+), B (80-89), C (70-79), D (60-69), F (<60)
```

---

## QualityGuard Agent Direktifleri

QualityGuard, validasyon, auto-fix ve production-ready check'ten sorumludur.

### Yeni Direktifler

**Production Readiness Checklist:**

```markdown
## Pre-Production Validation

### HTML Validation
- [ ] No duplicate IDs
- [ ] All form inputs have labels
- [ ] All images have alt attributes
- [ ] No empty href/src attributes
- [ ] Valid nesting (no div inside p, etc.)

### ARIA Validation
- [ ] No conflicting roles
- [ ] aria-labelledby/describedby references exist
- [ ] aria-controls targets exist
- [ ] No redundant ARIA (button with role="button")
- [ ] aria-live regions present for dynamic content

### TailwindCSS Validation
- [ ] No arbitrary values where design tokens exist
- [ ] Dark mode variants for all color utilities
- [ ] Focus states for all interactive elements
- [ ] Consistent spacing (4px grid)
- [ ] No conflicting utilities

### Alpine.js Validation
- [ ] x-cloak present on x-show elements
- [ ] No memory leaks (cleanup timers/observers)
- [ ] $store mutations in methods only
- [ ] Error boundaries for async operations
- [ ] Loading states for async data

### Performance Validation
- [ ] Images lazy loaded
- [ ] Large lists virtualized (>100 items)
- [ ] Debounced inputs
- [ ] CSS containment for complex components
- [ ] No layout thrashing
```

**Auto-Fix Rules:**

```javascript
const autoFixRules = {
  // HTML fixes
  'missing-alt': (el) => el.alt = el.alt || '',
  'missing-label': (input) => wrapWithLabel(input),
  'duplicate-id': (el) => el.id = `${el.id}-${Date.now()}`,
  
  // ARIA fixes
  'missing-aria-label': (el) => {
    if (el.textContent.trim()) {
      el.setAttribute('aria-label', el.textContent.trim());
    }
  },
  'orphan-aria-describedby': (el) => {
    const id = el.getAttribute('aria-describedby');
    if (!document.getElementById(id)) {
      el.removeAttribute('aria-describedby');
    }
  },
  
  // Tailwind fixes
  'missing-focus-ring': (el) => {
    el.classList.add('focus:ring-2', 'focus:ring-offset-2', 'focus:ring-blue-500');
  },
  'missing-dark-variant': (el) => {
    // Analyze light mode classes and add dark variants
  },
  
  // Alpine.js fixes
  'missing-x-cloak': (el) => {
    if (el.hasAttribute('x-show')) {
      el.setAttribute('x-cloak', '');
    }
  }
};
```

**Validation Error Severity Levels:**
- **Critical (🔴):** Breaks functionality or accessibility completely
- **Major (🟠):** Significant UX/accessibility impact
- **Minor (🟡):** Best practice violations
- **Info (🔵):** Suggestions for improvement

### TODO List

- [ ] ESLint plugin for Alpine.js patterns
- [ ] Stylelint rules for Tailwind best practices
- [ ] HTML validator with custom rules
- [ ] ARIA validator integration
- [ ] Auto-fix CLI tool
- [ ] Pre-commit hook setup
- [ ] CI/CD validation pipeline
- [ ] Bundle size analyzer

### Critical Auto-Fixes (Always Apply)
1. Add `x-cloak` to elements with `x-show`
2. Add `role="alert"` to error messages
3. Add `aria-live="polite"` to dynamic content regions
4. Add `tabindex="0"` to custom interactive elements
5. Add `type="button"` to non-submit buttons in forms

---

## Visionary Agent Direktifleri

Visionary, reference image analizi yaparak design intent'i anlar.

### Yeni Direktifler

**Visual Pattern Recognition:**

| Pattern | Indicators | Implementation Hint |
|---------|------------|---------------------|
| Data Grid | Headers, rows, columns, sort icons | `role="grid"`, sticky headers |
| Card Layout | Rounded corners, shadows, grouped content | `rounded-lg shadow-md p-6` |
| Modal | Centered, backdrop, close button | `fixed inset-0 flex items-center justify-center` |
| Sidebar | Left-aligned, icons + labels, collapsible | `fixed left-0 w-64 h-screen` |
| Tabs | Horizontal buttons, underline/pill active | `role="tablist"`, border-b indicator |
| Form | Stacked labels + inputs, submit button | `space-y-4`, fieldset grouping |
| Toast | Floating, corner positioned, icon + text | `fixed top-4 right-4 z-50` |
| Timeline | Vertical line, dots, alternating cards | `before:absolute before:left-3 before:w-px` |

**Design Token Extraction:**
```yaml
extracted_tokens:
  colors:
    primary: [detected hex]
    secondary: [detected hex]
    background: [detected hex]
    text: [detected hex]
  spacing:
    base: [detected px]
    section: [detected px]
  radius:
    small: [detected px]
    medium: [detected px]
    large: [detected px]
  shadows:
    depth: [none|sm|md|lg|xl]
```

**Component State Detection:**
- **Default:** Normal appearance
- **Hover:** Color change, shadow increase, scale
- **Focus:** Ring, outline, border change
- **Active/Pressed:** Darker shade, inset shadow
- **Disabled:** Opacity reduction, grayscale
- **Selected:** Background fill, checkmark, border
- **Error:** Red border/text
- **Loading:** Skeleton, spinner, pulse

### TODO List

- [ ] Color palette extraction algorithm
- [ ] Component boundary detection
- [ ] Interactive state inference
- [ ] Spacing grid detection
- [ ] Typography scale detection
- [ ] Icon style detection (outline, filled, duotone)
- [ ] Shadow depth estimation
- [ ] Animation/transition detection from sequences

### Reference Image Analysis Template
```markdown
## Visual Analysis Report

### Layout Structure
- [ ] Grid system: [12-col | flex | custom]
- [ ] Container max-width: [detected]
- [ ] Gutter/gap: [detected]

### Color Palette
- Primary: [hex]
- Secondary: [hex]  
- Accent: [hex]
- Background: [hex]
- Surface: [hex]
- Text primary: [hex]
- Text secondary: [hex]

### Typography
- Heading font: [detected]
- Body font: [detected]
- Base size: [px]
- Scale ratio: [1.2 | 1.25 | 1.333]

### Components Identified
1. [Component Name] - [location in image]
   - Estimated classes: [...]
   - States visible: [...]
```

---

## Universal Anti-Patterns (Tüm Agentlar)

### Kesinlikle Kaçınılacaklar

1. **Accessibility**
   - ❌ `outline: none` without replacement
   - ❌ `tabindex > 0`
   - ❌ Color as only indicator
   - ❌ Auto-playing media
   - ❌ Placeholder as label

2. **Performance**
   - ❌ Scroll event without throttle
   - ❌ `getBoundingClientRect()` in scroll handlers
   - ❌ Uncleaned observers/listeners
   - ❌ Eager loading all images
   - ❌ Synchronous blocking scripts

3. **State Management**
   - ❌ Deeply nested reactive objects
   - ❌ Direct DOM manipulation in Alpine.js
   - ❌ Global state for local data
   - ❌ Missing error handling for async

4. **Styling**
   - ❌ `z-index: 9999` (use scale)
   - ❌ `!important` overuse
   - ❌ Inline styles with Tailwind
   - ❌ Missing dark mode variants

---

## Örnek Kod Patterns (Pseudocode)

### Enterprise Data Grid Skeleton
```html
<div 
  x-data="dataGrid()" 
  role="grid" 
  :aria-rowcount="totalRows"
  :aria-colcount="columns.length"
  aria-label="[Grid Title]"
  @keydown="handleKeydown"
  class="overflow-auto max-h-[600px] relative"
>
  <!-- Live region for announcements -->
  <div aria-live="polite" class="sr-only" x-text="announcement"></div>
  
  <!-- Header -->
  <div role="rowgroup" class="sticky top-0 z-10 bg-white dark:bg-gray-800">
    <div role="row" aria-rowindex="1">
      <template x-for="(col, i) in columns" :key="col.key">
        <div 
          role="columnheader" 
          :aria-colindex="i + 1"
          :aria-sort="getSortDirection(col.key)"
          @click="sort(col.key)"
          class="px-4 py-2 text-left font-medium cursor-pointer hover:bg-gray-50"
        >
          <span x-text="col.label"></span>
          <span x-show="sortColumn === col.key" aria-hidden="true">
            <!-- Sort icon -->
          </span>
        </div>
      </template>
    </div>
  </div>
  
  <!-- Body with virtual scrolling -->
  <div 
    role="rowgroup" 
    class="relative" 
    :style="{ height: totalHeight + 'px' }"
    @scroll.throttle.50ms="onScroll"
  >
    <template x-for="row in visibleRows" :key="row.id">
      <div 
        role="row"
        :aria-rowindex="row.index + 2"
        :aria-selected="selectedRows.has(row.id)"
        :style="{ position: 'absolute', top: (row.index * rowHeight) + 'px' }"
        @click="selectRow(row.id, $event)"
        class="flex hover:bg-gray-50 data-[selected=true]:bg-blue-50"
        :data-selected="selectedRows.has(row.id)"
      >
        <template x-for="(col, i) in columns" :key="col.key">
          <div 
            role="gridcell" 
            :aria-colindex="i + 1"
            :tabindex="isActiveCell(row.index, i) ? 0 : -1"
            class="px-4 py-2 truncate"
            x-text="row[col.key]"
          ></div>
        </template>
      </div>
    </template>
  </div>
</div>
```

### Accessible Modal Pattern
```html
<div x-data="{ open: false }">
  <!-- Trigger -->
  <button @click="open = true" aria-haspopup="dialog">Open Modal</button>
  
  <!-- Modal -->
  <template x-teleport="body">
    <div 
      x-show="open"
      x-trap.noscroll.inert="open"
      @keydown.escape.window="open = false"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      class="fixed inset-0 z-50 flex items-center justify-center"
    >
      <!-- Backdrop -->
      <div 
        @click="open = false"
        class="absolute inset-0 bg-black/50 backdrop-blur-sm"
        aria-hidden="true"
      ></div>
      
      <!-- Panel -->
      <div 
        x-show="open"
        x-transition:enter="ease-out duration-300"
        x-transition:enter-start="opacity-0 scale-95"
        x-transition:enter-end="opacity-100 scale-100"
        class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full mx-4"
      >
        <h2 id="modal-title" class="text-lg font-semibold p-4">Modal Title</h2>
        <div class="p-4"><!-- Content --></div>
        <div class="flex justify-end gap-2 p-4 border-t">
          <button @click="open = false">Cancel</button>
          <button>Confirm</button>
        </div>
      </div>
    </div>
  </template>
</div>
```

---

## Sonuç ve Öncelik Sırası

Her agent için en kritik TODO'lar:

1. **Strategist:** Complexity tier sistemi ve bağımlılık grafiği
2. **Architect:** ARIA checklist ve keyboard nav şablonları  
3. **Alchemist:** Focus ring standardı ve dark mode coverage
4. **Physicist:** Virtual scrolling template ve $store patterns
5. **Critic:** Automated scoring tool ve accessibility audit
6. **QualityGuard:** Pre-commit validation hook ve auto-fix CLI
7. **Visionary:** Component boundary detection ve token extraction

Bu direktifler uygulandığında, sistem **WCAG 2.1 AA compliant**, **performanslı** ve **enterprise-grade** UI komponentleri üretebilecektir.