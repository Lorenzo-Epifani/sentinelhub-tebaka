# request_meta.json format
```json
{
    "target":{
        "center":[16.117562814594123, 41.03264440053801], //center of the target area
        "ofs":0.1 //height and width of the area, in coordinates 
    },
    "res":10, //resolution, 10 is the best available
    "time_interval":[[2021,12,1], [2022,12,20]], //time interval to observe
    "day_skip":5, //smallest window in which you have a single image
    "bands":["rgb"] //bands. TODO: hyper and cms. only support rgb
}
```

