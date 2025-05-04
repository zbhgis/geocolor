"""Main module."""

import ipyleaflet


class Map(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        """Initialize a new Map instance.

        Args:
            center (list, optional): The initial map center [latitude, longitude].
                Defaults to [20, 0].
            zoom (int, optional): Initial zoom level. Defaults to 2.
            height (str, optional): Height of the map widget. Defaults to "600px".
            **kwargs: Additional keyword arguments passed to ipyleaflet.Map.
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="OpenStreetMap"):
        """Add a built-in basemap layer to the map.

        Args:
            basemap (str, optional): Name of the basemap. Available options include
                'OpenStreetMap', 'StamenTerrain', 'EsriSatellite', etc.
                Defaults to "OpenStreetMap".
        """
        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add_layer(layer)

    def add_google_map(self, map_type="ROADMAP"):
        """Add a Google Map tile layer to the map.

        Args:
            map_type (str, optional): Type of Google Map. Valid options are:
                - "ROADMAP"
                - "SATELLITE"
                - "HYBRID"
                - "TERRAIN"
                Defaults to "ROADMAP".
        """
        map_types = {
            "ROADMAP": "m",
            "SATELLITE": "s",
            "HYBRID": "y",
            "TERRAIN": "p",
        }
        map_type = map_types[map_type.upper()]

        url = (
            f"https://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}"
        )
        layer = ipyleaflet.TileLayer(url=url, name="Google Map")
        self.add_layer(layer)

    def add_geojson(self, data, zoom_to_layer=True, hover_style=None, **kwargs):
        """Add a GeoJSON layer to the map.

        Args:
            data (str or dict): Path to a GeoJSON file or a GeoJSON dictionary.
            zoom_to_layer (bool, optional): Whether to zoom the map to the extent of the layer.
                Defaults to True.
            hover_style (dict, optional): Style applied when hovering over features.
                Defaults to {"color": "red", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments passed to ipyleaflet.GeoJSON.
        """
        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "red", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data
        else:
            raise ValueError("Unsupported data type for GeoJSON input.")

        layer = ipyleaflet.GeoJSON(data=geojson, hover_style=hover_style, **kwargs)
        self.add_layer(layer)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_shp(self, data, **kwargs):
        """Add a shapefile to the map.

        Args:
            data (str): Path to a shapefile (.shp).
            **kwargs: Additional keyword arguments passed to add_geojson().
        """
        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """Add a GeoDataFrame to the map.

        Args:
            gdf (geopandas.GeoDataFrame): GeoDataFrame to be added.
            **kwargs: Additional keyword arguments passed to add_geojson().
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """Add vector data to the map.

        Args:
            data (str, dict, or geopandas.GeoDataFrame): Input vector data.
                If string: path to a file.
                If dict: a GeoJSON dictionary.
                If GeoDataFrame: must be a valid geospatial DataFrame.
            **kwargs: Additional keyword arguments passed to appropriate method.
        """
        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Invalid data type")

    def add_layer_control(self):
        """Add a layer control widget to the map for toggling layers."""
        control = ipyleaflet.LayersControl(position="topright")
        self.add_control(control)
