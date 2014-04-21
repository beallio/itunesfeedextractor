import argparse
from bs4 import BeautifulSoup
import re
import urllib2

#============================================================================================================


class ConvertItunesLink():
    def __init__(self, args):
        """
        """
        try:
            # if coming from CLI
            self._itunes_url = args['ITUNES_URL']
            self._verbose = args['verbose']
        except TypeError:
            # if called from another module
            self._itunes_url = args
            self._verbose = False
            if not isinstance(self._itunes_url, basestring):
                # not a valid url raise error
                self._raise_url_error()
                pass

        self._USER_AGENT = 'iTunes/10.1 (Windows; U; Microsoft Windows XP Home Edition Service Pack 2 (Build 2600)) ' \
                           'DPI/96'  # Pretend we're iTunes.
        self._opener = ''
        self._feed_name = None
        #===========
        try:
            self._dlog(u'\nArguments: {0}\n'.format(args))
            self._info_print(u'Finding feed for url: {0}'.format(self._itunes_url))
            self._url = self._check_protocol_in_url(self._itunes_url)  # first check if correct protocol in url
            self._podcast_id = self._get_podcast_id(self._url)  # strip podcast id from url
            self.output_feed_url = self._get_feed_url()
        except UrlError:
            pass

    def __str__(self):
        return u'{0}'.format(self.output_feed_url)

    def _get_feed_url(self):
        base_url = 'http://itunes.apple.com/podcast/id'
        converted_url = base_url + self._podcast_id
        self._opener = urllib2.build_opener()
        self._opener.addheaders = [('User-agent', self._USER_AGENT)]
        # convert first url, will allow us to parse returned content for second
        # url to convert
        soup = self._convert_url(converted_url)
        new_url = ''.join(soup.find_all(text=re.compile('itunes')))  # second url
        # check if user already submitted a semi-parsed itunes URL
        # which can happen occasionally if googling for an artist, google will take people
        # to the second part of the URL we're looking for.
        if new_url[0:4] == 'http':
            self._dlog('Using converted iTunes URL: {0}'.format(new_url))
            used_url = new_url
            soup = self._convert_url(used_url)
        else:
            self._dlog('Using base URL and ID: {0}'.format(converted_url))
            used_url = converted_url
        final_feed_url = self.extract_feed_url(soup, used_url)
        self._dlog(u'Feed found for {0}: {1}'.format(self._feed_name, final_feed_url))
        return final_feed_url

    def extract_feed_url(self, soup, url):
        buttons = soup.find_all('button')
        output = None
        for button in buttons:
            try:
                self._feed_name = button['podcast-name']
                output = button['feed-url']
                if output is not None:
                    break
            except NameError and KeyError:
                continue
        if output is None:
            itunes_u_check = self._check_if_itunes_u(url, self._feed_name)
            if not itunes_u_check:
                if self._feed_name:
                    self._info_print('Feed {0} not found.'.format(self._feed_name))
                else:
                    self._info_print('Feed not found.')
                    #self.dlog('{0}'.format(soup.find_all(text=re.compile('customerMessage</key>')))
            self._raise_url_error()
        return output

    def _raise_url_error(self):
        self.output_feed_url = None
        raise UrlError(u'Error locating feed for URL: {0}'.format(self._itunes_url))

    def _convert_url(self, url):
        try:
            content = self._opener.open(url).read()
        except urllib2.HTTPError, e:
            self._info_print('{0} occurred.\nError connecting to iTunes.'.format(str(e)))
            self._raise_url_error()
        else:
            return BeautifulSoup(content)

    def _check_if_itunes_u(self, url, feed_name=None):
        """
        Since iTunes-U uses the same identifier symbols,
        this is where we rule them out until it is supported
        Note: more checking for itunes-u content is done farther below
        Example URL: http://itunes.apple.com/itunes-u/the-civil-war-reconstruction/id341650730

        Return True if itunes-U URL; False otherwise
        :rtype : boolean
        """
        itunes_u_designator = ['itunes-u', 'itunesu']
        # loop through itunes-u URL designators in the converted URL and user argument URL
        check = [itm for itm in itunes_u_designator if itm in url or itm in self._itunes_url]
        if len(check) > 0:
            # itunes URL dedicated, show warning to user, and return TRUE
            self._info_print('''\n
                Warning: iTunes-U links not supported.\n
                Currently Apple does not offer a way to subscribe to iTunes-U material outside of iTunes.
                A temporary solution is to search for a similar title as the podcast in hopes that the content
                providers also posted it to the iTunes Podcast Directory (unlikely for password protected content).''')
            if feed_name is not None:
                self._info_print('''
                Try searching for: {0}
                '''.format(feed_name))
            return True
        # itunes u not found, return FALSE
        return False

    def _check_protocol_in_url(self, url):
        protocols = ['itms', 'feed', 'itpc']  # array of invalid protocols to check against
        if ':' in url:  # a colon should indicate if there's a protocol in the URL
            protocol = url.split(':')[0]  # get the protocol
            if len(protocol) > 5:  # check if valid web protocol in url
                self._dlog('Error! {0} not a recognized protocol'.format(protocol))
                self._info_print('{0} does not appear to be a valid URL.  Exiting.'.format(url))
                self._raise_url_error()
                return
            if protocol in protocols:  # if it's not 'http:' fix it.
                self._dlog('Replacing URL protocol: {0}'.format(protocol))
                url = url.replace(protocol, 'http')
        return url

    def _get_podcast_id(self, url):  # strip podcast id from url for later use
        id_styles = ['?id=', '&id=', '/id']  # indicates location of podcast id in URL
        id_separator = [x for x in id_styles if x in url]
        self._dlog('Podcast ID separator(s): {0}'.format(id_separator))
        if len(id_separator) == 0:  # no podcast id found / exit
            self._info_print('iTunes podcast id not found in url: {0}'.format(url))
            self._raise_url_error()
            return
        elif len(id_separator) > 1:  # multiple podcast ids found / exit
            self._info_print('Multiple iTunes podcast ids found in url: {0}\nExiting.'.format(url))
            self._raise_url_error()
            return
        else:
            podcast_id = url.split(id_separator[0])[1]
            self._dlog('Non-stripped Podcast ID: {0}'.format(podcast_id))
            podcast_id = re.match('\d+', podcast_id).group()
            self._dlog('Stripped Podcast ID: {0}'.format(podcast_id))
            return podcast_id

    def _dlog(self, output):
        if self._verbose:
            print '[DEBUG] ' + u'{0}'.format(output)

    def _info_print(self, output):
        print '[INFO] ' + u'{0}'.format(output)


class UrlError(Exception):
    pass

#====================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument('ITUNES_URL', help='iTunes Podcast URL Link')
    args = vars(parser.parse_args())
    print ConvertItunesLink(args)

else:
    pass

# exit file
