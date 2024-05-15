In order to enable popups for your layers you have to define them in the settings using `MAP_ENGINE_POPUPS` parameter.
For each layer in your map you can add a popup which is shown when clicking on the layer.
To set up a popup for a layer you must use `Popup` dataclass from `django_mapengine.setup`. 
There you define to which layer the popup belongs. 
In order to enable popups for choropleths, which are layered over an existing layer (see section about [choropleths](./CHOROPLETHS.md)),
you can use attribute `choropleths` to give a list of existing choropleths which should have popups. 
In order to deactivate popup for layer itself (enabled by default when setting up a popup), you must set `popup_at_default_layer=False`.  

NOTE: Order of popups defined under `MAP_ENGINE_POPUPS` matters! If two layers are overlapping, only first popup in list will show up.

Once, popups are defined in settings, each time a user clicks on a layer and a popup event is fired, a backend call is made to
`popup/<str:lookup>/<int:region>` holding the layer ID (or choropleth ID respectively) as `lookup` and clicked feature ID as `region`.
Additionally, all parameters stored in frontend JS in variable `map_store.cold.state` are transferred to backend as well and can be received via `map_state = request.GET.dict()`.
You can make use of this map state variable in your project in order to send additional information to backend, which can be used to customize popups depending on that information.

From there, you can handle popup creation as you like, you only must return HTML at the end, which will be rendered within a popup modal.
Nevertheless, you could use base classes from `django_mapengine.popups` as a starting point for your popups, which are holding basic functionality for
initializing parameters and are offering a simple template system.