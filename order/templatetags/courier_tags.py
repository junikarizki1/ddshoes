from django import template

register = template.Library()

COURIER_TRACKING_URLS = {
    'jne': 'https://www.jne.co.id/id/trace',
    'jnt': 'https://www.jet.co.id/track',
    'sicepat': 'https://www.sicepat.com/checkAwb',
    'anteraja': 'https://anteraja.id/tracking',
    'pos': 'https://www.posindonesia.co.id/id/trace',
    'tiki': 'https://www.tiki.id/tracing',
    'lion': 'https://lionparcel.com/track',
    'ninja': 'https://ninja.co.id/track',
    'sap': 'https://www.sap-express.com/track',
    'rex': 'https://rex.com.id/track',
    'star': 'https://www.starcargo.co.id/track',
    'wahana': 'https://www.wahana.com/track',
    'ncs': 'https://www.ncs.co.id/track',
    'sentral': 'https://www.sentralcargo.com/track',
    'ide': 'https://www.idealogistics.co.id/track',
    'rpx': 'https://www.rpxonline.com/track',
    'dse': 'https://www.dse.co.id/track',
}

@register.filter
def courier_tracking_url(shipping_service):
    if not shipping_service:
        return '#'
    code = shipping_service.split()[0].lower()
    return COURIER_TRACKING_URLS.get(code, '#')
