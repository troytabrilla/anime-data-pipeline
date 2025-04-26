import anime_data_pipeline.defs

from dagster.components import definitions, load_defs


@definitions
def defs():
    return load_defs(defs_root=anime_data_pipeline.defs)
