# var settings = {
#     server                : "http://pigeonfarmserver.foo",        // target Pigeon Farm server
#     site                  : "example.com",                        // site domain
#     key                   : "somegibberish-uuid-key",             // site access key
#     container             : "#selector"                           // selector of element to contain the form
#     [success_message]     : "Success, the message has been sent!" // an optional success message override
# }
# PigeonFarm(settings);                            // initialize form

PigeonFarm = (settings) ->
    if jQuery and settings and settings.container
        data = {}
        fields = {}
        
        initForm = ->
            fields_html = """
                email: <input id='pf-contact-sender' type='text' placeholder='your email address'><span id='pf-contact-sender-status' style='visibility:hidden;'>Please enter a valid email address</span><br />
                subject: <input id='pf-contact-subject' type='text' placeholder='subject'><span id='pf-contact-subject-status' style='visibility:hidden;'>Please enter a subject</span><br />
                <textarea id='pf-contact-body" placeholder='message'></textarea><br />
                <button id='pf-contact-send'>send &raquo;</button><img id='pf-contact-spinner' src='#{spinner_gif_base64}' style=display:none;/>
                <span id='pf-contact-general-status' style='visibility:hidden;'></span>
                """
            jQuery(settings.container).append(fields_html)
            
            # bind fields
            fields.status           = jQuery("#pf-contact-general-status")
            fields.sender           = jQuery("#pf-contact-sender")
            fields.sender_status    = jQuery("#pf-contact-sender-status")
            fields.subject          = jQuery("#pf-contact-subject")
            fields.subject_status   = jQuery("#pf-contact-subject-status")
            fields.body             = jQuery("#pf-contact-body")
            fields.send             = jQuery("#pf-contact-send")
            fields.spinner          = jQuery("#pf-contact-spinner")

            # bind events
            fields.send.click(sendMessage)
            fields.sender.focus(clearError)
            fields.subject.focus(clearError)
            fields.body.focus(clearError)
 
        getData = ->
            valid = true

            # pull values
            data.sender = fields.sender.val()
            data.subject = fields.subject.val()
            data.body = fields.body.val()

            # validate
            if not validateEmail(data.sender)
                valid = false
                fields.sender.addClass("pf-error")
                fields.sender_status.addClass("pf-error")
                fields.sender_status.css({"visibility":"visible"})

            if not validateSubject(data.subject)
                valid = false
                fields.subject.addClass("pf-error")
                fields.subject_status.addClass("pf-error")
                fields.subject_status.css({"visibility":"visible"})

            if not validateBody(data.body)
                valid = false
                fields.body.addClass("pf-error")
                fields.status.addClass("pf-error")
                fields.status.text("Please enter a message")
                fields.status.css({"visibility":"visible"})

            return valid

        validateEmail = (email) ->
           email_reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
           return email_reg.test(email)
        
        validateSubject = (subject) ->
            return subject isnt ""

        validateBody = (subject) ->
            return subject isnt ""

        clearError = ->
            jQuery(this).removeClass("pf-error")

        sendMessage = ->
            fields.sender_status.css({"visibility":"hidden"})
            fields.subject_status.css({"visibility":"hidden"})
            fields.status.css({"visibility":"hidden"})
            
            fields.spinner.show()
            
            if getData()
                inbound_data =
                    site    : settings.site
                    key     : settings.key
                    sender  : data.sender
                    subject : data.subject
                    body    : data.body

                jQuery.get("#{settings.server}/inbound/", inbound_data, (response) ->
                    if response.status? and response.status is "success"
                        showSuccessNotification()
                    else
                        fields.status.addClass("pf-error")
                        fields.status.text("There was a problem. Please try again.")
                        fields.status.css({"visibility":"visible"})

                    if settings.callback? and typeof settings.callback is "function"
                        settings.callback(response)

                    fields.spinner.hide()
                , "jsonp")
            else
                fields.spinner.hide()
        
        showSuccessNotification = ->
            success_notice_html = if settings.success_message? then settings.success_message else 'Success! Your message has been sent. We will get back to you as soon as possible.'
            jQuery(settings.container).html(success_notice_html)
        
        initForm()
        
        return this

    else
        return undefined

window.PigeonFarm = PigeonFarm

spinner_gif_base64 = "data:image/gif;base64,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"