If you want to try it out on your own you need to have Windows, and have wsl installed on your system.
inside your Linux environment you need to install some dependencies, as well as nsjail.\n
'''bash
wsl\n
sudo apt update\n
sudo apt install -y autoconf bison flex gcc g++ git libprotobuf-dev libnl-route-3-dev libtool make pkg-config protobuf-compiler\n
git clone https://github.com/google/nsjail.git\n
cd nsjail\n
make\n
sudo cp nsjail /usr/local/sbin/\n
'''
once you have nsjail set up in the correct location, clone this repo, and run server.py\n

video demonstration of project:\n
https://youtu.be/d0gMCG_W9wM
