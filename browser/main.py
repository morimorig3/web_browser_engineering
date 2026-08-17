class URL:
    # http://example.org
    def __init__(self, url):
        # "://"でschemeとurlを分割
        # 「http」「example.org」
        self.scheme, url = url.split("://", 1)