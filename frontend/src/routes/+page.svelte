<script lang="ts">
import { onMount } from "svelte";
import * as Sheet from "$lib/components/ui/sheet";
import { Button } from "$lib/components/ui/button";
import { Input } from "$lib/components/ui/input";
import { Separator } from "$lib/components/ui/separator";
import { Skeleton } from "$lib/components/ui/skeleton";
import * as Tooltip from "$lib/components/ui/tooltip";
import CircleAlertIcon from "@lucide/svelte/icons/circle-alert";
import MinusIcon from "@lucide/svelte/icons/minus";
import PlusIcon from "@lucide/svelte/icons/plus";
import RotateCwIcon from "@lucide/svelte/icons/rotate-cw";
import SearchIcon from "@lucide/svelte/icons/search";
import ShoppingCartIcon from "@lucide/svelte/icons/shopping-cart";
import TagIcon from "@lucide/svelte/icons/tag";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type Category = {
id: number;
name: string;
};

type MenuItem = {
id?: number;
name: string;
description?: string | null;
price: number;
tags?: string[] | null;
active: boolean;
modifiers?: number[] | null;
category_id?: number | null;
};

type CategoryResponse = {
id?: number;
name?: string;
};

const skeletonCards = Array.from({ length: 6 }, (_, index) => index);

let menuItems = $state<MenuItem[]>([]);
let categories = $state<Category[]>([]);
let isLoading = $state(true);
let errorMessage = $state<string | null>(null);
let searchTerm = $state("");
let activeCategoryId = $state<number | "all">("all");
let cartOpen = $state(false);
let orderItems = $state<Record<number, { item: MenuItem; quantity: number }>>({});

const cartEntries = $derived.by(() => Object.values(orderItems));
const cartCount = $derived.by(() =>
cartEntries.reduce((total, entry) => total + entry.quantity, 0)
);
const cartTotal = $derived.by(() =>
cartEntries.reduce((total, entry) => total + entry.item.price * entry.quantity, 0)
);
const categoryLookup = $derived.by(() =>
new Map(categories.map((category) => [category.id, category.name]))
);
const activeCategoryLabel = $derived.by(() => {
if (activeCategoryId === "all") return "All items";
return categoryLookup.get(activeCategoryId) ?? `Category ${activeCategoryId}`;
});
const filteredItems = $derived.by(() => {
const term = searchTerm.trim().toLowerCase();
return menuItems.filter((item) => {
const matchesTerm =
!term ||
item.name.toLowerCase().includes(term) ||
(item.description ?? "").toLowerCase().includes(term);
const matchesCategory =
activeCategoryId === "all" ||
(typeof item.category_id === "number" && item.category_id === activeCategoryId);
return matchesTerm && matchesCategory;
});
});

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

async function resolveCategories(
items: MenuItem[],
rawCategories: CategoryResponse[]
): Promise<Category[]> {
const withIds = rawCategories
.filter(
(category): category is { id: number; name: string } =>
typeof category.id === "number" && typeof category.name === "string"
)
.map((category) => ({ id: category.id, name: category.name }));
if (withIds.length) {
return withIds;
}

const categoryIds = Array.from(
new Set(
items
.map((item) => item.category_id)
.filter((id): id is number => typeof id === "number")
)
);
if (categoryIds.length === 0) {
return rawCategories
.filter(
(category): category is { name: string } => typeof category.name === "string"
)
.map((category, index) => ({ id: index + 1, name: category.name }));
}

const resolved = await Promise.all(
categoryIds.map(async (id) => {
try {
const data = await fetchJson<{ name?: string }>(`/categories/${id}`);
return { id, name: typeof data.name === "string" ? data.name : `Category ${id}` };
} catch (error) {
return { id, name: `Category ${id}` };
}
})
);
return resolved;
}

async function loadData() {
isLoading = true;
errorMessage = null;
try {
const [items, rawCategories] = await Promise.all([
fetchJson<MenuItem[]>("/menu_items/"),
fetchJson<CategoryResponse[]>("/categories/"),
]);
menuItems = Array.isArray(items) ? items : [];
categories = await resolveCategories(
menuItems,
Array.isArray(rawCategories) ? rawCategories : []
);
} catch (error) {
errorMessage =
"We couldn't load the menu data. Please check the backend connection and try again.";
menuItems = [];
categories = [];
} finally {
isLoading = false;
}
}

function addToOrder(item: MenuItem) {
if (typeof item.id !== "number") return;
const existing = orderItems[item.id];
if (existing) {
orderItems = {
...orderItems,
[item.id]: { ...existing, quantity: existing.quantity + 1 },
};
} else {
orderItems = {
...orderItems,
[item.id]: { item, quantity: 1 },
};
}
cartOpen = true;
}

function updateQuantity(itemId: number | undefined, delta: number) {
if (typeof itemId !== "number") return;
const existing = orderItems[itemId];
if (!existing) return;
const nextQuantity = existing.quantity + delta;
if (nextQuantity <= 0) {
const { [itemId]: _, ...rest } = orderItems;
orderItems = rest;
return;
}
orderItems = { ...orderItems, [itemId]: { ...existing, quantity: nextQuantity } };
}

function clearOrder() {
orderItems = {};
}
</script>

<svelte:head>
<title>BeanThere POS</title>
</svelte:head>

