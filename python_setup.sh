wget http://www.raspberrypiwiki.com/images/4/46/LCD-show-170509.tar.gz
mkdir lcd
mv LCD-show-170509.tar.gz lcd/
cd lcd/
tar xzvf LCD-show-170509.tar.gz 
cd LCD-show/
sudo ./LCD35-show 
sudo apt-get update
sudo apt-get install vim
ifconfig wlan0
sudo wpa_cli reconfigure
sudo vi /etc/wpa_supplicant/wpa_supplicant.conf 
ls /var/run/ | grep wpa
sudo apt-get install wpa_supplicant
ps -ef | grep wpa
sudo wpa_passphrase [SSID] [PASSWORD] >> /etc/wpa_supplicant/wpa_supplicant.conf 
sudo reboot
sudo apt-get update
sudo apt-get install build-essential git cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install libgtk2.0-dev
sudo apt-get install libatlas-base-dev gfortran
sudo apt-get install python2.7-dev python3-dev
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.0.0.zip
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip
unzip opencv.zip 
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
cd opencv-3.1.0/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=OFF ..
ls /usr/local/lib/python3.4/dist-packages/
make -j4
sudo make install
sudo ldconfig
ls /usr/local/lib/python3.4/dist-packages/
ls /usr/local/lib/python3.4/
sudo pip install numpy
cmake clean
make clean
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON ..
python
ls -a /usr/local/lib/python2.7/site-packages/
ls -a /usr/local/lib/python3.4/dist-packages/
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON -D PYTHON2_PACKAGES_PATH=/usr/local/lib/python2.7/site-packages -D PYTHON2_NUMPY_INCLUDE_DIRS=ls /usr/local/lib/python2.7/dist-packages/numpy/core/include -D PYTHON_NUMPY_INCLUDE_DIR=/usr/local/lib/python3.4/dist-packages/numpy/core/include ..
sudo apt-get install python3-pip
sudo pip3 install numpy
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON ..
make -j4
sudo make install
sudo ls /usr/local/lib/python3.4/site-packages/
ls /usr/local/lib/python3.4/dist-packages/
cd /usr/local/lib/python3.4/dist-packages/
sudo mv cv2.cpython-34m.so cv2.so
cd /usr/lib/python3/dist-packages/
sudo ln -s /usr/local/lib/python3.4/dist-packages/cv2.so 
sudo mv cv2.so cv2.cpython-34m.so
sudo ln -s /usr/local/lib/python3.4/dist-packages/cv2.cpython-34m.so 
sudo pip3 install picamera
