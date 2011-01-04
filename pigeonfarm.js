// ==ClosureCompiler==
// @compilation_level SIMPLE_OPTIMIZATIONS
// @output_file_name pigeonfarm-min.js
// ==/ClosureCompiler==

// var settings = {
//     server:      "http://pigeonfarmserver.foo",  // target Pigeon Farm server
//     site:        "example.com",                  // site domain
//     key:         "somegibberish-uuid-key",       // site access key
//     container:   "#selector"                     // selector of element to contain the form
// }
// PigeonFarm(settings);                            // initialize form

function PigeonFarm(settings) {
    if (jQuery && settings && settings.container) {
        
        var that = this;
        var data = {};
        var fields = {};
        
        function initForm() {
            
            var fields_html =   '<input id="pf-contact-sender" type="text" placeholder="your email address"><span id="pf-contact-sender-status" style="visibility:hidden;">Please enter a valid email address</span><br />' +
                                '<input id="pf-contact-subject" type="text" placeholder="subject"><span id="pf-contact-subject-status" style="visibility:hidden;">Please enter a subject</span><br />' +
                                '<textarea id="pf-contact-body" placeholder="message"></textarea><br />' +
                                '<button id="pf-contact-send">send &raquo;</button><img id="pf-contact-spinner" src="http://typestatic.net/pigeonfarm/images/small-spinner.gif" style="display:none;"/>' +
                                '<span id="pf-contact-general-status" style="visibility:hidden;"></span>';
            
            jQuery(settings.container).append(fields_html);
            
            // bind fields
            fields.status           = jQuery("#pf-contact-general-status");
            fields.sender           = jQuery("#pf-contact-sender");
            fields.sender_status    = jQuery("#pf-contact-sender-status");
            fields.subject          = jQuery("#pf-contact-subject");
            fields.subject_status   = jQuery("#pf-contact-subject-status");
            fields.body             = jQuery("#pf-contact-body");
            fields.send             = jQuery("#pf-contact-send");
            fields.spinner          = jQuery("#pf-contact-spinner");

            // bind events
            fields.send.click(sendMessage);
            fields.sender.focus(clearError);
            fields.subject.focus(clearError);
            fields.body.focus(clearError);
            
        }

        function getData() {
            var valid = true;

            // pull values
            data.sender = fields.sender.val();
            data.subject = fields.subject.val();
            data.body = fields.body.val();

            // validate
            if(!validate_email(data.sender)) {
                valid = false;
                fields.sender.addClass("pf-error");
                fields.sender_status.addClass("pf-error");
                fields.sender_status.css({"visibility":"visible"});
            }

            if(!validate_subject(data.subject)) {
                valid = false;
                fields.subject.addClass("pf-error");
                fields.subject_status.addClass("pf-error");
                fields.subject_status.css({"visibility":"visible"});
            }

            if(!validate_body(data.body)) {
                valid = false;
                fields.body.addClass("pf-error");
                fields.status.addClass("pf-error");
                fields.status.text("Please enter a message");
                fields.status.css({"visibility":"visible"});
            }
            
            return valid;
        }

        function validate_email(email) {
           var email_reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
           return email_reg.test(email);
        }
        
        function validate_subject(subject) {
            return (subject !== "");
        }

        function validate_body(subject) {
            return (subject !== "");
        }

        function clearError() {
            jQuery(this).removeClass("pf-error");
        }

        function sendMessage() {
            fields.sender_status.css({"visibility":"hidden"});
            fields.subject_status.css({"visibility":"hidden"});
            fields.status.css({"visibility":"hidden"});
            
            fields.spinner.show();
            
            if(getData()) {
                inbound_data = {
                    'site': settings.site,
                    'key': settings.key,
                    'sender': data.sender,
                    'subject': data.subject,
                    'body': data.body
                };
                jQuery.get(settings.server + '/inbound/', inbound_data, function(response) {
                    if(response.status && response.status === "success") {
                        showSuccessNotification();
                    } else {
                        fields.status.addClass("pf-error");
                        fields.status.text("There was a problem. Please try again.");
                        fields.status.css({"visibility":"visible"});
                    }
                    if(settings.external_callback) {
                        settings.external_callback(response);
                    }
                    fields.spinner.hide();
                }, "jsonp");
            } else {
                fields.spinner.hide();
            }
        }
        
        function showSuccessNotification() {
            var success_notice_html = 'Success! Your message has been sent. We will get back to you as soon as possible.';
            jQuery(settings.container).html(success_notice_html);
        }
        
        // INIT 
        initForm();
        
        return that;
        
    } else { return undefined; }
}
