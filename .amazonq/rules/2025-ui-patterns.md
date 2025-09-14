# 🎨 2025 UI Patterns (Compact)

## Tailwind 4.0 Essentials
```css
/* Container queries */
.card { @container (min-width: 300px) { @apply grid-cols-2; } }

/* OKLCH colors */
:root { --primary: oklch(0.7 0.15 200); }
.btn { @apply bg-[var(--primary)] text-white px-4 py-2 rounded-lg; }

/* Animations */
.fade-in { @apply animate-[fadeIn_0.3s_ease-out]; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
```

## Alpine.js 3.14+ Patterns
```html
<!-- Reactive component -->
<div x-data="{ open: false, items: [] }" x-init="loadItems()">
  <button @click="open = !open" x-text="open ? 'Close' : 'Open'"></button>
  <div x-show="open" x-transition>
    <template x-for="item in items">
      <div x-text="item.name"></div>
    </template>
  </div>
</div>

<!-- Global store -->
<script>
Alpine.store('app', {
  user: null,
  notifications: [],
  addNotification(msg) { this.notifications.push(msg); }
});
</script>
```

## HTMX 2.0 Patterns
```html
<!-- Form with validation -->
<form hx-post="/api/students/" hx-target="#result">
  <input name="name" hx-validate="blur" required>
  <button type="submit">Save</button>
</form>

<!-- Live updates -->
<div hx-get="/api/stats" hx-trigger="every 30s"></div>

<!-- Infinite scroll -->
<div hx-get="/api/students?page=2" hx-trigger="revealed" hx-swap="afterend"></div>
```

## Component Library
```html
<!-- Student card -->
<div class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all">
  <div class="flex items-center space-x-3">
    <img class="w-12 h-12 rounded-full" src="{{ student.avatar }}">
    <div>
      <h3 class="font-semibold">{{ student.name }}</h3>
      <p class="text-sm text-gray-500">{{ student.class }}</p>
    </div>
  </div>
</div>

<!-- Form field -->
<div class="space-y-1">
  <label class="block text-sm font-medium">Name</label>
  <input class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500">
  <p class="text-xs text-gray-500">Enter full name</p>
</div>

<!-- Button variants -->
<button class="btn-primary">Primary</button>
<button class="btn-secondary">Secondary</button>
<button class="btn-danger">Delete</button>
```

## Responsive Grid
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Auto-responsive cards -->
</div>
```

## Loading States
```html
<div x-show="loading" class="flex justify-center py-8">
  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
</div>
```

## Form Validation
```html
<form x-data="{ errors: {} }" @submit.prevent="validate">
  <input x-model="form.email" :class="errors.email ? 'border-red-500' : 'border-gray-300'">
  <span x-show="errors.email" x-text="errors.email" class="text-red-500 text-sm"></span>
</form>
```

## Dark Mode
```css
@media (prefers-color-scheme: dark) {
  :root { --bg: #1f2937; --text: #f9fafb; }
}
[data-theme="dark"] { --bg: #1f2937; --text: #f9fafb; }
```

## Accessibility
```html
<button aria-label="Close dialog" aria-expanded="false">
<input aria-describedby="help-text" aria-invalid="false">
<div role="alert" aria-live="polite">Error message</div>
```

## Performance
- Use `loading="lazy"` for images
- Debounce search inputs
- Virtual scrolling for large lists
- Intersection Observer for animations
- Web Workers for heavy computations