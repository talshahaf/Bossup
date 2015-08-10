change MyGroup.py and run it



added FaceGroup to MyGroup.py for face swapping

based on face_swap: https://github.com/Rambo-django/faces

you'll have to install:
    openCV - follow this guide for windows: http://docs.opencv.org/doc/tutorials/introduction/windows_install/windows_install.html
    dlib - for windows: do the same with the folder python_examples from https://github.com/davisking/dlib
    
    for linux you could probably apt-get or yum or whatever
    
    
you'll also have to download the file: shape_predictor_68_face_landmarks.dat from http://sourceforge.net/projects/dclib/files/dlib/v18.10/

that should work.