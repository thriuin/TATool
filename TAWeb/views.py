from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.views import View
from math import ceil
from nltk.tokenize.regexp import RegexpTokenizer
import pysolr

class TASearchView(View):
    def __index__(self):
        super().__init__()

    def __init__(self):
        super().__init__()
        # French search fields
        self.solr_fields_fr = ("id,fsc_txt_en,fsc_desc_txt_en,gsin_s,gsin_s_txt_en,gsin_txt_fr,"
                               "nafta_s,chile_s,colombia_s,honduras_s,panama_s,peru_s,korea_s,ukraine_s,wtoagp_s,ceta_s,cptpp_s")
        self.solr_fields_en = ("id,fsc_txt_en,fsc_desc_txt_en,gsin_s,gsin_s_txt_en,gsin_txt_en,"
                               "nafta_s,chile_s,colombia_s,honduras_s,panama_s,peru_s,korea_s,ukraine_s,wtoagp_s,ceta_s,cptpp_s")
        self.solr_query_fields_fr = ['fsc_txt_en', 'fsc_fr_s', 'fsc_desc_txt_en', 'gsin_s', 'gsin_txt_fr']
        self.solr_query_fields_en = ['fsc_txt_en', 'fsc_en_s', 'fsc_desc_txt_en', 'fsc_desc_en_s', 'gsin_s', 'gsin_txt_en']
        self.solr_facet_fields_fr =  ['{!ex=tag_fsc_fr_s}fsc_fr_s',
                                      '{!ex=tag_fsc_desc_fr_s}fsc_desc_fr_s',
                                      '{!ex=tag_gsin_s}gsin_s']
        self.solr_facet_fields_en =  ['{!ex=tag_fsc_en_s}fsc_en_s',
                                      '{!ex=tag_fsc_desc_en_s}fsc_desc_en_s',
                                      '{!ex=tag_gsin_s}gsin_s']
        self.solr_hl_fields_fr = ['fsc_txt_en', 'gsin_s_txt_en', 'fsc_desc_txt_en', 'gsin_txt_fr']
        self.solr_hl_fields_en = ['fsc_txt_en', 'gsin_s_txt_en', 'fsc_desc_txt_en', 'gsin_txt_en']
        self.phrase_xtras_fr = {
            'hl': 'on',
            'hl.simple.pre': '<mark>',
            'hl.simple.post': '</mark>',
            'hl.method': 'unified',
            'hl.snippets': 10,
            'hl.fl': self.solr_hl_fields_fr,
            'hl.preserveMulti': 'true',
            'ps': 10,
            'mm': '3<70%',
            'f.fsc_desc_fr_s.facet.limit': -1,
        }
        self.phrase_xtras_en = {
            'hl': 'on',
            'hl.simple.pre': '<mark>',
            'hl.simple.post': '</mark>',
            'hl.method': 'unified',
            'hl.snippets': 10,
            'hl.fl': self.solr_hl_fields_en,
            'hl.preserveMulti': 'true',
            'ps': 10,
            'mm': '3<70%',
        }

    def get(self, request):
        context = dict(LANGUAGE_CODE=request.LANGUAGE_CODE, )
        context["cdts_version"] = settings.CDTS_VERSION

        # Get any search terms
        solr_search_terms = get_search_terms(request)
        context['search_text'] = str(request.GET.get('search_text', ''))

        # Facets
        solr_search_fsc: str = request.GET.get('ta-search-fsc', '')
        solr_search_fsc_desc: str = request.GET.get('ta-search-fsc-desc', '')
        solr_search_gsin: str = request.GET.get('ta-search-gsin', '')

        context["fsc_selected"] = solr_search_fsc
        context["fsc_selected_list"] = solr_search_fsc.split('|')
        context["fsc_desc_selected"] = solr_search_fsc_desc
        context["fsc_desc_selected_list"] = solr_search_fsc_desc.split('|')
        context["gsin_selected"] = solr_search_gsin
        context["gsin_selected_list"] = solr_search_gsin.split('|')

        if request.LANGUAGE_CODE == 'fr':
            # Uses English for the prototype
            facets_dict = dict(fsc_fr_s=solr_search_fsc,
                               fsc_desc_fr_s=solr_search_fsc_desc,
                               gsin_s=solr_search_gsin)
        else:
            facets_dict = dict(fsc_en_s=solr_search_fsc,
                               fsc_desc_en_s=solr_search_fsc_desc,
                               gsin_s=solr_search_gsin)

        # Query Solr
        # Set pagination values for the page
        start_row, page = calc_starting_row(request.GET.get('page', 1))
        results = solr_query(solr_search_terms,
                             settings.SOLR_URL,
                             self.solr_fields_en,
                             self.solr_query_fields_en,
                             self.solr_facet_fields_en,
                             self.phrase_xtras_en,
                             start_row=str(start_row), pagesize=str(settings.ITEMS_PER_PAGE),
                             facets=facets_dict,
                             sort_order='score desc')
        context['results'] = results
        pagination = calc_pagination_range(context['results'], settings.ITEMS_PER_PAGE, page)
        context['pagination'] = pagination
        context['previous_page'] = (1 if page == 1 else page - 1)
        last_page = (pagination[len(pagination) - 1] if len(pagination) > 0 else 1)
        last_page = (1 if last_page < 1 else last_page)
        context['last_page'] = last_page
        next_page = page + 1
        next_page = (last_page if next_page > last_page else next_page)
        context['next_page'] = next_page
        context['currentpage'] = page

        # Facet results
        if request.LANGUAGE_CODE == 'fr':
            # Identical to English -- for now
            context['fsc_facets_en'] = convert_facet_list_to_dict(
                results.facets['facet_fields']['fsc_fr_s'])
            context['fsc_desc_facets_en'] = convert_facet_list_to_dict(
                results.facets['facet_fields']['fsc_desc_fr_s'])
            context['gsin_facets'] = convert_facet_list_to_dict(
                results.facets['facet_fields']['gsin_s'])
        else:
            context['fsc_facets_en'] = convert_facet_list_to_dict(
                results.facets['facet_fields']['fsc_en_s'])
            context['fsc_desc_facets_en'] = convert_facet_list_to_dict(
                results.facets['facet_fields']['fsc_desc_en_s'])
            context['gsin_facets'] = convert_facet_list_to_dict(
                results.facets['facet_fields']['gsin_s'])

        return render(request, "search.html", context)


