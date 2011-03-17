# Pigeon Farm: contact forms for static sites

## What
Pigeon Farm handles the dynamic part necessary for contact forms that's impossible on a purely static site.

## Why
Contact forms are generally low usage relative to the overall site, so it's silly to have a dynamic site for static content, just to have a contact form. Plus, centralizing this "dynamicness" means multiple sites can share the resources necessary. It's on AppEngine, which only spins up instances as needed, so when nobody is using the form, there are no resources dedicated to it.

## How
The JavaScript widget included in the page produces a set of fields for a contact form. The input from these fields then gets sent to the AppEngine app, which stores the message. The app supports email dispatching to recipients listed for each site.

Each site on the server has the following attributes:

* Name          : arbitrary name for human-friendliness
* Domain        : the domain of the site where the contact form is
* Recipients    : list of email addresses to send messages to
* Access Key    : auto generated gibberish key

### Security
The app logs the IP address of each message — even geocoding them — and supports blacklisting. On the client-side, the domain and access key must match the site on the server in order for the message to go through. Obviously, this is not really secure, as all the information necessary to send a message is included in the page (by necessity). But, the point is to require someone to go out of their way in order to send a message using something other than the form.

Also, since the form is not a traditional form, but instead a set of fields inserted using JavaScript, it doesn't even exist in the page for bots to see.

### Requirements
The widget requires jQuery, and the app uses Django templates.


### Sample usage

client side:

    …assuming jQuery present in page…
    
    <script type="text/javascript" src="path/to/pigeonfarm-min.js"></script>
    <script type="text/javascript">
        var settings = {
            server              : "http://pigeonfarmserver.foo",            // target Pigeon Farm server
            site                : "example.com",                            // site domain
            key                 : "somegibberish-uuid-key",                 // site access key
            container           : "#selector",                              // selector of element to contain the form
            success_message     : "Success, the message has been sent!",    // (optional) success message override
            email_label         : "Email:",                                 // (optional) email label override, set to "" to remove
            subject_label       : "Subject:"                                // (optional) subject label override, set to "" to remove
        }
        PigeonFarm(settings); // initialize form
    </script>

site config:

    name        : my site
    domain      : example.com
    access key  : somegibberish-uuid-key
    recipients  : person@example.com, other.person@example.com

The site will dispatch emails to person@example.com and other.person@example.com every time it receives a message from example.com


### Styling

The `pigeonfarm.js` snippet doesn't include any style information. Except for the included spinner.gif image, the look is up to you. Any field that doesn't validate gets the class `pf-error` added to it, which you can use to style the error feedback.


### See it in action

* [alecperkins.net/contact/](http://alecperkins.net/contact/)
* [typeish.net/#engage](http://typeish.net/#engage)

## TODO / wishlist

* SMS dispatching support
* Duplicate message detection
* Spam detection/filtering
* Better error feedback to page
