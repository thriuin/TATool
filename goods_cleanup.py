from collections import defaultdict
import csv
from django.conf import settings
import os
import pysolr
import sys

BULK_SIZE = 100
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TATool.settings')

solr = pysolr.Solr(settings.SOLR_URL)
solr.delete(q='*:*')
solr.commit()

cc_list = []
i = 0
total = 0
with open(sys.argv[1], 'r', encoding='utf-8-sig', errors="ignore") as cc_file:
    cc_reader = csv.DictReader(cc_file, dialect='excel')
    last = dict.fromkeys(['code', 'code_desc', 'gsin', 'gsin_en', 'gsin_fr'], "")
    agreements = dict.fromkeys(['nafta', 'chile', 'colombia', 'honduras', 'panama', 'peru', 'korea', 'ukraine', 'wtoagp', 'ceta', 'cptpp'], "")
    entries = defaultdict(str)
    for cc in cc_reader:
        if str(cc['Federal Supply Codes Description']).startswith('http'):
            continue
        if cc['Federal Supply Codes']:
            entries['code'] = cc['Federal Supply Codes'].strip()
            last['code_desc'] = "{0} (unspecified)".format(entries['code'])
        else:
            last['code'].strip()
        last['code'] = entries['code'].strip()

        entries['code_desc'] = cc['Federal Supply Codes Description'].strip() if cc['Federal Supply Codes Description'] else last['code_desc'].strip()
        last['code_desc'] = entries['code_desc'].strip()

        entries['gsin'] = cc['GSIN Code'] if cc['GSIN Code'] else last['gsin']
        last['gsin'] = entries['gsin'].strip()
        entries['gsin_en'] = cc['GSIN Description EN'] if cc['GSIN Description EN'] else last['gsin_en']
        last['gsin_en'] = entries['gsin_en'].strip()
        entries['gsin_fr'] = cc['GSIN Description FR'] if cc['GSIN Description FR'] else last['gsin_fr']
        last['gsin_fr'] = entries['gsin_fr'].strip()
        agreements['nafta'] = cc['NAFTA Annex 1001.1b-1'] if cc['NAFTA Annex 1001.1b-1'] else '-'
        agreements['chile'] = cc['Chile (CCFTA) Annex K bis-01.1-3'] if cc['Chile (CCFTA) Annex K bis-01.1-3'] else '-'
        agreements['colombia'] = cc['Colombia (CCoFTA) Annex 1401-4'] if cc['Colombia (CCoFTA) Annex 1401-4'] else '-'
        agreements['honduras'] = cc['Honduras (CHFTA) Annex 17.3'] if cc['Honduras (CHFTA) Annex 17.3'] else '-'
        agreements['panama'] = cc['Panama (CPaFTA) Annex 4'] if cc['Panama (CPaFTA) Annex 4'] else '-'
        agreements['peru'] = cc['Peru (CPFTA) Annex 1401. 1-3'] if cc['Peru (CPFTA) Annex 1401. 1-3'] else '-'
        agreements['korea'] = cc['Korea (CKFTA) Annex 14-A'] if cc['Korea (CKFTA) Annex 14-A'] else '-'
        agreements['ukraine'] = cc['Ukraine (CUFTA) Annex 10-3'] if cc['Ukraine (CUFTA) Annex 10-3'] else '-'
        agreements['wtoagp'] = cc['WTO-AGP Canada Annex 1'] if cc['WTO-AGP Canada Annex 1'] else '-'
        agreements['ceta'] = cc['CETA Annex 19-4'] if cc['CETA Annex 19-4'] else '-'
        agreements['cptpp'] = cc['CPTPP Chapter 15-A Section D'] if cc['CPTPP Chapter 15-A Section D'] else '-'
        cc_obj = {'id': "goods-{0}".format(entries['gsin']),
                  'class_s': 'Goods',
                  'fsc_txt_en': entries['code'],
                  'fsc_desc_txt_en': entries['code_desc'],
                  'gsin_s': entries['gsin'],
                  'gsin_txt_en': entries['gsin_en'],
                  'gsin_txt_fr': entries['gsin_fr'],
                  'nafta_s': agreements['nafta'],
                  'chile_s': agreements['chile'],
                  'colombia_s': agreements['colombia'],
                  'honduras_s': agreements['honduras'],
                  'panama_s': agreements['panama'],
                  'peru_s': agreements['peru'],
                  'korea_s': agreements['korea'],
                  'ukraine_s': agreements['ukraine'],
                  'wtoagp_s': agreements['wtoagp'],
                  'ceta_s': agreements['ceta'],
                  'cptpp_s': agreements['cptpp'],
                  }
        cc_list.append(cc_obj)
        i += 1
        total += 1
        if i == BULK_SIZE:
            solr.add(cc_list)
            solr.commit()
            cc_list = []
            print('{0} Records Processed'.format(total))
            i = 0

    if len(cc_list) > 0:
        solr.add(cc_list)
        solr.commit()
        print('{0} Records Processed'.format(total))
