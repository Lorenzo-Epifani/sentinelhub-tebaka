import json
from os.path import join as join_pth
from sentinelhub import SHConfig,SentinelHubCatalog,SentinelHubRequest,DataCollection,MimeType
import evalscripts as evs
import skimage.exposure as skie
import datetime
import hashlib
from PIL import Image  
from pathlib import Path


def get_catalog():
    f = open('./credentials.json')
    cred = json.load(f)
    config = SHConfig()
    config.sh_client_id = cred['client_id']
    config.sh_client_secret = cred['client_secret']
    config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    config.sh_base_url = "https://sh.dataspace.copernicus.eu"
    config.save("cdse")
    #config = SHConfig("cdse")
    catalog = SentinelHubCatalog(config=config)
    return catalog,config

def download_array_bands(config, aoi_bbox, aoi_size, time_interval, SAVE_ROOT,
                   bands = "rgb"):
    script,mime_type,save_function=evs.api_middleware(bands)
    Path(join_pth(SAVE_ROOT,bands)).mkdir(parents=True, exist_ok=True)
    request_array_bands = SentinelHubRequest(
        data_folder=SAVE_ROOT,
        evalscript=script,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    name="s2l2a", service_url="https://sh.dataspace.copernicus.eu"
                ),
                time_interval=time_interval,
                other_args={"dataFilter": {"mosaickingOrder": "leastCC"}} #minime nuvole
            )
        ],
        responses=[SentinelHubRequest.output_response("default",mime_type)],
        bbox=aoi_bbox,
        size=aoi_size,
        config=config,
    )
    print("DOWNLOADING IMAGE FOR THE INTERVAL: ")
    print(time_interval)
    result_array_bands = request_array_bands.get_data(save_data=False)[0]
    save_function(result_array_bands,SAVE_ROOT,time_interval)



    #SHOW WITH CORRECTION
    
    #plt.imshow(image)
    #plt.savefig('./myfilename.png')
    #plt.show()
    return request_array_bands


def get_time_windows(time_interval,day_skip):
    start,end = time_interval 
    i=0
    slots=[]
    while start+datetime.timedelta(days=(i+1)*day_skip) < end:
        slots.append(tuple([(start+datetime.timedelta(days=(i+k)*day_skip)).date().isoformat() for k in [0,1]]))
        #slots.append((start+datetime.timedelta(days=i*day_skip),start+datetime.timedelta(days=(i+1)*day_skip)))
        i+=1
    return slots
    #print("Monthly time windows:\n")
    #for slot in slots:
    #    print(slot)

def list_to_dtt(interval):
    return [datetime.datetime(*el) for el in interval]

def dtt_to_iso(interval):
    return [el.date().isoformat() for el in interval]
#testint = [[2022,12,1], [2023,12,20]]
#get_time_windows(testint,10)
def hash_list(tup):
    m = hashlib.md5()
    for s in tup:
        m.update(str(s).encode())
    fn = m.hexdigest() # => 'd16fb36f0911f878998c136191af705e'
    return fn