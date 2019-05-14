from AdcircPy.Model import AdcircMesh
# from AdcircPy.Outputs._OutputFactory import _OutputFactory


def read_mesh(fort14, SpatialReference=4326, vertical_datum=None,
              datum_mesh=None):
    """
    Reads ADCIRC input files.
    -----------
    Parameters:
    -----------
        fort14 (string): Path to fort.14 file.
    -------------------
    Optional arguments:
    -------------------
        fort13 (string): Path to optional fort.13 file.
        datum (string): Mesh vertical datum. Usually 'LMSL'
        SpatialReference (int): Corresponds to epsg projection.
    -------
    returns:
    -------
                                    AdcirPy.Model.AdcircMesh instance.
    """

    return AdcircMesh(fort14, SpatialReference, vertical_datum, datum_mesh)

# def read_output(path, fort14=None, vertical_datum='LSML', epsg=4326, datum_grid=None, fort15=None):
#     """
#     Reads ADCIRC output files and returns the appropriate output type class.
#     Supports ASCII and NetCDF outputs.
#     -----------
#     Parameters:
#     -----------
#             path (str)          : Path to output file.
#     -------------------
#     Optional arguments:
#     -------------------
#             fort14 (str)        : Path to fort.14 file. Required for ASCII gridded field outputs (e.g. maxele).
#                                                         Optional in case of NetCDF files (used for inclusion of boundary data).
#             datum  (string)     : Mesh vertical datum. Usually 'LMSL' or 'NAVD88'.
#             epsg   (int)        : Corresponds to epsg projection. Use 4326 for WGS84 (default)
#             datum_grid (string) : Path to datum conversion grid. Useful when doing HWM validations.
#     -------
#     return:
#     -------
#             AdcirPy.<output>  where <output> is the output type.
#     """
#     return _OutputFactory(path, fort14, vertical_datum, epsg, datum_grid, fort15).get_output_instance()