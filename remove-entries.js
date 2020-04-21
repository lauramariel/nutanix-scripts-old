function removeEntries(){
  // original
  for(var e=document.getElementsByClassName("n-nav-menu-item n-nav-toggle n-main-menu-link"),n=0;n<e.length;)
      {
          let a=e[n].innerText;
          "Dashboard"==a||"Explore"==a||"Alerts"==a ? n++:e[n].parentElement.removeChild(e[n])
      }
  // only show sidebar headings Virtual Infra, Networking, Policies, Administration and Data Recovery
  for (var e=document.getElementsByClassName("entity-type-group"),n=0;n<e.length;)
  {
          let a=e[n].innerText;
          a.includes("VIRTUAL INFRASTRUCTURE")||a.includes("NETWORKING")||a.includes("ADMINISTRATION")||a.includes("DATA RECOVERY") ? n++:e[n].parentElement.removeChild(e[n])
  }
  // only show sidebar items VMs, Images, Virtual Private Cloud, Floating IPs, Categories, Availability Zones, Protection Policies, Recovery Plans and Recoverable Entities
  for (var e=document.getElementsByClassName("selectionItem entity-item -small-detail"),n=0;n<e.length;)
  {
    let a=e[n].innerText;
    a.includes("VMs")||a.includes("Images")||a.includes("Virtual Private Cloud")||a.includes("Floating IPs")||a.includes("Categories")||a.includes("Availability Zones")||a.includes("Protection Policies")||a.includes("Recovery Plans")||a.includes("Recoverable Entities") ? n++:e[n].parentElement.removeChild(e[n])
  }
  };
removeEntries();
var alwaysfixnav=setInterval(removeEntries(),1e3);
