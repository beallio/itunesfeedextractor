"""
  iTunes Podcast URL Extractor
  php version implemented at http://itunes.so-nik.com
  Original code & inspiration from http://itunes.so-nik.com website; SOURCE: http://snipplr.com/view/52465

  Ex: http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/viewPodcast?id=269238657
  Ex: http://itunes.apple.com/us/podcast/hombre-potato/id319810190?uo=4
 
    Usage: python itunes-extractor.py http://itunes.apple.com/us/podcast/the-morning-stream/id414564832?uo=4
    Returns: http://myextralife.com/ftp/radio/morningstream.xml
"""

#============================================================================================================

import argparse
import sys
from bs4 import BeautifulSoup
import re
import urllib2

#============================================================================================================


class ConvertItunesLink():
    def __init__(self, args):
        """

        :rtype : string or something
        """
        self.itunes_url = args['ITUNES_URL']
        self.verbose = args['verbose']
        self.user_agent = 'iTunes/10.1 (Windows; U; Microsoft Windows XP Home Edition ' \
                          'Service Pack 2 (Build 2600)) DPI/96'  # Pretend we're iTunes.
        self.opener = ''
        self.feed_name = None
        #===========
        print 'Finding feed for url: {0}'.format(self.itunes_url)
        self.url = self.check_protocol_in_url(self.itunes_url)  # first check if correct protocol in url
        self.podcast_id = self.get_podcast_id(self.url)  # strip podcast id from url
        self.output_feed_url = self.get_feed_url

    @property
    def get_feed_url(self):
        base_url = 'http://itunes.apple.com/podcast/id'
        itunes_url = base_url + self.podcast_id
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', self.user_agent)]
        # convert first url, will allow us to parse returned content for second
        # url to convert
        soup = self.convert_url(itunes_url)
        new_url = ''.join(soup.find_all(text=re.compile('itunes')))  # second url
        self.dlog(u'iTunes URL: {0}'.format(new_url))
        soup = self.convert_url(new_url)
        final_feed_url = self.extract_feed_url(soup)
        self.dlog('Feed found for {0}: {1}'.format(self.feed_name, final_feed_url))
        return final_feed_url

    def __repr__(self):
        print u'{0}'.format(self.output_feed_url)

    def __str__(self):
        return u'{0}'.format(self.output_feed_url)

    def extract_feed_url(self, soup):
        buttons = soup.find_all('button')
        for button in buttons:
            output = None
            try:
                self.feed_name = button['podcast-name']
                output = button['feed-url']
                break
            except NameError and KeyError:
                continue
        if output is None:
            print 'Feed not found for {0}'.format(self.feed_name)
            sys.exit()
        return output

    def convert_url(self, url):
        try:
            content = self.opener.open(url).read()
        except urllib2.HTTPError, e:
            print '{0} occurred.\nError connecting to iTunes.'.format(str(e))
            sys.exit()
        else:
            return BeautifulSoup(content)

    def check_if_itunes_u(self, url, title):
        """
        Since iTunes-U uses the same identifier symbols,
        this is where we rule them out until it is supported
        Note: more checking for itunes-u content is done farther below
        Example URL: http://itunes.apple.com/itunes-u/the-civil-war-reconstruction/id341650730
        """
        itunes_u = 'itunes-u'
        if itunes_u in url:
            print '''iTunes-U links not supported.\n
                  Currently Apple does not offer a way to subscribe to iTunes-U material outside of iTunes.\n
                  A temporary solution is to search for a similar title as the podcast in hopes that the content\n
                  providers also posted it to the iTunes Podcast Directory (unlikely for password protected content).\n
                  Try searching for: {0}\n'''.format(title)
            sys.exit()
        pass

    def check_protocol_in_url(self, url):
        protocols = ['itms', 'feed', 'itpc']  # array of invalid protocols to check against
        if ':' in url:  # a colon should indicate if there's a protocol in the URL
            protocol = url.split(':')[0]  # get the protocol
            if len(protocol) > 5:  # check if valid web protocol in url
                self.dlog('Error! {0} not a recognized protocol'.format(protocol))
                print '{0} does not appear to be a valid URL.  Exiting.'.format(url)
                sys.exit()
            if protocol in protocols:  # if it's not 'http:' fix it.
                self.dlog('Replacing URL protocol: {0}'.format(protocol))
                url = url.replace(protocol, 'http')
        return url

    def get_podcast_id(self, url):
        # strip podcast id from url for later use
        id_styles = ['?id=', '&id=', '/id']  # indicates location of podcast id in URL
        id_separator = [x for x in id_styles if x in url]
        self.dlog('Podcast ID separator(s): {0}'.format(id_separator))
        if len(id_separator) == 0:
            # no podcast id found / exit
            print 'iTunes podcast id not found in url: {0}'.format(url)
            sys.exit()
        elif len(id_separator) > 1:
            # multiple podcast ids found / exit
            print 'Multiple iTunes podcast ids found in url: {0}\nExiting.'.format(url)
            sys.exit()
        else:
            podcast_id = url.split(id_separator[0])[1]
            self.dlog('Non-stripped Podcast ID: {0}'.format(podcast_id))
            podcast_id = re.match('\d+', podcast_id).group()
            self.dlog('Stripped Podcast ID: {0}'.format(podcast_id))
            return podcast_id

    def dlog(self, output):
        if self.verbose:
            print '{0}'.format(output)

#====================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument('ITUNES_URL', help='iTunes Podcast URL Link')
    args = vars(parser.parse_args())
    itunes_link = ConvertItunesLink(args)
    print itunes_link

else:
    sys.exit()

