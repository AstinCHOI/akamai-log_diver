## Log Diver 
Log Diver can see entire edge locations and log lines with googlemap (for akamai internal tool).

![alt text][sample-image]

### Tech  
* nginx
* python3 (flask, gunicorn, gevent, [geventwebsocket])
* javascript (socket.io, jQuery)
* ruby (Akamai Internal Script) 
* bootstrap
 
### run
You can see the GUI, but can't run(submit) without Akamai internal network.
```sh
$ gunicorn --bind 0.0.0.0:8000 wsgi -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --daemon
```

### TODO
* deploy script

[geventwebsocket]: https://bitbucket.org/noppo/gevent-websocket
[sample-image]: https://raw.githubusercontent.com/AstinCHOI/akamai-log_diver/master/sample_image.png
