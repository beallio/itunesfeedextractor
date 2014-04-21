iTunes Podcast URL Extractor
===================

Original php code & inspiration from [itunes.so-nik.com](http://itunes.so-nik.com)

[PHP source](http://snipplr.com/view/52465)


* Ex: `http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/viewPodcast?id=269238657`
* Ex: `http://itunes.apple.com/us/podcast/hombre-potato/id319810190?uo=4`
* Ex: `https://itunes.apple.com/us/podcast/hardwell-on-air-official-podcast/id559788668?mt=2`

***

Usage and installation
-------------

To install:

    cd /path/to/code
    git clone https://github.com/beallio/itunesfeedextractor.git
    pip install -r /path/to/code/requirements.txt

Usage (CLI):

    python itunes_feed_extractor.py http://itunes.apple.com/us/podcast/the-morning-stream/id414564832?uo=4

Returns:

    http://myextralife.com/ftp/radio/morningstream.xml

Optional Arguments:

    -v : increase verbosity to console

-------------
Usage (as imported module):

    itunes_feed_extractor.ConvertItunesLink(url)

Returns:

    url, if found.  None if podcast url resolution fails.
