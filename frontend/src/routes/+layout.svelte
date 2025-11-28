<script lang="ts">
 import * as Sidebar from "$lib/components/ui/sidebar/index.js";
 import { ModeWatcher } from "mode-watcher";
 import AppSidebar from "$lib/components/app-sidebar.svelte";
 import "../app.css"
 
 let { children } = $props();
</script>
 <ModeWatcher></ModeWatcher>
<Sidebar.Provider>
 <AppSidebar />
 <main>
  <Sidebar.Trigger />
  {@render children?.()}
 </main>
</Sidebar.Provider>
