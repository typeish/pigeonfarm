(function(){var g;window.PigeonFarm=function(c){var e,d,a,h,i,j,k,l,m,n;if(jQuery&&c&&c.container){d={};a={};i=function(){var b;b="email: <input id='pf-contact-sender' type='text' placeholder='your email address'><span id='pf-contact-sender-status' style='visibility:hidden;'>Please enter a valid email address</span><br />\nsubject: <input id='pf-contact-subject' type='text' placeholder='subject'><span id='pf-contact-subject-status' style='visibility:hidden;'>Please enter a subject</span><br />\n<textarea id='pf-contact-body\" placeholder='message'></textarea><br />\n<button id='pf-contact-send'>send &raquo;</button><img id='pf-contact-spinner' src='"+
g+"' style=display:none;/>\n<span id='pf-contact-general-status' style='visibility:hidden;'></span>";jQuery(c.container).append(b);a.status=jQuery("#pf-contact-general-status");a.sender=jQuery("#pf-contact-sender");a.sender_status=jQuery("#pf-contact-sender-status");a.subject=jQuery("#pf-contact-subject");a.subject_status=jQuery("#pf-contact-subject-status");a.body=jQuery("#pf-contact-body");a.send=jQuery("#pf-contact-send");a.spinner=jQuery("#pf-contact-spinner");a.send.click(j);a.sender.focus(e);
a.subject.focus(e);return a.body.focus(e)};h=function(){var b;b=true;d.sender=a.sender.val();d.subject=a.subject.val();d.body=a.body.val();if(!m(d.sender)){b=false;a.sender.addClass("pf-error");a.sender_status.addClass("pf-error");a.sender_status.css({visibility:"visible"})}if(!n(d.subject)){b=false;a.subject.addClass("pf-error");a.subject_status.addClass("pf-error");a.subject_status.css({visibility:"visible"})}if(!l(d.body)){b=false;a.body.addClass("pf-error");a.status.addClass("pf-error");a.status.text("Please enter a message");
a.status.css({visibility:"visible"})}return b};m=function(b){return/^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/.test(b)};n=function(b){return b!==""};l=function(b){return b!==""};e=function(){return jQuery(this).removeClass("pf-error")};j=function(){var b;a.sender_status.css({visibility:"hidden"});a.subject_status.css({visibility:"hidden"});a.status.css({visibility:"hidden"});a.spinner.show();if(h()){b={site:c.site,key:c.key,sender:d.sender,subject:d.subject,body:d.body};return jQuery.get(""+
c.server+"/inbound/",b,function(f){if(f.status!=null&&f.status==="success")k();else{a.status.addClass("pf-error");a.status.text("There was a problem. Please try again.");a.status.css({visibility:"visible"})}c.callback!=null&&typeof c.callback==="function"&&c.callback(f);return a.spinner.hide()},"jsonp")}else return a.spinner.hide()};k=function(){var b;b=c.success_message!=null?c.success_message:"Success! Your message has been sent. We will get back to you as soon as possible.";return jQuery(c.container).html(b)};
i();return this}};g="data:image/gif;base64,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"}).call(this);
