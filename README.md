oEmbed for Picasa
==============================================================================

Supports [oEmbed] output for both photos and videos uploaded to [Picasa].
 
 [oEmbed]: http://oembed.com
 [Picasa]: http://picasaweb.picasaweb.google.com


Supported URLs
==============================================================================
Support for Picasa URLs;

 * http(s)://picasaweb.google.com/{userid}/{albumname}

     Outputs "rich" element which contains the Picasa album.

 * http(s)://picasaweb.google.com/{userid}/{albumname}#{photoid}

     Outputs "photo" or "video" element which contains the Photo/Video.

 * http(s)://picasaweb.google.com/.*/{userid}/albumid/{albumid}/photoid/{photoid}

     Outputs "photo" or "video" element which contains the Photo/Video.

Don't forget to escape the *hash* in the URL! Otherwise it will never get to
the oEmbed server and you'll get album mode.

Support for the following Google+ URLs (which use Picasa in the background);

 * https://plus.google.com/photos/{userid}/albums/{albumid}/{userid}

     Outputs "photo" or "video" element which contains the Photo/Video.

 * https://plus.google.com/photos/{userid}/albums/{albumid}

     Outputs "rich" element which contains the Picasa album.


Picasa Video Support
==============================================================================

Picasa Video support is a little tricky because the URLs that the Picasa feed
gives back have authentication tokens which expire after a short period.

To work around this the oEmbed server provides a page which uses javascript to
re-fetch the authentication tokens when the page is display. This means the
server will return an iframe element for video elements.

