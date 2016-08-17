import urllib.request

# We need to define a custom handler for 'urllib' in order to correctly handle
# HTTP HEAD requests.
# Based on code from original source: https://filippo.io/send-a-head-request-in-python/
class HeadHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    """
    Subclass the HTTPRedirectHandler to make it use our
    HeadRequest also on the redirected URL
    """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (301, 302, 303, 307):
            newurl = newurl.replace(' ', '%20')
            return HeadRequest(newurl,
                               headers=req.headers,
                               origin_req_host=req.origin_req_host,
                               unverifiable=True)
        else:
            raise urllib.error.HTTPError(req.get_full_url(), code, msg, headers, fp)

class HeadRequest(urllib.request.Request):
    def get_method(self):
        return "HEAD"
