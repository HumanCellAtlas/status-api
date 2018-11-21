SERVICE_OK = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="72" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="72" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h49v20H0z"/><path fill="#4c1" d="M49 0h23v20H49z"/><path fill="url(#b)" d="M0 0h72v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="255" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="390">service</text><text x="255" y="140" transform="scale(.1)" textLength="390">service</text><text x="595" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="130">ok</text><text x="595" y="140" transform="scale(.1)" textLength="130">ok</text></g> </svg>
"""

SERVICE_ERROR = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="86" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="86" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h49v20H0z"/><path fill="#e05d44" d="M49 0h37v20H49z"/><path fill="url(#b)" d="M0 0h86v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="255" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="390">service</text><text x="255" y="140" transform="scale(.1)" textLength="390">service</text><text x="665" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="270">error</text><text x="665" y="140" transform="scale(.1)" textLength="270">error</text></g> </svg>
"""

SERVICE_UNKNOWN = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="110" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="110" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h49v20H0z"/><path fill="#9f9f9f" d="M49 0h61v20H49z"/><path fill="url(#b)" d="M0 0h110v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="255" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="390">service</text><text x="255" y="140" transform="scale(.1)" textLength="390">service</text><text x="785" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">unknown</text><text x="785" y="140" transform="scale(.1)" textLength="510">unknown</text></g> </svg>
"""

PIPELINE_UNKNOWN = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="114" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="114" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h53v20H0z"/><path fill="#9f9f9f" d="M53 0h61v20H53z"/><path fill="url(#b)" d="M0 0h114v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="275" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="430">pipeline</text><text x="275" y="140" transform="scale(.1)" textLength="430">pipeline</text><text x="825" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">unknown</text><text x="825" y="140" transform="scale(.1)" textLength="510">unknown</text></g> </svg>
"""

AVAILABILITY_TEMPLATE = """<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="132" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="132" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h69v20H0z"/>
    <path fill="{}" d="M69 0h63v20H69z"/>
    <path fill="url(#b)" d="M0 0h132v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
    <text x="355" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="590">availability</text>
    <text x="355" y="140" transform="scale(.1)" textLength="590">availability</text>
    <text x="995" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">{}</text>
    <text x="995" y="140" transform="scale(.1)" textLength="530">{}</text>
  </g>
</svg>"""


def make_availability_svg(color_name, availability):
    text = 'unknown'
    if availability:
        text = "%0.05f" % availability
    color = {
        'lightgrey': '#9f9f9f',
        'brightgreen': '#4c1',
        'yellow': '#dfb317',
        'red': '#e05d44'
    }[color_name]
    return AVAILABILITY_TEMPLATE.format(color, text, text)
