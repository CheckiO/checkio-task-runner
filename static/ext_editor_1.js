define([],function(){
    "use strict";

    return {
        'set_generate_animation_panel':function(callback){
            top.EXT.set_generate_animation_panel = callback;
        },
        'set_console_process_err':function(callback){
            top.EXT.console_process_err = callback
        },
        'set_console_process_out':function(callback){
//            top.Ext.A.console_process_out = callback
        },
        'set_console_process_ret':function(callback){
            top.EXT.set_console_process_ret = callback
        },

        'set_process_in':function(callback){
//            top.Ext.A.process_in = callback
        },
        'set_process_fail_check':function(callback){
//            top.Ext.A.process_fail_check = callback
        },
        'set_process_success_check':function(callback){
//            top.Ext.A.process_success_check = callback
        },
        'set_process_out':function(callback){
//            top.Ext.A.process_out = callback
        },
        'set_process_ext':function(callback){
//            top.Ext.A.process_ext = callback
        },
        'set_process_err':function(callback){
//            top.Ext.A.process_err = callback
        },
        'set_process_error':function(callback){
//            top.Ext.A.process_error = callback
        },
        'set_start_game':function(callback){
//            top.Ext.A.start_game = callback
        },
        'set_in_start_game':function(callback){
//            top.Ext.A.in_start_game = callback
        },
        'set_animate_slide':function(callback){
            top.EXT.set_animate_slide = callback;
        },
        'set_animate_success_slide':function(callback){
//            top.Ext.A.animate_success_slide = callback
        },
        'set_reset_form_data': function(callback){
//            top.Ext.A.reset_form_data = callback
        },
        'html_escape': function(val){
            val = val.replace(/&/gim, '&amp;');
            val = val.replace(/</gim, '&lt;');
            val = val.replace(/>/gim, '&gt;');
            val = val.replace(/\n/gim, '<br/>');
            val = val.replace(/\s/gim, '&nbsp;');
            return val;
        },
        'JSON': {
            'encode': JSON.stringify,
            'decode': JSON.parse
        },

        'get_template': function(template_name){
            return top.document.getElementById('template_'+template_name) ?
                top.document.getElementById('template_'+template_name).text : '';
        }
    }
})