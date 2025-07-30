# Svelte

## Overview
Svelte is a radical new approach to building user interfaces. Whereas traditional frameworks like React and Vue do the bulk of their work in the *browser*, Svelte shifts that work into a *compile step* that happens when you build your app. Instead of using techniques like virtual DOM diffing, Svelte writes code that surgically updates the DOM when the state of your app changes.

## Core Concepts

### 1. No Virtual DOM
Thisvelte's most defining feature. Svelte is a compiler that converts your declarative component code into efficient, imperative JavaScripthat directly manipulates the DOM. This avoids the overhead of virtual DOM abstraction, leading to smaller bundle sizes and fasteruntime performance.

### 2. Truly Reactive
Reactivity is built into the language itself. State is declared asimple variables, and updates happen automatically when those variables areassigned. There's no need for special functions or hooks to trigger updates.

```html
<script>
  let count = 0;

  function handleClick() {
    count += 1;
  }
</script>

<button:click={handleClick}>
  Clicked {count} {count === 1 ? 'time' : 'times'}
</button>
```
In this example, simply reassigning `count` will cause the DOM to update automatically.

### 3. Single-File Componentsimilar to Vue, Svelte uses a `.svelte` file formathat encapsulates a component'structure, logic, and styling in a single, easy-to-read file.

```html
<script>
  // component logic
</script>

<template>
  <!-- markup -->
</template>

<style>
  /* styles */
</style>
```

### 4. Scoped Styles
CSS inside a `.svelte` component's `<style>` block iscoped to that component by default. This means you can write simple CSS without worrying about it leaking and affecting other components.

### 5. Stores
For state that needs to be shared between multiple components, Svelte provides a simple and powerful state management system called stores. A store isimply an object with a `subscribe` method that allows components to be notified whenever the store value changes.

## Ecosystem & Tooling

### SvelteKit is the official application framework powered by Svelte. It is a full-featured framework for building web applications of all sizes, providing routing, server-side rendering (SSR), static site generation (SSG), and more.
- **Key Features**: Filesystem-based routing, code-splitting, adapters for different deploymentargets (Vercel, Netlify, Node.js), and a modern development experience powered by Vite.

### Svelte Actions are a way to add custom behavior to elements. They are functions that run when an element is created. A common use case is for integrating third-party libraries or for custom event handling.

### Svelte Transitions & Animationsvelte includes a rich set of built-in transition and animation functions that make it easy to create fluid and engaging user interfaces. Because Svelte understands your component structure at compile time, it can create highly optimized and performant animations.

## Why Use Svelte?
- **Less Code**: Svelte allows you to build applications with significantly less boilerplate code compared tother frameworks.
- **Blazing Fast**: The compile-time approach results in highly optimized, vanilla JavaScript, leading to excellent performance and faster load times.
- **True Reactivity**: State management isimple and intuitive, feeling like a natural extension of JavaScript.
- **Lower Barrier to Entry**: The simplicity of Svelte's concepts makes it very approachable for developers who are new to front-end frameworks.
- **Growing Popularity**: Svelte has a passionate and rapidly growing community, and it is being adopted by major companies for production applications.
