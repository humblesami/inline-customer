var ajax_request = {
    makeFormData: function (FormElement){
        var formData = new FormData(FormElement);
        var ConvertedJSON = {};
        for (const [key, value]  of formData.entries())
        {
            ConvertedJSON[key] = value;
        }
        return ConvertedJSON
    },
    showLoader: function (target){
        var ajax_loader = $('.ajax-loader');
        if(!ajax_loader.length)
        {
            $('body').append(`
                <div class="ajax-loader" style=".ajax-loader{
                    position: fixed;
                    background: rgba(0,0,0,0.15);
                    display: none;
                    align-items: center;
                    justify-content: center;
                }">
                    <img src="/hr_employee_portal/static/img/loader.gif" />
                </div>
            `);
            ajax_loader = $('.ajax-loader');
        }
        var css_data = {
            top: 0,
            left: 0,
            height: document.body.height,
            width: document.body.width,
        }
        if ($(target).length){
            css_data = target.getBoundingClientRect();
            css_data = {
                top: css_data.top,
                left: css_data.left,
                height: css_data.height,
                width: css_data.width,
            }
        }
        css_data['display'] = 'flex';
        ajax_loader.css(css_data);
    },
    full_url: '',
    send: function (options, form_el){
        if(!options.data)
        {
            options.data = ajax_request.makeFormData(form_el)
        }
        options.beforeSend = function(a, b){
            if (b.url.startsWith('http'))
            {
                ajax_request.full_url = b.url;
            }
            else{
                ajax_request.full_url = window.location.origin.toString() + b.url;
            }
            if(!options.noLoader)
            {
                ajax_request.showLoader(form_el);
            }
        },
        options.data = {params: JSON.stringify(options.data)}
        options.dataType = 'JSON';
        options.success = function(data){
            if(!data)
            {
                data = {error: 'No data returned by '+options.url }
            }
            if (data.error){
                console.log('Error in '+options.url, ajax_request.full_url);
                if(data.details){
                    console.log(data.details);
                }
                if(options.onError){
                    options.onError(data.error);
                }
                else{
                    $('#feedback.error').html(data.error)
                    console.log(data.error);
                }
            }
            else{
                if(data.data)
                {
                    data = data.data;
                    try{
                        data = JSON.parse(data);
                    }
                    catch{
                    }
                }
                if(options.onSuccess){
                    options.onSuccess(data);
                }
                else{
                    console.log(data)
                }
            }
        }
        options.error = function(a){
            if(options.onError){
                options.onError(a.responseText)
            }
            else{
                console.log('Error in '+options.url,  a.responseText);
            }
        }
        options.complete = function(){
            if(!options.redirect){
                $('.ajax-loader').hide();
            }
            if(options.onComplete)
            {
                options.onComplete();
            }
        }
        $.ajax(options);
    }
}
