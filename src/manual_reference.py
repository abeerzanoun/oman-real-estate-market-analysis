"""Project slugs and bilingual names; these are reference labels, not observations."""
import re
import unicodedata


def normalize(value):
    text = unicodedata.normalize('NFKC', str(value)).casefold().strip()
    text = re.sub(r'[\u064b-\u065f\u0670\u0640\u200e\u200f\u202a-\u202e]', '', text)
    text = text.translate(str.maketrans('أإآىیکة', 'اااييكه'))
    return re.sub(r'[^\w]+', ' ', text).strip()


GOVERNORATES = (
    ('muscat', 'Muscat', 'مسقط', ('Masqat',)),
    ('dhofar', 'Dhofar', 'ظفار', ()),
    ('musandam', 'Musandam', 'مسندم', ()),
    ('al_buraimi', 'Al Buraimi', 'البريمي', ('Al Buraymi', 'Buraimi', 'Buraymi')),
    ('ad_dakhiliyah', 'Ad Dakhiliyah', 'الداخلية', ('Ad Dakhliyah', 'Al Dakhiliyah', 'Dakhiliyah')),
    ('north_al_batinah', 'North Al Batinah', 'شمال الباطنة', ('Al Batinah North', 'Albatinah North')),
    ('south_al_batinah', 'South Al Batinah', 'جنوب الباطنة', ('Al Batinah South', 'Albatinah South')),
    ('north_ash_sharqiyah', 'North Ash Sharqiyah', 'شمال الشرقية', ('Ash Sharqiyah North', 'Ash Sharqiah North', 'North Sharqiya', 'North Al Sharqiyah')),
    ('south_ash_sharqiyah', 'South Ash Sharqiyah', 'جنوب الشرقية', ('Ash Sharqiyah South', 'Ash Sharqiah South', 'South Sharqiya', 'South Al Sharqiyah')),
    ('adh_dhahirah', 'Adh Dhahirah', 'الظاهرة', ('Ad Dhahirah', 'Al Dhahirah', 'Dhahirah')),
    ('al_wusta', 'Al Wusta', 'الوسطى', ('Wusta',)),
)
GOVERNORATE_LOOKUP = {}
for slug, english, arabic, aliases in GOVERNORATES:
    for label in (slug, english, arabic, *aliases):
        GOVERNORATE_LOOKUP[normalize(label)] = (slug, english, arabic)
TOTAL_LABELS = {normalize(s) for s in ('Total', 'Grand total', 'Oman', 'Sultanate of Oman', 'الإجمالي', 'اجمالي', 'الجملة', 'سلطنة عمان', 'عمان')}


def governorate(value):
    key = normalize(value)
    key = re.sub(r'^(?:محافظ[ةه]|governorate of)\s+', '', key)
    key = re.sub(r'\s+governorate$', '', key)
    if key in TOTAL_LABELS:
        return None
    if key not in GOVERNORATE_LOOKUP:
        key = next((k for k in GOVERNORATE_LOOKUP if k.replace(' ', '') == key.replace(' ', '')), key)
    if key not in GOVERNORATE_LOOKUP:
        raise ValueError(f'Unknown or combined governorate label: {value!r}')
    return GOVERNORATE_LOOKUP[key]


HEADER_ALIASES = {
    'year': ('year', 'السنة', 'العام', 'سنة'),
    'month': ('month', 'الشهر', 'شهر'),
    'quarter': ('quarter', 'الربع', 'ربع'),
    'governorate': ('governorate', 'governorates', 'المحافظة', 'المحافظات', 'محافظة'),
    'wilayat': ('wilayat', 'wilaya', 'الولاية', 'ولاية'),
    'property_category': ('property_category', 'property category', 'property type', 'نوع العقار', 'فئة العقار', 'نوع الاستخدام'),
    'transaction_type': ('transaction_type', 'transaction type', 'نوع المعاملة', 'نوع التصرف'),
    'transaction_count': ('transaction_count', 'transaction count', 'عدد المعاملات', 'عدد العقود'),
    'transaction_value': ('transaction_value', 'transaction value', 'transaction_value_omr', 'transaction value omr', 'قيمة المعاملات', 'القيمة المتداولة', 'قيمة التداول'),
    'property_price_index': ('property_price_index', 'property price index', 'مؤشر أسعار العقارات', 'الرقم القياسي لأسعار العقارات'),
    'value': ('value', 'القيمة'),
    'period_start': ('period_start', 'period start', 'بداية الفترة'),
    'period_end': ('period_end', 'period end', 'نهاية الفترة'),
    'frequency': ('frequency', 'reporting frequency', 'الدورية'),
}
HEADER_LOOKUP = {normalize(label): canonical for canonical, aliases in HEADER_ALIASES.items() for label in aliases}
