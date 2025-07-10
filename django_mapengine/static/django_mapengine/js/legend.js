
const layerCheckboxes = document.querySelectorAll('.mapengine_layer');
const legend   = document.getElementById('legend');
const openBtn  = document.getElementById('open-btn');
const closeBtn = document.getElementById('close-btn');

closeBtn.addEventListener('click', () => {
  legend.classList.add('hidden');
  openBtn .classList.remove('hidden');
});

openBtn.addEventListener('click', () => {
  legend.classList.remove('hidden');
  openBtn .classList.add('hidden');
});

layerCheckboxes.forEach(checkbox => {
  console.log(checkbox);
  checkbox.addEventListener('change', () => {
    console.log(checkbox.checked);
    const layerName = checkbox.getAttribute('data-layer-name');
    console.log(layerName);
    if (checkbox.checked) {
      turn_on_layer(layerName);
    } else {
      turn_off_layer(layerName);
    }
  });
});