def calc_pagination_range(results, pagesize, current_page):
    pages = int(ceil(results.hits / pagesize))
    delta = 2
    if current_page > pages:
        current_page = pages
    elif current_page < 1:
        current_page = 1
    left = current_page - delta
    right = current_page + delta + 1
    pagination = []
    spaced_pagination = []

    for p in range(1, pages + 1):
        if (p == 1) or (p == pages) or (left <= p < right):
            pagination.append(p)

    last = None
    for p in pagination:
        if last:
            if p - last == 2:
                spaced_pagination.append(last + 1)
            elif p - last != 1:
                spaced_pagination.append(0)
        spaced_pagination.append(p)
        last = p

    return spaced_pagination


def calc_starting_row(page_num, rows_per_age=10):
    """
    Calculate a starting row for the Solr search results. We only retrieve one page at a time
    :param page_num: Current page number
    :param rows_per_age: number of rows per page
    :return: starting row
    """
    page = 1
    try:
        page = int(page_num)
    except ValueError:
        pass
    if page < 1:
        page = 1
    elif page > 100000:  # @magic_number: arbitrary upper range
        page = 100000
    return rows_per_age * (page - 1), page


def solr_query(q, solr_url, solr_fields, solr_query_fields, solr_facet_fields, phrases_extra,
               start_row='0', pagesize='10', facets={}, sort_order='score asc'):
    solr = pysolr.Solr(solr_url)
    solr_facets = []
    extras = {
            'start': start_row,
            'rows': pagesize,
            'facet': 'on',
            'facet.sort': 'index',
            'facet.field': solr_facet_fields,
            'fq': solr_facets,
            'fl': solr_fields,
            'defType': 'edismax',
            'qf': solr_query_fields,
            'sort': sort_order,
            'f.fsc_desc_en_s.facet.limit': -1,
            'f.gsin_s.facet.limit': -1,
        }

    for facet in facets.keys():
        if facets[facet] != '':
            facet_terms = facets[facet].split('|')
            quoted_terms = ['"{0}"'.format(item) for item in facet_terms]
            facet_text = '{{!tag=tag_{0}}}{0}:({1})'.format(facet, ' OR '.join(quoted_terms))
            solr_facets.append(facet_text)

    if q != '*':
        extras.update(phrases_extra)

    sr = solr.search(q, **extras)

    # If there are highlighted results, substitute the highlighted field in the doc results

    for doc in sr.docs:
        if doc['id'] in sr.highlighting:
            hl_entry = sr.highlighting[doc['id']]
            for hl_fld_id in hl_entry:
                if hl_fld_id in doc and len(hl_entry[hl_fld_id]) > 0:
                    if type(doc[hl_fld_id]) is list:
                        # Scan Multi-valued Solr fields for matching highlight fields
                        for y in hl_entry[hl_fld_id]:
                            y_filtered = re.sub('</mark>', '', re.sub(r'<mark>', "", y))
                            x = 0
                            for hl_fld_txt in doc[hl_fld_id]:
                                if hl_fld_txt == y_filtered:
                                    doc[hl_fld_id][x] = y
                                x += 1
                    else:
                        # Straight-forward field replacement with highlighted text
                        doc[hl_fld_id] = hl_entry[hl_fld_id][0]

    return sr


def get_search_terms(request: HttpRequest):
    # Get any search terms

    tr = RegexpTokenizer('[^"\s]\S*|".+?"', gaps=False)
    search_text = str(request.GET.get('search_text', ''))
    # Respect quoted strings
    search_terms = tr.tokenize(search_text)
    if len(search_terms) == 0:
        solr_search_terms = "*"
    else:
        solr_search_terms = ' '.join(search_terms)
    return solr_search_terms


def convert_facet_list_to_dict(facet_list: list, reverse: bool = False) -> dict:
    """
    Solr returns search facet results in the form of an alternating list. Convert the list into a dictionary key
    on the facet
    :param facet_list: facet list returned by Solr
    :param reverse: boolean flag indicating if the search results should be returned in reverse order
    :return: A dictonary of the facet values and counts
    """
    facet_dict = {}
    for i in range(0, len(facet_list)):
        if i % 2 == 0:
            facet_dict[facet_list[i]] = facet_list[i + 1]
    if reverse:
        rkeys = sorted(facet_dict,  reverse=True)
        facet_dict_r = {}
        for k in rkeys:
            facet_dict_r[k] = facet_dict[k]
        return facet_dict_r
    else:
        return facet_dict

class TAEvalView(View):
    def __index__(self):
        super().__init__()

    def __init__(self):
        super().__init__()

    def get(self, request):
        context = dict(LANGUAGE_CODE=request.LANGUAGE_CODE, )
        context["cdts_version"] = settings.CDTS_VERSION
        return render(request, "trade_agreeements.html", context)