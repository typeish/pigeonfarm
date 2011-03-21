(function() {
  var PigeonFarm, spinner_gif_base64;
  PigeonFarm = function(settings) {
    var addError, classes, clearError, data, email_label, fields, getData, hideSpinner, initForm, sendMessage, showSpinner, showSuccessNotification, spinner_html, subject_label, validateBody, validateEmail, validateSubject;
    if (window.XMLHttpRequest && ((settings != null ? settings.container : void 0) != null)) {
      data = {};
      fields = {};
      settings.container = document.querySelector(settings.container);
      email_label = settings.email_label != null ? settings.email_label : "Email:";
      subject_label = settings.subject_label != null ? settings.subject_label : "Subject:";
      if (email_label) {
        email_label = "<label for='pf-contact-sender'>" + email_label + "</label> ";
      }
      if (subject_label) {
        subject_label = "<label for='pf-contact-subject'>" + subject_label + "</label> ";
      }
      spinner_html = settings.spinner_url != null ? settings.spinner_url : spinner_gif_base64;
      if (spinner_html) {
        spinner_html = "<img id='pf-contact-spinner' src='" + spinner_html + "' style=display:none;/>";
      }
      initForm = function() {
        settings.container.innerHTML = "" + email_label + "<input id='pf-contact-sender' type='text' placeholder='your email address'><span id='pf-contact-sender-status' style='visibility:hidden;'>Please enter a valid email address</span><br />\n" + subject_label + "<input id='pf-contact-subject' type='text' placeholder='subject'><span id='pf-contact-subject-status' style='visibility:hidden;'>Please enter a subject</span><br />\n<textarea id='pf-contact-body' placeholder='message'></textarea><br />\n<button id='pf-contact-send'>send &raquo;</button>" + spinner_html + "\n<span id='pf-contact-general-status' style='visibility:hidden;'></span>";
        fields.status = document.querySelector("#pf-contact-general-status");
        fields.sender = document.querySelector("#pf-contact-sender");
        fields.sender_status = document.querySelector("#pf-contact-sender-status");
        fields.subject = document.querySelector("#pf-contact-subject");
        fields.subject_status = document.querySelector("#pf-contact-subject-status");
        fields.body = document.querySelector("#pf-contact-body");
        fields.send = document.querySelector("#pf-contact-send");
        fields.spinner = document.querySelector("#pf-contact-spinner");
        fields.send.onclick = sendMessage;
        fields.sender.onfocus = clearError;
        fields.subject.onfocus = clearError;
        return fields.body.onfocus = clearError;
      };
      classes = {
        error: "pf-error"
      };
      getData = function() {
        var valid;
        valid = true;
        data.sender = fields.sender.value;
        data.subject = fields.subject.value;
        data.body = fields.body.value;
        if (!validateEmail(data.sender)) {
          valid = false;
          fields.sender.addError();
          fields.sender_status.addError();
          fields.sender_status.style.visibility = "";
        }
        if (!validateSubject(data.subject)) {
          valid = false;
          fields.subject.addError();
          fields.subject_status.addError();
          fields.subject_status.style.visibility = "";
        }
        if (!validateBody(data.body)) {
          valid = false;
          fields.body.addError();
          fields.status.addError();
          fields.status.innerText = "Please enter a message";
          fields.status.style.visibility = "";
        }
        return valid;
      };
      validateEmail = function(email) {
        var email_reg;
        email_reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
        return email_reg.test(email);
      };
      validateSubject = function(subject) {
        return subject !== "";
      };
      validateBody = function(subject) {
        return subject !== "";
      };
      clearError = function() {
        return this.className = this.className.replace(classes.error, "");
      };
      addError = function() {
        return this.className = "" + this.className + " " + classes.error;
      };
      HTMLElement.prototype.addError = addError;
      sendMessage = function() {
        var inbound_data;
        fields.sender_status.style.visibility = "hidden";
        fields.subject_status.style.visibility = "hidden";
        fields.status.style.visibility = "hidden";
        showSpinner();
        if (getData()) {
          inbound_data = {
            site: settings.site,
            key: settings.key,
            sender: data.sender,
            subject: data.subject,
            body: data.body
          };
          return jQuery.get("" + settings.server + "/inbound/", inbound_data, function(response) {
            if ((response.status != null) && response.status === "success") {
              showSuccessNotification();
            } else {
              fields.status.addError();
              fields.status.innerText = "There was a problem. Please try again.";
              fields.status.style.visibility = "visible";
            }
            if ((settings.callback != null) && typeof settings.callback === "function") {
              settings.callback(response);
            }
            return hideSpinner();
          }, "jsonp");
        } else {
          return hideSpinner();
        }
      };
      showSpinner = function() {
        return fields.spinner.style.display = "";
      };
      hideSpinner = function() {
        return fields.spinner.style.display = "none";
      };
      showSuccessNotification = function() {
        return settings.container.innerHTML = settings.success_message != null ? settings.success_message : 'Success! Your message has been sent. We will get back to you as soon as possible.';
      };
      initForm();
      return this;
    } else {
      return void 0;
    }
  };
  window.PigeonFarm = PigeonFarm;
  spinner_gif_base64 = "data:image/gif;base64,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";
}).call(this);
