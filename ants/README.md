# Ants on a plane!

In this étude we simulate (some of) the behaviour of creatures related to
Langton’s ant. For each ant simulated, a graph of the ants path is generated.

__To run this code, use the following snippet:__

```
python main.py test/i<N>.txt
```
where `N` is the number of the input file.

By default, the program will detect loops and fast-forward the ant's position to the end of the loop, allowing for simulations with an arbitrary number of steps. You can disable this behaviour by using the `-s` option.

You can generate images of the ant's path by specifying a directory to save to, using the `-i` option. This will also disable fast-forwarding.


__Generate images for each ant:__
```
mkdir images
python main.py test/i<N>.txt -i images
```


__Run `python main.py -h` for help:__

```
usage: main.py [-h] [-i IMAGE_DIR] [-s] filename

Simulates the movement of Langton's Ant

positional arguments:
  filename              The file containing ant instructions

options:
  -h, --help            show this help message and exit
  -i IMAGE_DIR, --image_dir IMAGE_DIR
                        The directory to save the output images to. Specifying
                        this option will disable loop detection and fast
                        forwarding.
  -s, --simple          No loop detection and fast forwarding
```
