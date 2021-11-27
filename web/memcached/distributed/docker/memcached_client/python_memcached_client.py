import pylibmc
mc = pylibmc.Client(["memcachedserver1:11211", 
                     "memcachedserver2:11211"], 
                    binary=True, 
                    behaviors={"tcp_nodelay": True, 
                               "ketama": True,
                               "remove_failed":1,
                               "retry_timeout": 1,
                               "dead_timeout": 60})
mc["ahmed"] = "Hello World"
mc["tek"] = "Hello World"
print (mc["ahmed"])