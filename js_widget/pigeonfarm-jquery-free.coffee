# var settings = {
#     server                : "http://pigeonfarmserver.foo",        // target Pigeon Farm server
#     site                  : "example.com",                        // site domain
#     key                   : "somegibberish-uuid-key",             // site access key
#     container             : "#selector"                           // selector of element to contain the form
#     [success_message]     : "Success, the message has been sent!" // (optional) success message override
#     [email_label]         : "Email:"                              // (optional) email label override, set to "" to remove
#     [subject_label]       : "Subject:"                            // (optional) subject label override, set to "" to remove
#     [spinner_url]         : "/path/to/spinner.gif"                // (optional) spinner src override, set to "" to remove
# }
# PigeonFarm(settings);     // initialize form


PigeonFarm = (settings) ->
    if window.XMLHttpRequest and settings?.container?
        data = {}
        fields = {}
        
        settings.container = document.querySelector(settings.container)
        
        email_label = if settings.email_label? then settings.email_label else "Email:"
        subject_label = if settings.subject_label? then settings.subject_label else "Subject:"
        
        if email_label
            email_label = "<label for='pf-contact-sender'>#{email_label}</label> "
        
        if subject_label
            subject_label = "<label for='pf-contact-subject'>#{subject_label}</label> "
        
        spinner_html = if settings.spinner_url? then settings.spinner_url else spinner_gif_base64
        
        if spinner_html
            spinner_html = "<img id='pf-contact-spinner' src='#{spinner_html}' style=display:none;/>"
        
        initForm = ->
            settings.container.innerHTML = """
                #{email_label}<input id='pf-contact-sender' type='text' placeholder='your email address'><span id='pf-contact-sender-status' style='visibility:hidden;'>Please enter a valid email address</span><br />
                #{subject_label}<input id='pf-contact-subject' type='text' placeholder='subject'><span id='pf-contact-subject-status' style='visibility:hidden;'>Please enter a subject</span><br />
                <textarea id='pf-contact-body' placeholder='message'></textarea><br />
                <button id='pf-contact-send'>send &raquo;</button>#{spinner_html}
                <span id='pf-contact-general-status' style='visibility:hidden;'></span>
                """
            
            # bind fields
            fields.status           = document.querySelector("#pf-contact-general-status")
            fields.sender           = document.querySelector("#pf-contact-sender")
            fields.sender_status    = document.querySelector("#pf-contact-sender-status")
            fields.subject          = document.querySelector("#pf-contact-subject")
            fields.subject_status   = document.querySelector("#pf-contact-subject-status")
            fields.body             = document.querySelector("#pf-contact-body")
            fields.send             = document.querySelector("#pf-contact-send")
            fields.spinner          = document.querySelector("#pf-contact-spinner")

            # bind events
            fields.send.onclick = sendMessage
            fields.sender.onfocus = clearError
            fields.subject.onfocus = clearError
            fields.body.onfocus = clearError
 
        classes =
            error: "pf-error"
 
        getData = ->
            valid = true

            # pull values
            data.sender = fields.sender.value
            data.subject = fields.subject.value
            data.body = fields.body.value

            # validate
            if not validateEmail(data.sender)
                valid = false
                fields.sender.addError()
                fields.sender_status.addError()
                fields.sender_status.style.visibility = ""

            if not validateSubject(data.subject)
                valid = false
                fields.subject.addError()
                fields.subject_status.addError()
                fields.subject_status.style.visibility = ""

            if not validateBody(data.body)
                valid = false
                fields.body.addError()
                fields.status.addError()
                fields.status.innerText = "Please enter a message"
                fields.status.style.visibility = ""

            return valid

        validateEmail = (email) ->
           email_reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
           return email_reg.test(email)
        
        validateSubject = (subject) ->
            return subject isnt ""

        validateBody = (body) ->
            return body isnt ""

        clearError = ->
            this.className = this.className.replace(classes.error,"")

        addError = ->
            this.className = "#{this.className} #{classes.error}"
        
        HTMLElement.prototype.addError = addError

        sendMessage = ->
            fields.sender_status.style.visibility = "hidden"
            fields.subject_status.style.visibility = "hidden"
            fields.status.style.visibility = "hidden"
            
            showSpinner()
            
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
                        fields.status.addError()
                        fields.status.innerText = "There was a problem. Please try again."
                        fields.status.style.visibility = "visible"

                    if settings.callback? and typeof settings.callback is "function"
                        settings.callback(response)

                    hideSpinner()
                , "jsonp")



            else
                hideSpinner()
        
        showSpinner = ->
            fields.spinner.style.display = ""
        
        hideSpinner = ->
            fields.spinner.style.display = "none"
        
        showSuccessNotification = ->
            settings.container.innerHTML = if settings.success_message? then settings.success_message else 'Success! Your message has been sent. We will get back to you as soon as possible.'
        
        initForm()
        
        return this
    else
        return undefined

window.PigeonFarm = PigeonFarm

