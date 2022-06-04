(function(){
    window.await_jquery = {
        completed: 0,
        functions : [],
        exec_on_ready: function(awaiting_function){
            if(window.await_jquery.completed){
                console.log('executed without wait');
                awaiting_function();
            }
            else{
                window.await_jquery.functions.push(awaiting_function);
            }
        },
    };

    if(typeof $){
        let ref_script = document.getElementById('web.layout.odooscript');
        let lazy_js_found = false;
        let sibling = ref_script.nextElementSibling;
        while(!lazy_js_found && sibling){
            if(sibling.src && sibling.src.endsWith('web.assets_common_lazy.min.js')){
                lazy_js_found = true;
                sibling.onload = function(){
                    window.await_jquery.completed = 1;
                    for(let fun of window.await_jquery.functions){
                        fun();
                    }
                    console.log('executed waiting functions');
                };
            }
            sibling = sibling.nextElementSibling;
        }
    }
    else{
        console.log('executed waiting functions $ already loaded');
        for(let fun of window.await_jquery.functions){
            fun();
        }
    }
})();