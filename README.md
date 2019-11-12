labelVid - Video Annotation Tool
========

labelVid - it's simple video annotation tool made from [labelImg](https://github.com/tzutalin/labelImg) which is written in Python and PyQt.

Annotations are saved as TXT file in like that YOLO format:
`<frame number> <x1> <x2> <y1> <y2> <class object> <precision>`

<pre>
# start
10 348 95 381 180 2 0
11 348 95 381 180 2 0
12 348 95 381 180 4 0
12 119 30 150 60 3 0
12 348 95 381 180 4 0
12 348 95 381 180 4 0
13 348 95 381 180 3 0
19 348 95 381 180 2 0
20 348 95 381 180 2 0
# end
</pre>
![Demo Image](https://raw.githubusercontent.com/tyommik/labelVid/master/demo/demo1.jpg)
