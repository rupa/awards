# coding=utf-8
'''
confer an honor

curl -d "n=NAME&t=TITLE&b=BY&m=MSG"
'''

import cgi, mimetypes, os, random, sqlite3
from datetime import datetime
from string import ascii_letters, digits

# set this if HTTP_HOST isn't good enough
BASE_URL = None

cwd = os.path.abspath(os.path.dirname(__file__))

def getconn():
    conn = sqlite3.connect(
        os.path.join(cwd, 'db.sqlite3'),
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    conn.row_factory = sqlite3.Row
    return conn

if not os.path.exists(os.path.join(cwd, 'db.sqlite3')):
    conn = getconn()
    conn.executescript('''
    CREATE TABLE awards (
        id TEXT PRIMARY KEY,
        name TEXT,
        title TEXT,
        by TEXT,
        msg TEXT,
        lr TEXT,
        tb TEXT,
        SEAL TEXT,
        date TIMESTAMP
    );
    ''')
    conn.commit()
    conn.close()

body_html = '''
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="robots" content="noindex, nofollow, noimageclick">
        <link
            href='http://fonts.googleapis.com/css?family=Great+Vibes'
            rel='stylesheet'
            type='text/css'
        >
        <link
            href='http://fonts.googleapis.com/css?family=La+Belle+Aurore'
            rel='stylesheet'
            type='text/css'>
        <link
            href='http://fonts.googleapis.com/css?family=Special+Elite'
            rel='stylesheet'
            type='text/css'>
        <link
            href='http://fonts.googleapis.com/css?family=UnifrakturMaguntia'
            rel='stylesheet'
            type='text/css'
        >
        <style>
            a {{
                text-decoration: none;
            }}
            #accomplishment {{
                font-family: "Special Elite", monospace;
                font-weight: bold;
                font-size: 1.5em;
                margin-bottom: 2em;
            }}
            #awarded {{
                font-family: "Great Vibes", cursive;
                font-size: 1.5em;
                margin-top: 10px;
                margin-bottom: 20px;
            }}
            #dated {{
                font-family: "Special Elite", monospace;
                margin-bottom: 1em;
                text-align: right;
            }}
            #heading {{
                font-family: 'UnifrakturMaguntia', cursive;
                font-size: 3.3em;
                color: #000080;
                text-shadow: 4px 4px 2px rgba(150, 150, 150, 1);
            }}
            #honoree {{
                font-family: "Special Elite", monospace;
                font-weight: bold;
                font-size: 2em;
                margin-top: 1em;
            }}
            #message {{
                font-family: "Special Elite", monospace;
                font-size: 0.8em;
                font-style: italic;
                margin-bottom: 10px;
            }}
            #signed {{
                font-family: "La Belle Aurore", cursive;
                font-size: 1.5em;
                margin-bottom: -20px;
                margin-top: -10px;
            }}
            hr {{
                height: 30px;
                border-style: solid;
                border-color: #444444;
                border-width: 1px 0 0 0;
                border-radius: 20px;
            }}
            hr:before {{ /* Not really supposed to work, but does */
                display: block;
                content: "";
                height: 30px;
                margin-top: -31px;
                border-style: solid;
                border-color: black;
                border-width: 0 0 1px 0;
                border-radius: 20px;
            }}
            hr.heavy {{
                border-width: 2px 0 0 0;
                width: 80%;
            }}
        </style>
    </head>
    <body>
    {0}
    </body>
</html>
'''

award_html = '''
        <p>&nbsp;</p>
        <center>
            <table width="650">
                <tr>
                <td>
                    <img src="images/lr/{0}">
                </td>
                <td>
                    <center>
                        <img src="images/tb/{1}">
                        <br>
                        <br>
                    </center>
                    <center>
                        <a href="{8}">
                        <div id="heading">
                            Achievement Certificate
                        </div>
                        </a>
                        <div id="honoree">{2}</div>
                        <hr class="heavy">
                        <div id="awarded">
                            is Awarded this Certificate for
                        </div>
                        <div id="accomplishment">
                            {3}
                        </div>
                    </center>
                    <table>
                        <tr>
                        <td width="120">
                            <center>
                                <img src="images/seals/{4}">
                            </center>
                        </td>
                        <td width="75"></td>
                        <td width="200">
                            <center>
                            <div id="message">
                                {5}
                            </div>
                            <div id="signed">{6}</div>
                            <hr>
                            </center>
                            <div id="dated">{7}</div>
                        </td>
                        </tr>
                    </table>
                    <center>
                        <img src="images/tb/{1}">
                    </center>
                </td>
                <td>
                    <img src="images/lr/{0}">
                </td>
                </tr>
            </table>
        </center>
'''

# sides, topbottom, name, title, seal, msg, by, date(), topbottom, sides

images = {}
for x in ['lr', 'tb', 'seals']:
    images[x] = os.listdir(os.path.join(cwd, 'images', x))

def randpics():
    return (
        random.choice(images['tb']),
        random.choice(images['lr']),
        random.choice(images['seals'])
    )

def make_award(name, title, by, msg):

    def randname():
        return ''.join(random.sample(ascii_letters + digits, 4))

    name = name.replace('<','').strip()
    title = title.replace('<','').strip()
    by = by.replace('<','').strip()
    msg = msg.replace('<','').strip()

    if not (name or title or by):
        return ''

    if not msg:
        msg = 'Congratulations about this'

    tb, lr, seal = randpics()
    outname = randname()
    conn = getconn()
    while conn.execute(
        'SELECT count() FROM awards where id=?', (outname,)
    ).fetchone()[0] > 0:
        outname = randname()

    conn.execute('INSERT INTO awards VALUES(?,?,?,?,?,?,?,?,?)', (
        outname,
        name,
        title,
        by,
        msg,
        lr,
        tb,
        seal,
        datetime.now()
    ))
    conn.commit()
    conn.close()

    return outname

def get_award(award_id='', base_url=''):
    conn = getconn()
    fields = conn.execute(
        'SELECT * FROM awards WHERE id=?', (award_id,)
    ).fetchone()
    conn.close()
    if fields:
        return format_award(fields, base_url)
    return ''

def format_award(fields, base_url=''):
    award = award_html.format(
        fields[5],
        fields[6],
        fields[1],
        fields[2],
        fields[7],
        fields[4],
        fields[3],
        fields[8].strftime('%A, %B %d %Y'),
        'http://{0}/{1}'.format(base_url, fields[0])
    )
    return body_html.format(award)

def example_award(base_url=''):
    tb, lr, seal = randpics()
    fields = ['', '', '', '', '', lr, tb, seal, datetime.now(), '']
    return format_award(fields, base_url)

def recent_awards(base_url='', limit=10):
    conn = getconn()
    awards = conn.execute(
        'SELECT id FROM awards ORDER BY date DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    awards = [get_award(id[0], base_url) for id in awards]
    return body_html.format('\n'.join(awards))

def index(base_url):

    # recent awards
    #return recent_awards(base_url)

    # blank award
    #return example_award(base_url=base_url)

    # html
    try:
        with open(os.path.join(cwd, 'index.html'), 'r') as html:
            return html.read()
    except IOError:
        return ''

def application(environ, start_response):

    def get_base_url():
        base_url = BASE_URL
        if not base_url:
            base_url = environ.get('HTTP_X_FORWARDED_HOST', False)
        if not base_url:
            base_url = environ.get('HTTP_HOST')
        return base_url

    path = environ.get('PATH_INFO')
    method = environ.get('REQUEST_METHOD')
    base_url = get_base_url()

    status = '200 OK'
    headers = []

    if method == 'HEAD':
        content_type = 'text/plain; charset=utf-8'
        data = ''

    elif method == 'OPTIONS':
        headers.append(('Allows', 'HEAD, GET, POST, OPTIONS'))
        content_type = 'text/plain; charset=utf-8'
        data = '{0} {1}\n'.format(__doc__.strip(), environ.get('HTTP_HOST'))
        # debug
        #data = repr(environ)

    elif method == 'POST':
        form = cgi.FieldStorage(
            fp=environ['wsgi.input'], environ=environ
        )
        name = form.getfirst('n', '')
        title = form.getfirst('t', '')
        by = form.getfirst('b', '')
        msg = form.getfirst('m', '')

        content_type = 'text/plain; charset=utf-8'
        data = 'http://{0}/{1}\n'.format(
            base_url, make_award(name, title, by, msg)
        )

    elif method == 'GET':
        fname = '{0}{1}'.format(cwd, path)

        if path != '/db.sqlite3' and os.path.isfile(fname):
            content_type = mimetypes.guess_type(fname)
            with open(fname, 'r') as fh:
                data = fh.read()
        elif path == '/':
            content_type = 'text/html; charset=utf-8'
            data = index(base_url)
        else:
            content_type = 'text/html; charset=utf-8'
            data = get_award(path[1:], base_url)
            if not data:
                # index
                data = index(base_url)

    else:
        status = '405 Method Not Allowed'
        content_type = 'text/html; charset=utf-8'
        data = 'Method Not Allowed'

    headers.append(('Content-Type', content_type))
    headers.append(('Content-Length', str(len(data))))

    start_response(status, headers)
    return iter([data])
