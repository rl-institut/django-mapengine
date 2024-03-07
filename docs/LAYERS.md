# Layers
## Toggling layers
In your django project you can create inputs which get connected automatically connected to a layer in order to switch this layer on and off.
To do so, you have to create an `input` of `type` "checkbox" with an `id` which is related to layer ID you want to trigger:

```html
<input id="wind" type="checkbox">
```

Triggering (changing) this input will toggle all layers starting with "wind".
This guarantees that also clustered layers (in this example "wind", "wind_cluster" and "wind_cluster_count") are triggered. 