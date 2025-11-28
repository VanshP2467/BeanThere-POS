
<script lang="ts">
 import SquarePlusIcon from "@lucide/svelte/icons/square-plus";
 import HouseIcon from "@lucide/svelte/icons/house";
 import MenuSquareIcon from "@lucide/svelte/icons/menu-square";
 import ListOrderedIcon from "@lucide/svelte/icons/list-ordered";
 import SettingsIcon from "@lucide/svelte/icons/settings";
 import * as Sidebar from "$lib/components/ui/sidebar/index.js";
 
 // Menu items.
 const items = [
  {
   title: "Home",
   url: "#",
   icon: HouseIcon,
  },
  {
   title: "Menu",
   url: "#",
   icon: MenuSquareIcon,
  },
  {
   title: "New Order",
   url: "#",
   icon: SquarePlusIcon,
  },
  {
   title: "Kitchen Orders",
   url: "#",
   icon: ListOrderedIcon,
  },
  {
   title: "Settings",
   url: "#",
   icon: SettingsIcon,
  },
 ];
</script>
 
<Sidebar.Root collapsible="icon" variant="sidebar">
 <Sidebar.Content>
  <Sidebar.Group>
   <Sidebar.GroupLabel>Application</Sidebar.GroupLabel>
   <Sidebar.GroupContent>
    <Sidebar.Menu>
     {#each items as item (item.title)}
      <Sidebar.MenuItem>
       <Sidebar.MenuButton>
        {#snippet child({ props })}
         <a href={item.url} {...props}>
          <item.icon />
          <span>{item.title}</span>
         </a>
        {/snippet}
       </Sidebar.MenuButton>
      </Sidebar.MenuItem>
     {/each}
    </Sidebar.Menu>
   </Sidebar.GroupContent>
  </Sidebar.Group>
 </Sidebar.Content>
</Sidebar.Root>