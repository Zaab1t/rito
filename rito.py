"""
    Python wrapper for Riot Games' v3 API
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> client = authorize('YOUR-API-KEY')

    You can access every endpoint with attributes so
    ``/lol/static-data/v3/language-strings becomes``

    >>> client.static_data.language_strings()

    Notice that - is replaces by _  and that there are no ``lol`` and
    ``v3`` because we don't like repetition. You just call (with '()')
    the thing, when you want to send a request. Responses are like
    class:`requests.Response`, except that you can lookup in it directly.
    To get a summoner id, you can then do:
    
    >>> my_summoner_name = 'Zaab1t'
    >>> client.summoner.summoners.by_name.name(name=my_summoner_name)

    This is how you can use attributes as placeholders for variabels. The
    only placeholder not allowed is 'server', as it should be used so:

    >>> client = authorize('YOUR-API-KEY', 'na1')  # default is euw1
    >>> client.summoner.summoners.by_name.name(name='Zaab1t', server='euw1')
"""


__all__ = ['authorize', 'get_summoner_id']
__author__ = 'Carl Bordum Hansen'
__license__ = 'MIT'


import requests


_client = None
requests.Response.__getitem__ = lambda self, key: self.json()[key]


class Client:
    endpoint = 'https://{}.api.riotgames.com/'

    def __init__(self, api_key, default_server, *, path=['lol']):
        self.api_key = api_key
        self.default_server = default_server
        self.path = path

    @property
    def url(self):
        return self.endpoint.format(self.server) + '/'.join(self.path)

    def __getattr__(self, name):
        new_path = [name.replace('_', '-')]
        if len(self.path) == 1:
            new_path.append('v3')
        return Client(
            self.api_key,
            self.default_server,
            path=(self.path + new_path)
        )

    def __call__(self, **kwargs):
        self.server = kwargs.pop('server', None) or self.default_server
        self.path = [kwargs.get(key, key) for key in self.path]
        r = requests.get(self.url, params={'api_key': self.api_key})
        r.raise_for_status()
        return r


def authorize(api_key, default_server='euw1'):
    global _client
    _client = Client(api_key, default_server)
    return Client(api_key, default_server)


def get_summoner_id(summoner_name, server):
    return _client.summoner.summoners.by_name.name(
        name=summoner_name,
        server=server
    )['id']