spinner_gif_base64 = "data:image/gif;base64,R0lGODlhEAAQAPQAAP///wAAAPDw8IqKiuDg4EZGRnp6egAAAFhYWCQkJKysrL6+vhQUFJycnAQEBDY2NmhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH/C05FVFNDQVBFMi4wAwEAAAAh/hpDcmVhdGVkIHdpdGggYWpheGxvYWQuaW5mbwAh+QQJCgAAACwAAAAAEAAQAAAFdyAgAgIJIeWoAkRCCMdBkKtIHIngyMKsErPBYbADpkSCwhDmQCBethRB6Vj4kFCkQPG4IlWDgrNRIwnO4UKBXDufzQvDMaoSDBgFb886MiQadgNABAokfCwzBA8LCg0Egl8jAggGAA1kBIA1BAYzlyILczULC2UhACH5BAkKAAAALAAAAAAQABAAAAV2ICACAmlAZTmOREEIyUEQjLKKxPHADhEvqxlgcGgkGI1DYSVAIAWMx+lwSKkICJ0QsHi9RgKBwnVTiRQQgwF4I4UFDQQEwi6/3YSGWRRmjhEETAJfIgMFCnAKM0KDV4EEEAQLiF18TAYNXDaSe3x6mjidN1s3IQAh+QQJCgAAACwAAAAAEAAQAAAFeCAgAgLZDGU5jgRECEUiCI+yioSDwDJyLKsXoHFQxBSHAoAAFBhqtMJg8DgQBgfrEsJAEAg4YhZIEiwgKtHiMBgtpg3wbUZXGO7kOb1MUKRFMysCChAoggJCIg0GC2aNe4gqQldfL4l/Ag1AXySJgn5LcoE3QXI3IQAh+QQJCgAAACwAAAAAEAAQAAAFdiAgAgLZNGU5joQhCEjxIssqEo8bC9BRjy9Ag7GILQ4QEoE0gBAEBcOpcBA0DoxSK/e8LRIHn+i1cK0IyKdg0VAoljYIg+GgnRrwVS/8IAkICyosBIQpBAMoKy9dImxPhS+GKkFrkX+TigtLlIyKXUF+NjagNiEAIfkECQoAAAAsAAAAABAAEAAABWwgIAICaRhlOY4EIgjH8R7LKhKHGwsMvb4AAy3WODBIBBKCsYA9TjuhDNDKEVSERezQEL0WrhXucRUQGuik7bFlngzqVW9LMl9XWvLdjFaJtDFqZ1cEZUB0dUgvL3dgP4WJZn4jkomWNpSTIyEAIfkECQoAAAAsAAAAABAAEAAABX4gIAICuSxlOY6CIgiD8RrEKgqGOwxwUrMlAoSwIzAGpJpgoSDAGifDY5kopBYDlEpAQBwevxfBtRIUGi8xwWkDNBCIwmC9Vq0aiQQDQuK+VgQPDXV9hCJjBwcFYU5pLwwHXQcMKSmNLQcIAExlbH8JBwttaX0ABAcNbWVbKyEAIfkECQoAAAAsAAAAABAAEAAABXkgIAICSRBlOY7CIghN8zbEKsKoIjdFzZaEgUBHKChMJtRwcWpAWoWnifm6ESAMhO8lQK0EEAV3rFopIBCEcGwDKAqPh4HUrY4ICHH1dSoTFgcHUiZjBhAJB2AHDykpKAwHAwdzf19KkASIPl9cDgcnDkdtNwiMJCshACH5BAkKAAAALAAAAAAQABAAAAV3ICACAkkQZTmOAiosiyAoxCq+KPxCNVsSMRgBsiClWrLTSWFoIQZHl6pleBh6suxKMIhlvzbAwkBWfFWrBQTxNLq2RG2yhSUkDs2b63AYDAoJXAcFRwADeAkJDX0AQCsEfAQMDAIPBz0rCgcxky0JRWE1AmwpKyEAIfkECQoAAAAsAAAAABAAEAAABXkgIAICKZzkqJ4nQZxLqZKv4NqNLKK2/Q4Ek4lFXChsg5ypJjs1II3gEDUSRInEGYAw6B6zM4JhrDAtEosVkLUtHA7RHaHAGJQEjsODcEg0FBAFVgkQJQ1pAwcDDw8KcFtSInwJAowCCA6RIwqZAgkPNgVpWndjdyohACH5BAkKAAAALAAAAAAQABAAAAV5ICACAimc5KieLEuUKvm2xAKLqDCfC2GaO9eL0LABWTiBYmA06W6kHgvCqEJiAIJiu3gcvgUsscHUERm+kaCxyxa+zRPk0SgJEgfIvbAdIAQLCAYlCj4DBw0IBQsMCjIqBAcPAooCBg9pKgsJLwUFOhCZKyQDA3YqIQAh+QQJCgAAACwAAAAAEAAQAAAFdSAgAgIpnOSonmxbqiThCrJKEHFbo8JxDDOZYFFb+A41E4H4OhkOipXwBElYITDAckFEOBgMQ3arkMkUBdxIUGZpEb7kaQBRlASPg0FQQHAbEEMGDSVEAA1QBhAED1E0NgwFAooCDWljaQIQCE5qMHcNhCkjIQAh+QQJCgAAACwAAAAAEAAQAAAFeSAgAgIpnOSoLgxxvqgKLEcCC65KEAByKK8cSpA4DAiHQ/DkKhGKh4ZCtCyZGo6F6iYYPAqFgYy02xkSaLEMV34tELyRYNEsCQyHlvWkGCzsPgMCEAY7Cg04Uk48LAsDhRA8MVQPEF0GAgqYYwSRlycNcWskCkApIyEAOwAAAAAAAAAAAA=="