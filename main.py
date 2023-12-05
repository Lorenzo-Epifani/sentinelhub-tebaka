# Utilities
import json
import utils as U
from os.path import join as join_pth
import shutil
from sentinelhub import (
    DataCollection,
    BBox,
    bbox_to_dimensions,
    CRS,
)
from pathlib import Path


# SAVE FOLDER NAME ####################
SAVE_ROOT="./orthos"
Path(SAVE_ROOT).mkdir(parents=True, exist_ok=True)

#########################

# TARGET INFO ###################à
f = open('./request_meta.json')
request_meta = json.load(f)
f.close()
#########################
center = request_meta["target"]["center"]
ofs = request_meta["target"]["ofs"]
resolution = request_meta["res"]
bands = request_meta["bands"]

time_int_dtt = U.list_to_dtt(request_meta["time_interval"])

day_skip = request_meta["day_skip"]
aoi_coords_wgs84 = [center[0]-ofs, center[1]-ofs, center[0]+ofs, center[1]+ofs]
aoi_bbox = BBox(bbox=aoi_coords_wgs84, crs=CRS.WGS84)
aoi_size = bbox_to_dimensions(aoi_bbox, resolution=resolution)
center_hash = U.hash_list(center)
SAVE_ROOT=f'{SAVE_ROOT}/{center_hash}'

shutil.copy('./request_meta.json', SAVE_ROOT)

#DON T EXCEED 2500 DIMENSION
print(f"Image shape at {resolution} m resolution: {aoi_size} pixels")
aoi_bbox = BBox(bbox=aoi_coords_wgs84, crs=CRS.WGS84)
##################################################
# REQUEST CATALOG USING CREDENTIALS
catalog,config = U.get_catalog()
##################################################
# SEARCH AVAIABLE ##################################################
search_iterator = catalog.search(
    DataCollection.SENTINEL2_L2A,
    bbox=aoi_bbox,
    time=U.dtt_to_iso(time_int_dtt),
    fields={"include": ["id", "properties.datetime"], "exclude": []},
)

results = list(search_iterator)
#print("Total number of results:", len(results))
####################################################################################################

# DOWNLOAD ORTHOS ##################################################
time_windows = U.get_time_windows(time_int_dtt, day_skip)
for window in time_windows:
    for band in bands:
        U.download_ortho(config, aoi_bbox, aoi_size, window, SAVE_ROOT=SAVE_ROOT )
####################################################################################################

