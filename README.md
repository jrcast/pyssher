# Pyssher

## What is pyssher?

Pyssher is a simple tool based on python3 that allows users to run commands over ssh in multiple clients simultaneously. 


## Getting started

The easiest way to run pyssher is to pull the public docker image

```
docker pull jrcast/pyssher
```

or you can build your own by pulling this repository and running the following:
```
docker build -t pyssher -f Dockerfile .
```

Once you have the image, create a folder and copy over the sshkey files you will be using for all your servers. [see limitations](https://github.com/jrcast/pyssher#current-limitations). 

You can then run pyssher as follows:

```
docker run -ti --rm  -v /PATH-TO-KEYS/:/pyssher/keys jrcast/pyssher -s USER@HOSTNAME:PORT -c 'echo "Greetings from $HOSTNAME"'
```

PORT is optional. Port 22 is assumed by default if you dont specify any. You can also specify more than one server by using the -s/--server runtime argument multiple times. Note that if you do specify more than one server, pyssher will not terminate if only one/some of the servers fail or disconnect. 


## Docker

Releases are automatically built and published to dockerhub: jrcast/sshref



## Current limitations:

1. The sshkey folder must contain ssh keys only. Currently, pyssher doesn't not validate that each files is valid. 
