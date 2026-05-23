<script lang="ts">
 import { onMount } from "svelte";
 import { Button } from "$lib/components/ui/button";
 import { Input } from "$lib/components/ui/input";
 import { Separator } from "$lib/components/ui/separator";
 import { Skeleton } from "$lib/components/ui/skeleton";
 import CircleAlertIcon from "@lucide/svelte/icons/circle-alert";
 import PencilIcon from "@lucide/svelte/icons/pencil";
 import PlusIcon from "@lucide/svelte/icons/plus";
 import RotateCwIcon from "@lucide/svelte/icons/rotate-cw";
 import SearchIcon from "@lucide/svelte/icons/search";
 import Trash2Icon from "@lucide/svelte/icons/trash-2";
 
 const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
 
 type Category = {
  id: number;
  name: string;
 };
 
 type MenuItem = {
  id: number;
  name: string;
  description?: string | null;
  price: number;
  tags?: string[] | null;
  active: boolean;
  category_id?: number | null;
 };
 
 const skeletonCards = Array.from({ length: 6 }, (_, index) => index);
 
 let menuItems = $state<MenuItem[]>([]);
 let categories = $state<Category[]>([]);
 let isLoading = $state(true);
 let isSaving = $state(false);
 let errorMessage = $state<string | null>(null);
 let formError = $state<string | null>(null);
 let searchTerm = $state("");
 let editingId = $state<number | null>(null);
 
 let name = $state("");
 let description = $state("");
 let price = $state("");
 let tagsInput = $state("");
 let active = $state(true);
 let categoryId = $state("");
 
 const filteredItems = $derived.by(() => {
  const term = searchTerm.trim().toLowerCase();
  if (!term) return menuItems;
  return menuItems.filter((item) => {
   return (
    item.name.toLowerCase().includes(term) ||
    (item.description ?? "").toLowerCase().includes(term)
   );
  });
 });
 
 const categoryLookup = $derived.by(
  () => new Map(categories.map((category) => [category.id, category.name]))
 );
 
 onMount(() => {
  loadData();
 });
 
 const formatPrice = (value: number) =>
  new Intl.NumberFormat("en-US", {
   style: "currency",
   currency: "USD",
  }).format(value);
 
 async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
   throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
 }
 
 async function requestJson<T>(path: string, options: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
   headers: { "Content-Type": "application/json" },
   ...options,
  });
  if (!response.ok) {
   throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
 }
 
 async function loadData() {
  isLoading = true;
  errorMessage = null;
  try {
   const [items, categoryList] = await Promise.all([
    fetchJson<MenuItem[]>("/menu_items/"),
    fetchJson<Category[]>("/categories/"),
   ]);
   menuItems = Array.isArray(items) ? items : [];
   categories = Array.isArray(categoryList) ? categoryList : [];
  } catch (error) {
   errorMessage =
    "We couldn't load the menu items. Please check the backend connection and try again.";
   menuItems = [];
   categories = [];
  } finally {
   isLoading = false;
  }
 }
 
 function resetForm() {
  editingId = null;
  name = "";
  description = "";
  price = "";
  tagsInput = "";
  active = true;
  categoryId = "";
  formError = null;
 }
 
 function startEdit(item: MenuItem) {
  editingId = item.id;
  name = item.name;
  description = item.description ?? "";
  price = Number.isFinite(item.price) ? item.price.toString() : "";
  tagsInput = item.tags?.join(", ") ?? "";
  active = item.active ?? true;
  categoryId = item.category_id ? String(item.category_id) : "";
  formError = null;
 }
 
 function parseTags(value: string) {
  return value
   .split(",")
   .map((tag) => tag.trim())
   .filter(Boolean);
 }
 
 function validateForm() {
  if (!name.trim()) {
   return "Menu item name is required.";
  }
  if (!price || Number.isNaN(Number(price))) {
   return "Enter a valid price for this item.";
  }
  if (!categoryId) {
   return "Select a category for this item.";
  }
  return null;
 }
 
 async function saveItem() {
  const validationError = validateForm();
  if (validationError) {
   formError = validationError;
   return;
  }
  formError = null;
  isSaving = true;
  try {
   const payload = {
    name: name.trim(),
    description: description.trim() ? description.trim() : null,
    price: Number(price),
    tags: parseTags(tagsInput),
    active,
    category_id: Number(categoryId),
    modifier_ids: [],
   };
   if (editingId) {
    await requestJson(`/menu_items/${editingId}`, {
     method: "PUT",
     body: JSON.stringify(payload),
    });
   } else {
    await requestJson("/menu_items/", {
     method: "POST",
     body: JSON.stringify(payload),
    });
   }
   resetForm();
   await loadData();
  } catch (error) {
   formError =
    "We couldn't save this menu item. Please check the details and try again.";
  } finally {
   isSaving = false;
  }
 }
 
 async function deleteItem(item: MenuItem) {
  if (!item?.id) return;
  const confirmed = window.confirm(`Delete "${item.name}" from the menu?`);
  if (!confirmed) return;
  try {
   await requestJson(`/menu_items/${item.id}`, { method: "DELETE" });
   if (editingId === item.id) {
    resetForm();
   }
   await loadData();
  } catch (error) {
   errorMessage =
    "We couldn't delete that menu item. Please refresh and try again.";
  }
 }
 </script>
 
 <svelte:head>
 <title>Menu Management | BeanThere POS</title>
 </svelte:head>
 
 <div class="flex min-h-screen w-full flex-col gap-6 p-6">
 <header class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
  <div class="space-y-1">
   <p class="text-sm font-medium text-muted-foreground">BeanThere POS</p>
   <h1 class="text-3xl font-semibold tracking-tight">Menu management</h1>
   <p class="text-sm text-muted-foreground">
    Create, edit, and retire menu items for the POS.
   </p>
  </div>
  <div class="flex flex-wrap items-center gap-2">
   <Button variant="outline" class="gap-2" onclick={loadData} disabled={isLoading}>
    <RotateCwIcon class="size-4" />
    Refresh
   </Button>
   <Button variant="outline" class="gap-2" onclick={resetForm} disabled={isSaving}>
    <PlusIcon class="size-4" />
    New item
   </Button>
  </div>
 </header>
 
 {#if errorMessage}
  <div
   class="flex items-start gap-3 rounded-lg border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive"
  >
   <CircleAlertIcon class="mt-0.5 size-4" />
   <div class="space-y-1">
    <p class="font-medium">Something went wrong</p>
    <p>{errorMessage}</p>
   </div>
  </div>
 {/if}
 
 <section class="grid gap-6 xl:grid-cols-[minmax(0,360px)_minmax(0,1fr)]">
  <div class="flex flex-col gap-4 rounded-lg border bg-card p-4 shadow-sm">
   <div class="space-y-1">
    <p class="text-sm font-medium text-muted-foreground">
     {editingId ? "Editing menu item" : "Create a new item"}
    </p>
    <h2 class="text-lg font-semibold">
     {editingId ? "Update menu item" : "Menu item details"}
    </h2>
   </div>
   <Separator />
   <form class="flex flex-col gap-4" on:submit|preventDefault={saveItem}>
    <div class="space-y-2">
     <label class="text-sm font-medium">Name</label>
     <Input placeholder="Vanilla latte" bind:value={name} disabled={isSaving} />
    </div>
    <div class="space-y-2">
     <label class="text-sm font-medium">Description</label>
     <textarea
      class="border-input bg-background ring-offset-background placeholder:text-muted-foreground shadow-xs min-h-[96px] w-full rounded-md border px-3 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]"
      placeholder="Add a short description"
      bind:value={description}
      disabled={isSaving}
     ></textarea>
    </div>
    <div class="grid gap-4 sm:grid-cols-2">
     <div class="space-y-2">
      <label class="text-sm font-medium">Price</label>
      <Input
       type="number"
       min="0"
       step="0.01"
       placeholder="4.50"
       bind:value={price}
       disabled={isSaving}
      />
     </div>
     <div class="space-y-2">
      <label class="text-sm font-medium">Category</label>
      <select
       class="border-input bg-background ring-offset-background placeholder:text-muted-foreground shadow-xs flex h-9 w-full rounded-md border px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]"
       bind:value={categoryId}
       disabled={isSaving || categories.length === 0}
      >
       <option value="">Select a category</option>
       {#each categories as category}
        <option value={category.id}>{category.name}</option>
       {/each}
      </select>
      {#if categories.length === 0 && !isLoading}
       <p class="text-xs text-muted-foreground">
        Create a category in the admin backend before adding items.
       </p>
      {/if}
     </div>
    </div>
    <div class="space-y-2">
     <label class="text-sm font-medium">Tags</label>
     <Input
      placeholder="cold, seasonal, oat milk"
      bind:value={tagsInput}
      disabled={isSaving}
     />
     <p class="text-xs text-muted-foreground">Separate tags with commas.</p>
    </div>
    <label class="flex items-center gap-2 text-sm font-medium">
     <input
      type="checkbox"
      class="border-input text-primary shadow-xs size-4 rounded"
      bind:checked={active}
      disabled={isSaving}
     />
     Item is active
    </label>
    {#if formError}
     <div
      class="rounded-lg border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive"
     >
      {formError}
     </div>
    {/if}
    <div class="flex flex-wrap gap-2">
     <Button type="submit" class="gap-2" disabled={isSaving}>
      <PlusIcon class="size-4" />
      {editingId ? "Save changes" : "Add to menu"}
     </Button>
     {#if editingId}
      <Button type="button" variant="outline" onclick={resetForm} disabled={isSaving}>
       Cancel
      </Button>
     {/if}
    </div>
   </form>
  </div>
 
  <div class="flex flex-col gap-4">
   <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
    <div class="space-y-1">
     <h2 class="text-lg font-semibold">Menu items</h2>
     <p class="text-sm text-muted-foreground">
      {filteredItems.length} items matching your filters.
     </p>
    </div>
    <div class="relative w-full lg:max-w-sm">
     <SearchIcon
      class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
     />
     <Input placeholder="Search items..." class="pl-9" bind:value={searchTerm} />
    </div>
   </div>
 
   <Separator />
 
   <section class="grid gap-4 sm:grid-cols-2">
    {#if isLoading}
     {#each skeletonCards as skeleton}
      <div class="flex flex-col gap-3 rounded-lg border bg-card p-4 shadow-sm">
       <Skeleton class="h-5 w-28" />
       <Skeleton class="h-4 w-full" />
       <Skeleton class="h-4 w-2/3" />
       <div class="flex items-center justify-between">
        <Skeleton class="h-6 w-16" />
        <Skeleton class="h-8 w-20" />
       </div>
      </div>
     {/each}
    {:else}
     {#each filteredItems as item (item.id)}
      <div class="flex h-full flex-col gap-3 rounded-lg border bg-card p-4 shadow-sm">
       <div class="flex items-start justify-between gap-3">
        <div>
         <p class="text-lg font-semibold">{item.name}</p>
         <p class="text-sm text-muted-foreground">
          {item.description ?? "No description available."}
         </p>
        </div>
        <span class="text-sm font-semibold">{formatPrice(item.price)}</span>
       </div>
       <div class="flex flex-wrap items-center gap-2 text-xs">
        <span
         class={`rounded-full border px-2 py-0.5 ${
          item.active
           ? "border-emerald-200 bg-emerald-50 text-emerald-700"
           : "border-amber-200 bg-amber-50 text-amber-700"
         }`}
        >
         {item.active ? "Active" : "Inactive"}
        </span>
        {#if item.category_id}
         <span class="rounded-full border border-muted px-2 py-0.5 text-muted-foreground">
          {categoryLookup.get(item.category_id) ?? `Category ${item.category_id}`}
         </span>
        {/if}
       </div>
       {#if item.tags?.length}
        <div class="flex flex-wrap gap-2">
         {#each item.tags as tag}
          <span
           class="rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground"
          >
           {tag}
          </span>
         {/each}
        </div>
       {/if}
       <div class="mt-auto flex flex-wrap items-center gap-2">
        <Button
         variant="outline"
         size="sm"
         class="gap-2"
         onclick={() => startEdit(item)}
        >
         <PencilIcon class="size-4" />
         Edit
        </Button>
        <Button
         variant="outline"
         size="sm"
         class="gap-2 text-destructive hover:text-destructive"
         onclick={() => deleteItem(item)}
        >
         <Trash2Icon class="size-4" />
         Delete
        </Button>
       </div>
      </div>
     {/each}
     {#if filteredItems.length === 0}
      <div
       class="col-span-full rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground"
      >
       No menu items match your search.
      </div>
     {/if}
    {/if}
   </section>
  </div>
 </section>
 </div>
