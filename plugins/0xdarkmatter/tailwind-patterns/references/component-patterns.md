# Tailwind Component Patterns

Ready-to-use component patterns with Tailwind CSS.

## Navigation

### Navbar

```html
<nav class="bg-white shadow">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between h-16">
      <!-- Logo -->
      <a href="/" class="text-xl font-bold text-gray-900">Logo</a>

      <!-- Desktop Menu -->
      <div class="hidden md:flex items-center space-x-8">
        <a href="#" class="text-gray-600 hover:text-gray-900">Home</a>
        <a href="#" class="text-gray-600 hover:text-gray-900">Features</a>
        <a href="#" class="text-gray-600 hover:text-gray-900">Pricing</a>
        <a href="#" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          Get Started
        </a>
      </div>

      <!-- Mobile Menu Button -->
      <button class="md:hidden p-2">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>
  </div>
</nav>
```

### Sidebar

```html
<aside class="w-64 bg-gray-900 text-white min-h-screen">
  <div class="p-4">
    <h2 class="text-lg font-semibold mb-4">Dashboard</h2>
    <nav class="space-y-2">
      <a href="#" class="flex items-center px-4 py-2 bg-gray-800 rounded-lg">
        <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
        Home
      </a>
      <a href="#" class="flex items-center px-4 py-2 text-gray-400 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
        <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
        </svg>
        Users
      </a>
    </nav>
  </div>
</aside>
```

## Cards

### Feature Card

```html
<div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
  <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M13 10V3L4 14h7v7l9-11h-7z"/>
    </svg>
  </div>
  <h3 class="text-lg font-semibold text-gray-900 mb-2">Lightning Fast</h3>
  <p class="text-gray-600">Optimized for speed with edge computing and CDN distribution.</p>
</div>
```

### Profile Card

```html
<div class="bg-white rounded-xl shadow-lg overflow-hidden max-w-sm">
  <div class="h-32 bg-gradient-to-r from-blue-500 to-purple-600"></div>
  <div class="relative px-6 pb-6">
    <img src="avatar.jpg" alt="Profile"
         class="w-24 h-24 rounded-full border-4 border-white absolute -top-12">
    <div class="pt-16">
      <h3 class="text-xl font-bold text-gray-900">Jane Doe</h3>
      <p class="text-gray-500">Senior Developer</p>
      <div class="flex gap-4 mt-4">
        <div class="text-center">
          <div class="text-xl font-bold text-gray-900">142</div>
          <div class="text-sm text-gray-500">Posts</div>
        </div>
        <div class="text-center">
          <div class="text-xl font-bold text-gray-900">4.2k</div>
          <div class="text-sm text-gray-500">Followers</div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### Pricing Card

```html
<div class="bg-white rounded-2xl shadow-xl p-8 border-2 border-blue-500 relative">
  <div class="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
    Popular
  </div>
  <h3 class="text-xl font-bold text-gray-900">Pro</h3>
  <div class="mt-4">
    <span class="text-4xl font-bold">$29</span>
    <span class="text-gray-500">/month</span>
  </div>
  <ul class="mt-6 space-y-3">
    <li class="flex items-center text-gray-600">
      <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
      </svg>
      Unlimited projects
    </li>
    <li class="flex items-center text-gray-600">
      <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
      </svg>
      Advanced analytics
    </li>
    <li class="flex items-center text-gray-600">
      <svg class="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
      </svg>
      Priority support
    </li>
  </ul>
  <button class="w-full mt-8 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
    Get Started
  </button>
</div>
```

## Forms

### Login Form

```html
<form class="bg-white rounded-xl shadow-lg p-8 max-w-md mx-auto">
  <h2 class="text-2xl font-bold text-gray-900 mb-6">Welcome back</h2>

  <div class="space-y-4">
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
      <input type="email" id="email"
             class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
             placeholder="you@example.com">
    </div>

    <div>
      <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
      <input type="password" id="password"
             class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
             placeholder="••••••••">
    </div>

    <div class="flex items-center justify-between">
      <label class="flex items-center">
        <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
        <span class="ml-2 text-sm text-gray-600">Remember me</span>
      </label>
      <a href="#" class="text-sm text-blue-600 hover:underline">Forgot password?</a>
    </div>

    <button type="submit"
            class="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
      Sign in
    </button>
  </div>
</form>
```

### Search Input with Button

```html
<div class="flex max-w-lg">
  <input type="text"
         class="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
         placeholder="Search...">
  <button class="px-6 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 transition-colors">
    Search
  </button>
</div>
```

## Lists

### Task List

```html
<ul class="bg-white rounded-xl shadow divide-y">
  <li class="flex items-center px-6 py-4 hover:bg-gray-50">
    <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
    <span class="ml-4 flex-1">Complete project documentation</span>
    <span class="text-sm text-gray-500">Due tomorrow</span>
  </li>
  <li class="flex items-center px-6 py-4 hover:bg-gray-50">
    <input type="checkbox" checked class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
    <span class="ml-4 flex-1 line-through text-gray-400">Review pull requests</span>
    <span class="text-sm text-gray-500">Completed</span>
  </li>
</ul>
```

### User List

```html
<div class="bg-white rounded-xl shadow divide-y">
  <div class="flex items-center px-6 py-4">
    <img src="avatar1.jpg" class="w-10 h-10 rounded-full" alt="User">
    <div class="ml-4 flex-1">
      <h4 class="font-medium text-gray-900">John Smith</h4>
      <p class="text-sm text-gray-500">john@example.com</p>
    </div>
    <span class="px-3 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Active</span>
  </div>
</div>
```

## Alerts/Badges

### Alert Types

```html
<!-- Success -->
<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
  <div class="flex items-center">
    <svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
    </svg>
    <span class="ml-3 text-green-800">Changes saved successfully!</span>
  </div>
</div>

<!-- Error -->
<div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
  <div class="flex items-center">
    <svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
    </svg>
    <span class="ml-3 text-red-800">Error processing your request.</span>
  </div>
</div>

<!-- Warning -->
<div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-r-lg">
  <span class="text-yellow-800">Please review before submitting.</span>
</div>

<!-- Info -->
<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
  <span class="text-blue-800">New features are now available.</span>
</div>
```

### Badges

```html
<!-- Status badges -->
<span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Active</span>
<span class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">Pending</span>
<span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Inactive</span>
<span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">Draft</span>

<!-- Notification badge -->
<div class="relative inline-block">
  <button class="p-2">
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
    </svg>
  </button>
  <span class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">3</span>
</div>
```

## Loading States

### Spinner

```html
<div class="flex items-center justify-center">
  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
</div>
```

### Skeleton

```html
<div class="animate-pulse space-y-4">
  <div class="h-4 bg-gray-200 rounded w-3/4"></div>
  <div class="h-4 bg-gray-200 rounded w-1/2"></div>
  <div class="h-4 bg-gray-200 rounded w-5/6"></div>
</div>
```

### Button Loading

```html
<button class="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg" disabled>
  <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
  </svg>
  Processing...
</button>
```
