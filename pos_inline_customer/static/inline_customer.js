//This file is just added so we can keep the actual code debuggable
//otherwise we could directly include inline_customer_debug.js in view file

(function(){
    let dt = new Date();
    dt = dt.getMinutes() + '-' + dt.getSeconds();
    let scripts = `
    <script type="text/javascript" src="/pos_inline_customer/static/inline_customer_debug.js?v=${dt}"></script>
    `;
    document.write(scripts);
})();