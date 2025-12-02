import ssl
import os
import certifi
import socket
from urllib.parse import urlparse

print('--- Diagnostics Report ---')
print('Python executable:', os.sys.executable)
print('Python version:', os.sys.version.splitlines()[0])
print('OpenSSL/ssl version:', getattr(ssl, 'OPENSSL_VERSION', 'unknown'))
print('certifi CA bundle:', certifi.where())

print('\n--- Proxy environment variables ---')
for var in ('HTTP_PROXY', 'http_proxy', 'HTTPS_PROXY', 'https_proxy', 'ALL_PROXY', 'all_proxy'):
    print(f'{var} =', os.environ.get(var))

print('\n--- MONGO URI parsing (from config) ---')
try:
    from config import Config
    print('Configured MONGO_URI: (hidden credentials)')
    u = Config.MONGO_URI
    # hide credentials for printing
    try:
        parsed = urlparse(u)
        safe = u.replace(parsed.password or '', '***') if parsed.password else u
        print(safe)
    except Exception:
        print('Unable to parse URI for safety')
except Exception as e:
    print('Failed to import Config:', e)

print('\n--- DNS SRV lookup for cluster SRV record ---')
try:
    import dns.resolver
    # extract host from URI
    host = None
    try:
        from config import Config as C
        host = urlparse(C.MONGO_URI).hostname
    except Exception:
        pass
    if host:
        try:
            answers = dns.resolver.resolve('_mongodb._tcp.' + host, 'SRV')
            for r in answers:
                print(r.to_text())
        except Exception as e:
            print('SRV lookup failed:', e)
    else:
        print('No host found to query SRV for')
except Exception as e:
    print('dnspython not available or SRV failed:', e)

print('\n--- Network connectivity (socket connect) ---')
try:
    # try connecting to one of the listed hosts by resolving SRV or hostname
    targets = []
    try:
        from config import Config as C2
        host = urlparse(C2.MONGO_URI).hostname
        if host:
            targets.append((host, 27017))
    except Exception:
        pass

    if not targets:
        print('No targets to test')
    else:
        for h, p in targets:
            try:
                print(f'Connecting to {h}:{p} ...')
                s = socket.create_connection((h, p), timeout=5)
                s.close()
                print('TCP connect: OK')
            except Exception as e:
                print('TCP connect failed:', e)
except Exception as e:
    print('Network check failed:', e)

print('\n--- End of report ---')
