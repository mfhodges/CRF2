from django import template




from rest_framework.utils.urls import remove_query_param
from django.utils.encoding import iri_to_uri
from django.utils.html import escape


register = template.Library()

@register.simple_tag
def delete_query_param(request, key):
    """
    Add a query parameter to the current request url, and return the new url.
    """

    iri = request.get_full_path()
    uri = iri_to_uri(iri)
    val = remove_query_param(uri, key)
    return escape(val)



@register.simple_tag
def get_item(qp, key):
    # qp is request.query_params
    print("qp", qp)
    print("key, val", (key , val))
    if val == None:
        return ""
    else:
        return val

"""
@register.simple_tag
def add_query_param(request, key, val):

    #Add a query parameter to the current request url, and return the new url.

    iri = request.get_full_path()
    uri = iri_to_uri(iri)
    return escape(replace_query_param(uri, key, val))



def replace_query_param(url, key, val):

    ##Given a URL and a key/val pair, set or replace an item in the query
    ##parameters of the URL, and return the new URL.

    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(force_str(url))
    query_dict = urlparse.parse_qs(query, keep_blank_values=True)
    query_dict[force_str(key)] = [force_str(val)]
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


def remove_query_param(url, key):

    ##Given a URL and a key/val pair, remove an item in the query
    ##parameters of the URL, and return the new URL.
    
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(force_str(url))
    query_dict = urlparse.parse_qs(query, keep_blank_values=True)
    query_dict.pop(key, None)
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))



"""
