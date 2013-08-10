var URL_JS_CHECK = "/center/check";
var URL_JS_SAVE = "/for-center/save";
var URL_JS_RESET = "/for-center/reset";
var URL_JS_CONSOLE = "/center/console";
var current_category;
var current_test;
var categories_names = [];
var checking_results;

var EXT = {};
EXT.setHtmlSlide = function(data) {
    data = $.trim(data);
    var anim = $(".animation_results .x-panel-body");
    anim.html(data);
    return ".animation_results .x-panel-body";
};

EXT.setHtmlTryIt = function(data) {
    data = $.trim(data);
    var tr = $(".tryit_results .x-panel-body");
    tr.html(data);
    return ".tryit_results .x-panel-body";
};

EXT.sendToConsoleCheckiO = function(data) {
    var send_data = {
        'data': editor.getSession().getValue(),
        'runner': 'python-27'
    };

    $.ajax({
        'type': 'POST',
        'data': send_data,
        'url': URL_JS_CONSOLE,
        'dataType': 'json',
        'success': function(res) {
            var connection_id = res[0][1];
            var send_data = {
                'data': "checkio(" + JSON.stringify(data) + ")",
                'runner': 'python-27',
                'id': connection_id
            };
            $.ajax({
                'type': 'POST',
                'data': send_data,
                'url': URL_JS_CONSOLE,
                'dataType': 'json',
                success: return_console
        })
        }

    });
};

EXT.setAnimationHeight = function(n) {
    $('.animation_results').css('height', n);
};


function return_console(data) {
    if (data[0][0] === 'err') {
        console.log(data[0][1]);
    }
    else if (data[0][0] === 'res') {
        EXT.set_console_process_ret(EXT, data[0][1]);
    }
}

function send_code(code, task_num, url) {
    var send_data = {
        'code': code,
        'task_num': task_num,
        'runner': 'python-27'
    };

    $.ajax({
        'type': 'POST',
        'data': send_data,
        'url': url,
        'dataType': 'json',
        'success': send_code_success

    });
    show_animation_panel();

}

function send_code_success(data, st) {
    var results = {};
    var category = "";
    var temp = {};
    for (var i = 0; i < data.length; i++){
        var el = data[i];
        if (el[0] == 'err') {
            temp['error'] = el[1];
            results[category].push(temp);
            console.log(el[1]);
        }
        else if (el[0] == "start_in") {
            category = el[1];
            categories_names.push(category);
            results[category] = [];
        }
        else if (el[0] == 'in') {
            temp[el[2]] = el[1];
        }
        else if (el[0] == 'ext'){
            temp[el[0]] = el[1];
            results[category].push(temp);
            temp = []
        }
    }

    checking_results = results;
    current_category = 0;
    current_test = 1;

    var quantity_tests;
    if (results[categories_names[current_category]]){
        quantity_tests = results[categories_names[current_category]].length;
    }
    else {
        quantity_tests = 0;
    }

    $("#category-name").html(categories_names[current_category]);
    $("#test-name").html(1 + "/" + quantity_tests);
    $(".switch").show();
    show_test_animation(current_category, current_test);
}

function show_animation_panel(){
    $("#editor-description").hide();
    $(".animation_results").show();
}

function show_test_animation(cat, num) {
    if (checking_results[categories_names[cat]]) {
        var data = checking_results[categories_names[cat]][num - 1];
        EXT.set_animate_slide(EXT, data);
    }
}

function check_code(data) {
    send_code(data, 1, URL_JS_CHECK);
}

function changeTest(dir) {
    current_test += dir;
    var quantity_tests = checking_results[categories_names[current_category]].length;
    if (current_test <= 0) {
        current_test = 1;
    }
    else if (current_test >= quantity_tests) {
        current_test = quantity_tests;
    }
    $("#test-name").html(current_test + "/" + quantity_tests);
    show_test_animation(current_category, current_test)
}

function changeCategory(dir) {
    current_category += dir;
    var quantity_categories = categories_names.length;
    if (current_category < 0) {
        current_category = 0;
    }
    else if (current_category >= quantity_categories) {
        current_category = quantity_categories - 1;
    }
    $("#category-name").html(categories_names[current_category]);
    $("#test-name").html(1 + "/" + checking_results[categories_names[current_category]].length);
    show_test_animation(current_category, 1)
}

function save_code (code) {
    $.ajax({
        'type': 'POST',
        'data': code,
        'url': URL_JS_SAVE,
        'dataType': 'json',
        'success': save_code_success
    });
}

function save_code_success(data) {
    alert("Code saved at " + data);
}

function reset_code() {
    $.ajax({
        'type': 'POST',
        'url': URL_JS_RESET,
        'dataType': 'json',
        'success': reset_code_success
    });
}

function reset_code_success(data) {
    editor.setValue(data);
}
