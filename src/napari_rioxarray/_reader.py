"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/plugins/guides.html?#readers
"""
from pathlib import Path
from typing import Callable, List, Sequence, Union

from napari.types import LayerData
from rasterio.drivers import raster_driver_extensions

supported_raster_extensions = raster_driver_extensions().keys()

PathLike = str
PathOrPaths = Union[PathLike, Sequence[PathLike]]
ReaderFunction = Callable[[PathOrPaths], List[LayerData]]


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not Path(path).suffix.lower().strip(".") in supported_raster_extensions:
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    from xarray import DataArray, open_dataarray, open_mfdataset

    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    # load all files into array
    # todo look at dask https://napari.org/tutorials/processing/dask.html
    if len(paths) == 1:
        data: DataArray = open_dataarray(paths[0], engine="rasterio")
    else:
        # todo test with a mspec observation
        data = open_mfdataset(paths, engine="rasterio", concat_dim="band", combine="nested").to_array()
    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {"name": data.name}
    return [(data, add_kwargs, "image")]
