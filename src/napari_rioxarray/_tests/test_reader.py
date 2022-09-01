import importlib.resources

from napari_rioxarray import napari_get_reader

from . import data


# tmp_path is a pytest fixture
def test_reader(tmp_path):
    """An example of how you might test your plugin."""

    with importlib.resources.path(data, "S2A_MSIL1C_20170102T111442_N0204_R137_T30TXT_20170102T111441_TCI_cloudoptimized_512_200m.tif") as my_test_file:
        # try to read it back in
        my_test_file = str(my_test_file.absolute())
        reader = napari_get_reader(my_test_file)
        assert callable(reader)
        # make sure we're delivering the right format
        layer_data_list = reader(my_test_file)
        assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
        layer_data_tuple = layer_data_list[0]
        assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0


def test_get_reader_pass():
    reader = napari_get_reader("fake.filefakefakefake")
    assert reader is None
