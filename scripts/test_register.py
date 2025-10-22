import urllib.request, urllib.parse, sys, traceback

def post():
    url = 'http://127.0.0.1:5000/event/1/register'
    data = urllib.parse.urlencode({'name':'Test User','class_name':'SE','year':'3','roll_no':'TEST123'}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'User-Agent':'test-client'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print('STATUS', resp.status)
            body = resp.read().decode('utf-8')
            print('BODY:', body)
    except Exception:
        print('EXCEPTION:')
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    post()
