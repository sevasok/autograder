If you want to try it out on your own you need to have Windows, and have wsl installed on your system.
inside your Linux environment you need to install some dependencies, as well as nsjail.
wsl
sudo apt update
sudo apt install -y autoconf bison flex gcc g++ git libprotobuf-dev libnl-route-3-dev libtool make pkg-config protobuf-compiler
git clone https://github.com/google/nsjail.git
cd nsjail
make
sudo cp nsjail /usr/local/sbin/

once you have nsjail set up in the correct location, clone this repo, and run server.py

video demonstration of project:
https://youtu.be/d0gMCG_W9wM