<Tooltip.Provider>
<div class="flex min-h-screen w-full flex-col gap-6 p-6">
<header class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
<div class="space-y-1">
<p class="text-sm font-medium text-muted-foreground">BeanThere POS</p>
<h1 class="text-3xl font-semibold tracking-tight">Order dashboard</h1>
<p class="text-sm text-muted-foreground">
Browse menu items and build a quick order.
</p>
</div>
<div class="flex flex-wrap items-center gap-2">
<Button variant="outline" class="gap-2" onclick={loadData} disabled={isLoading}>
<RotateCwIcon class="size-4" />
Refresh
</Button>
<Button class="gap-2" onclick={() => (cartOpen = true)}>
<ShoppingCartIcon class="size-4" />
Order ({cartCount})
</Button>
</div>
</header>

<section class="flex flex-col gap-4 rounded-lg border bg-card p-4 shadow-sm">
<div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
<div class="relative w-full lg:max-w-sm">
<SearchIcon
class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
/>
<Input placeholder="Search menu items..." class="pl-9" bind:value={searchTerm} />
</div>
<div class="flex flex-wrap gap-2">
<Button
size="sm"
variant={activeCategoryId === "all" ? "default" : "outline"}
onclick={() => (activeCategoryId = "all")}
>
All items
</Button>
{#if categories.length > 0}
{#each categories as category}
<Button
size="sm"
variant={activeCategoryId === category.id ? "default" : "outline"}
onclick={() => (activeCategoryId = category.id)}
>
{category.name}
</Button>
{/each}
{/if}
</div>
</div>

<Separator />
<div class="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
<TagIcon class="size-4" />
<span>{filteredItems.length} items shown</span>
{#if searchTerm}
<span>•</span>
<span>Filtering for “{searchTerm}”</span>
{/if}
{#if activeCategoryId !== "all"}
<span>•</span>
<span>{activeCategoryLabel}</span>
{/if}
</div>
</section>

{#if errorMessage}
<div
class="flex items-start gap-3 rounded-lg border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive"
>
<CircleAlertIcon class="mt-0.5 size-4" />
<div class="space-y-1">
<p class="font-medium">Unable to load menu data</p>
<p>{errorMessage}</p>
<Button variant="outline" size="sm" class="mt-2" onclick={loadData}>
Try again
</Button>
</div>
</div>
{/if}

<section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
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
{#each filteredItems as item (item.id ?? item.name)}
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
<Tooltip.Root>
<Tooltip.Trigger>
<span
class="rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground"
>
{tag}
</span>
</Tooltip.Trigger>
<Tooltip.Content sideOffset={6}>Tag: {tag}</Tooltip.Content>
</Tooltip.Root>
{/each}
</div>
{/if}
<div class="mt-auto flex items-center justify-between">
<Button
variant="outline"
size="sm"
class="gap-2"
onclick={() => addToOrder(item)}
disabled={typeof item.id !== "number"}
>
<PlusIcon class="size-4" />
Add to order
</Button>
{#if typeof item.id === "number" && orderItems[item.id]}
<span class="text-sm text-muted-foreground">
In order: {orderItems[item.id].quantity}
</span>
{/if}
</div>
</div>
{/each}
{#if !isLoading && filteredItems.length === 0}
<div
class="col-span-full rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground"
>
No menu items match your filters.
</div>
{/if}
{/if}
</section>

<Sheet.Root bind:open={cartOpen}>
<Sheet.Content class="flex flex-col gap-4">
<Sheet.Header>
<Sheet.Title>Current order</Sheet.Title>
<Sheet.Description>
Review items before sending them to the kitchen.
</Sheet.Description>
</Sheet.Header>
<Separator />
<div class="flex flex-col gap-4 overflow-auto">
{#if cartEntries.length === 0}
<p class="text-sm text-muted-foreground">
No items added yet. Select a menu item to start an order.
</p>
{:else}
{#each cartEntries as entry}
<div class="flex items-center justify-between gap-4 rounded-lg border p-3">
<div>
<p class="font-medium">{entry.item.name}</p>
<p class="text-sm text-muted-foreground">
{formatPrice(entry.item.price)}
</p>
</div>
<div class="flex items-center gap-2">
<Button
size="icon-sm"
variant="outline"
onclick={() => updateQuantity(entry.item.id, -1)}
>
<MinusIcon class="size-3" />
</Button>
<span class="min-w-[2rem] text-center text-sm font-medium">
{entry.quantity}
</span>
<Button
size="icon-sm"
variant="outline"
onclick={() => updateQuantity(entry.item.id, 1)}
>
<PlusIcon class="size-3" />
</Button>
</div>
</div>
{/each}
{/if}
</div>
<Separator />
<div class="flex items-center justify-between text-sm">
<span class="text-muted-foreground">Total</span>
<span class="text-lg font-semibold">{formatPrice(cartTotal)}</span>
</div>
<Sheet.Footer class="flex flex-col gap-2">
<Button class="w-full" disabled={cartEntries.length === 0}>
Send to kitchen
</Button>
<Button
variant="outline"
class="w-full"
onclick={clearOrder}
disabled={cartEntries.length === 0}
>
Clear order
</Button>
</Sheet.Footer>
</Sheet.Content>
</Sheet.Root>
</div>
</Tooltip.Provider>
