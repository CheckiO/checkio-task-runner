var retResult;

var ret = undefined;

var falseExt = {
    "set_start_game": function (f) {
    },
    "set_process_in": function (f) {
    },
    "set_process_ext": function (f) {
    },
    "set_process_err": function (f) {
    },
    "set_animate_slide": function (f) {
        f(fakeThis_e, fakeData);
    },
    "set_console_process_ret": function (f) {
        retResult = f;
    },
    "set_generate_animation_panel": function (f) {
        f(fakeThis_e);
    },
    "set_animate_success_slide": function (f) {
        f(fakeThis_e)
    },
    "setHtmlSlide": function (a) {
        return a
    },

    "get_template": function (name) {
        return $("." + name + "_results")
    },
    "JSON": {
        "encode": function lencode(a) {
            if (a instanceof Array) {
                var res = [];
                for (var i = 0; i < a.length; i++) {
                    res.push(lencode(a[i]));
                }
                return "[" + res.join(", ") + "]";
            }
            return String(a);
        },
        "decode": function (a) {
            return a;
        }
    }
};
var fakeThis_e = {
    "setHtmlSlide": function (a) {
        return a
    },
    "setHtmlTryIt": function (a) {
        return a
    },
    "setAnimationHeight": function (h) {
        $(".animation_results").attr("height", h)
    },
    "sendToConsoleCheckiO": function (data) {
        console.log(data);
        retResult(fakeThis_e, ret);
    }
};

var fakeDataError = {
    "referee": [1, 2, 3],
    "error": "Exception on \n 7 line"
};



function requirejs(list, func) {
    func(falseExt, $, []);
}
