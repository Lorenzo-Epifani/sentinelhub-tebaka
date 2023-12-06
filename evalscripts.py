from sentinelhub import MimeType
import skimage.exposure as skie
from PIL import Image  
from os.path import join as join_pth
from pathlib import Path
#BANDS REFERENCE:
#https://docs.sentinel-hub.com/api/latest/data/sentinel-2-l2a/
ndvi = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04","B08"]
            }],
            output: {
                bands: 3
            }
        };
    }

    function evaluatePixel(sample) {
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04)
        return [sample.B04*0, ndvi , sample.B04*0];
    }
"""
true_color_rgb = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04"]
            }],
            output: {
                bands: 3
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B04, sample.B03, sample.B02];
    }
"""
clm = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04", "CLM"],
    output: { bands: 3 }
  }
}

function evaluatePixel(sample) {
  if (sample.CLM == 1) {
    return [0.75 + sample.B04, sample.B03, sample.B02]
  }
  return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
}
"""

hyper = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"],
                units: "DN"
            }],
            output: {
                bands: 12,
                sampleType: "INT16"
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B01,
                sample.B02,
                sample.B03,
                sample.B04,
                sample.B05,
                sample.B06,
                sample.B07,
                sample.B08,
                sample.B8A,
                sample.B09,
                sample.B11,
                sample.B12];
    }
"""

def api_middleware(key):
    """
    map a tring to evalscript,mimetype and save function
    """
    def sf_rgb(array_bands,SAVE_ROOT,time_interval):
        array_bands = skie.adjust_gamma(array_bands,1.1,3)
        pilim= Image.fromarray(array_bands)
        pilim.save(join_pth(SAVE_ROOT,"rgb",f'{time_interval[0]}_{time_interval[1]}.png'))

    def sf_hyper(array_bands,SAVE_ROOT,time_interval):
        bands = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"]
        for i in range(array_bands.shape[2]):
            save_dir = join_pth(SAVE_ROOT,"hyper",f'{time_interval[0]}_{time_interval[1]}')
            Path(save_dir).mkdir(parents=True, exist_ok=True)
            pilim= Image.fromarray(array_bands[:,:,i])
            pilim.save(join_pth(save_dir,f'{bands[i]}.png'))

    def sf_ndvi(array_bands,SAVE_ROOT,time_interval):
        pilim= Image.fromarray(array_bands)
        pilim.save(join_pth(SAVE_ROOT,"ndvi",f'{time_interval[0]}_{time_interval[1]}.png'))

    def sf_clm():
        pass

    _d={
        "rgb": (true_color_rgb,MimeType.PNG,sf_rgb),
        "clm": (clm,MimeType.TIFF),
        "hyper": (hyper,MimeType.TIFF,sf_hyper),
        "ndvi": (ndvi,MimeType.PNG,sf_ndvi)
    }
    return _d[key]