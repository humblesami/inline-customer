//This file is just added so we can keep the actual code debuggable
//otherwise we could directly include inline_customer_debug.js in view file

(function(){
    let dt = new Date();
    dt = dt.getMinutes() + '-' + dt.getSeconds();
    let scripts = `
    <script type="text/javascript" defer src="/inline_customer_pos/static/inline_customer_debug.js?v=${dt}"></script>
    `;
    console.log('deferred');
    document.write(scripts);
})();