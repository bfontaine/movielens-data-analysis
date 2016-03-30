# -*- coding: UTF-8 -*-

from .data_importers import Ml100kImporter, Ml1mImporter, Ml10mImporter

def import_data(directory, dataset_format, verbose=False):
    """
    Import data from a movielens dataset located in ``directory``.

    Supported formats:
        * ``ml-100k``: MovieLens 100k dataset
        * ``ml-1m``: MovieLens 1M dataset
        * ``ml-10m``: MovieLens 10M dataset
    """
    fmts = {
        "ml-100k": Ml100kImporter,
        "ml-1m": Ml1mImporter,
        "ml-10m": Ml10mImporter,
    }

    if dataset_format in fmts:
        fmts[dataset_format](directory, verbose=verbose).run()
    else:
        raise NotImplementedError("format '%s'" % dataset_format)
