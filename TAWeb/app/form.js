
var accumulators = ['ta-search-fsc', 'ta-search-fsc-desc', 'ta-search-gsin'];

function select_facet(selected_item, accumulator) {

    let old_facet_arr = [];
    let old_facet_str = '';
    if (sessionStorage.getItem(accumulator)) {
        old_facet_str = sessionStorage.getItem(accumulator);
        old_facet_arr = String(old_facet_str).split('|');
    }
    let new_facet_arr = [];
    let  found_it = false;
    for (let i=0; i<old_facet_arr.length; i++) {
        let item = old_facet_arr[i];
        let en_selected_item = encodeURIComponent(selected_item).replace(/'/g,'%27');
        if (item !== en_selected_item) {
            new_facet_arr.push(item);
        } else {
            found_it = true;
        }
    }
    if (!found_it) {
        new_facet_arr.push(encodeURIComponent(selected_item));
    }
    let new_facets = new_facet_arr.toString();
    if (new_facets.charAt(0) === '|') {
        new_facets = new_facets.substring(1);
    }
    // Use | to separate values, not a comma
    new_facets = new_facets.replace(/,/g, '|').replace(/'/g,'%27');
    sessionStorage.setItem(accumulator, new_facets);
    $('#page').value = '1';
    submitForm();
}

function clear_facets() {
    let cbs = $( "input:checked" );
    cbs.each(function(i) {
        this['checked'] = false;
    });
    let tbs = $( "input:text" );
    tbs.each(function(i) {
        this['value'] = '';
    });
    sessionStorage.clear();
    submitForm();
}

function gotoPage(page_no) {
    $('#page').val(page_no);
    submitForm();
}

function submitForm() {

    let sort_opt = $('#sort-by').val();
    let page_no = $('#page').val();
    let search_text = $('#ta-search-input').val();
    // IE 11 incompatible: let search_terms = `sort=${sort_opt}&page=${page_no}`;
    let search_terms = "sort=" + sort_opt + "&page=" + page_no;
    if (typeof search_text !== 'undefined') {
        // IE 11 incompatible: search_terms = `${search_terms}&search_text=${search_text}`;
        search_terms = search_terms + "&search_text=" + search_text;
    }
    for (let i=0; i<accumulators.length; i++) {
        if (sessionStorage.getItem(accumulators[i])) {
            let facet_str = sessionStorage.getItem(accumulators[i]);
            // IE 11 incompatible: search_terms=`${search_terms}&${accumulators[i]}=${facet_str}`
            search_terms = search_terms + "&" + accumulators[i] + "=" + facet_str;
        }
    }
    window.location.search = search_terms;
}

function submitFormOnEnter(e) {
    if(e.which === 10 || e.which === 13) {
        $('#page').val('1');
        submitForm();
    }
}
