/*
Web client for DNA search app
*/

$(document).ready(init_page);

USER_SRC = 'user.fasta' // used as filename for user-entered data

MIME_TYPES = {
    'fasta': 'application/fasta'
    // 'gb': 'application/gb' # not yet tested
};

// Hold onto recent items. Display them even if they're not in the database yet. 
// Contains { guid : item }
RECENT_ITEMS = {};

DEBUG=true

function log(){ if (DEBUG){ console.log(...arguments); }}

function init_page(){
    poll_loop();
    $("#file_field").change(function() {
	var fileName = $(this).val().split("\\").pop();
	$(this).siblings(".custom-file-label").addClass("selected").html(fileName);
	$(":radio").prop("checked", false);
	$("#file_radio").prop("checked", true);
    });

    $("#textarea_field").on('keyup paste', function() {
	$(":radio").prop("checked", false);
	$("#textarea_radio").prop("checked", true);
    });
    $('#submit_search').click(start_upload);
}

function validate_form(){
    var source = $("input:radio:checked").val();
    if (typeof source == 'undefined') {
	console.log('pick a source');
	return false;
    }
    if (source == 'file'){
	filename = $('#file_field').val();
	ext = get_extension(filename);
	if (! (ext in MIME_TYPES)){
	    console.log('Invalid file extension:', ext);
	    return false;
	}
    }
    return true;
}

function get_user_info(){
    return USER_INFO;
}

// returns pathname extension (e.g. 'txt')
function get_extension(path){
  var re = /(?:\.([^.]+))?$/;
  return re.exec(path)[1];
}

// looks up value in MIME_TYPES
// returns null if extension is not known
function get_mime_type(path){
    var ext = get_extension(path);
    if (typeof ext == 'undefined'){
	return null;
    }
    ext = ext.toLowerCase();
    if (ext in MIME_TYPES){
	return MIME_TYPES[ext];
    }
    return null;
}

function start_upload(event){
    event.preventDefault();
    if (!validate_form()){
	return;
    }
    var source = $("input:radio:checked").val();

    if (source == 'file'){
	file = $('#file_field:file').get(0).files[0];
	filename = file.name;
	mime_type = get_mime_type(filename)
    } else if (source == 'textarea'){
	string = $('#textarea_field').val().toUpperCase();
	filename = USER_SRC;
	header = '> user-supplied data\n'
	file = new File([new Blob([header + string])], filename);
	mime_type = 'application/fasta'
    }
    var guid = make_guid();
    log('Uploading', guid);
    var url = SETTINGS.upload_url + '/' + SETTINGS.env + '/inbox/' + guid + '.' + get_extension(filename);
    show_upload_start(guid, filename);
    headers = {
	'Content-Type': mime_type,
	'x-amz-acl': 'bucket-owner-full-control',
	'x-amz-meta-filename' : filename,
	'x-amz-meta-email' : SETTINGS.email,
	'x-amz-meta-org' : SETTINGS.org,
	'x-amz-meta-env' : SETTINGS.env,
	'x-amz-meta-source' : source,
	'x-amz-meta-guid' : guid
    }
    if ('dev_username' in SETTINGS){
	headers['x-amz-meta-dev_username'] = SETTINGS.dev_username;
    }
    $.ajax({
	type: 'PUT',
	url: url,
	headers: headers,	
	data: file,
	contentType: 'binary/octet-stream',
	processData: false
    }).then((xhr, result)=>{show_upload_done(guid, result)});
}

function show_upload_start(guid, filename){
    item = {'guid': guid, 'filename': filename, 'status': 'uploading', 'start_time': new Date(Date.now())}
    row = make_row(item);
    RECENT_ITEMS[guid] = item;
    log('prepend', guid)
    $('table tbody').prepend(row.addClass('new_fade'));
    setTimeout(() =>{row.addClass('new_fade_end')}, 100);
}

function show_upload_done(guid, result){
    log('Upload:', result, guid);
}

function make_guid() {
    return random4() + random4() + '-' + random4() + random4();
}

function random4() {
    return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
}

function get_queries(email){
    var url = SETTINGS.api_url + '/' + SETTINGS.env + '/queries/' + email;
    $.ajax({type: 'GET',
	    url: url,
	    jsonp: 'with_queries',
	    dataType: 'jsonp'})
}

