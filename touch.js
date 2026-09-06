
/* Production safety guard: never allow an empty blocking panel on initial mobile load. */
window.addEventListener('pageshow',()=>{
  try{
    if(innerWidth<=760){
      document.querySelectorAll('.panel.show').forEach(p=>p.classList.remove('show'));
      document.querySelectorAll('.menuBtn.active').forEach(b=>b.classList.remove('active'));
    }
    /* Old lite-build save is intentionally ignored by the full build. */
    localStorage.removeItem('captainsDash.v07.prod');
  }catch(e){}
});
window.__CAPTAINS_DASH_BUILD__='FULL-v0.7.1';
