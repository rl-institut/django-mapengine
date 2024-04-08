# Clusters

## Usage

You can add a clustered layer using data from django model by adding a `ClusterAPI` element
to `MAP_ENGINE_API_CLUSTERS`:
```python
from django_mapengine import setup

MAP_ENGINE_API_CLUSTERS = [
    setup.ClusterAPI("wind", "map", "WindTurbine", properties=["id", "unit_count"]),
]
```

The element consists of following parameters:
- `layer_id`
- `app_name`
- `model_name`
- `properties`