function find_item_by_guid(guid, items){
    for (i in items){
	if (guid == items[i].guid){
	    return item;
	}
    }
}

// data: list of job status items received from server
// RECENT_ITEMS includes items that may not yet have been captured in the database
function update_with_recent_items(data){
    recents = Object.values(RECENT_ITEMS)
    result = [...data]; // make a copy, requires ES6
    for (i in recents){
	recent = recents[i];
	found = find_item_by_guid(recent.guid, data);
	if ((typeof found == 'undefined') || found == null){
	    log('inject recent', recent.guid)
	    result.push(recent);
	} else {
	    // safely recorded in database, no further need to track locally in the client
	    log('delete recent', recent.guid)
	    delete RECENT_ITEMS[recent.guid];
	}
    }
    return sorted_by_date(result);
}

function with_queries(data){
    log('data received', data.length)
    for (i in data){
	item = data[i]
        if ((typeof data.start_time) == 'string'){
	    data.start_time = new Date(timestamp+' UTC');
	}
    }
    show_table(update_with_recent_items(data));
}    

// Polls the server every 5 seconds to get a fresh copy of job status
function poll_loop(){
    wait = 5 * 1000 
    get_queries(SETTINGS.email);
    setTimeout(poll_loop, wait)
}

function show_table(queries){
    $('#queries').empty();
    $('#queries').append(make_table_head(), $('<tbody/>'));
    $.each(queries, (i, item)=>{$('#queries tbody').append(make_row(item))});
}

function make_table_head(){
    var row = $('<tr/>')
    var head = $('<thead/>').append(row)
    row.append($('<th/>').text('status'),
	       $('<th/>').text('start'),
               $('<th/>').text('input'),
	       $('<th/>').text('results')
	       )
    return head;
}


function make_row(item){
    var row = $('<tr/>').attr('guid', item.guid);
    row.append($('<td/>').append(format_status(item.status)),
	       $('<td/>').append(format_time(item.start_time)).addClass('time'),
               $('<td/>').append(format_filename(item.filename)),
	       $('<td/>').append(format_results(item.results))
	       )
    return row;
}

function sorted_by_date(items){
    items.sort(function(a,b){
	return new Date(b.start_time) - new Date(a.start_time);
    });
    return items;
}

// ---- Formatting

function format_filename(filename){
    if (filename == USER_SRC){
	return "<i>from user</i>";
    }
    return filename;
}

function format_status(status){
    if (status == 'uploaded'){
	div = $("<div/>").addClass('results status text-secondary');
	div.append($('<i class="fas fa-cog fa-spin"></i>'));
	return div;
    } else if (status == 'uploading'){
	div = $("<div/>").addClass('results status text-secondary');
	div.append($('<i class="fas fa-arrow-up"></i>'));
	return div;
    } else if (status == 'done'){
	div = $("<div/>").addClass('results status text-success');
	div.append($('<i class="fas fa-check"></i>'));
	return div;
    } else if (status == 'error'){
	div = $("<div/>").addClass('results status text-danger');
	div.append($('<i class="fas fa-times"></i>'));
	return div;
    }

}

function format_results(results){
    if (typeof results == 'undefined'){
	return ''
    }
    div = $('<div/>').addClass('results');
    if (results.length == 0){
	div.addClass('text-danger').text('No match found');
	return div;
    }
    for (i in results){
	var result = results[i];
	if ('name' in result){
	    text = "Match at location " + result.offset + ':';
	    div.append($('<div/>').addClass('match_name text-success').text(text));
	    div.append($('<div/>').addClass('match_desc').text(result.desc));
	} else if ('error' in result){
	    div.addClass('error alert-warning').text(result.error);
	}
    }
    return div
}

function format_time(timestamp) {
    if ((typeof timestamp) == 'undefined'){
	return 'undefined'
    }
    if ((typeof timestamp) == 'string'){
	date = new Date(timestamp+' UTC');
    } else if ((typeof timestamp.getMonth) === 'function'){
	date = timestamp
    } else {
	return '-'
    }
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var mon = date.getMonth()+1;
    var day = date.getDate();
    var year = date.getFullYear();
    var time_string = hours + ':' + minutes + ' ' + ampm;
    var date_string = mon + '/' + day + '/' + year;
    return time_string + '<br/>' + date_string;

}

