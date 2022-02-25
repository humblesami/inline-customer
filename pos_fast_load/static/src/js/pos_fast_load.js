(function(){
    let dateNow = '';
    if(window.disable_cache)
    {
        dateNow = new Date();
        dateNow = '?dt=' + dateNow.getMinutes() +''+ dateNow.getSeconds();
    }
    document.writeln('<script type="text/javascript" src="/pos_fast_load/static/src/js/pos_fast_load_debug.js'+dateNow+'"></script>');
})();
//# sourceMappingURL=/pos_fast_load_debug/static/src/js/pos_fast_load_debug.js