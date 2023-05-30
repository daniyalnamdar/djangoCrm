for (var i = 0; i < document.links.length; i++) {
    if (document.links[i].href === document.URL && document.getElementsByClassName("page-nav") && !document.getElementsByClassName("active")) {
        document.links[i].className = 'current';
    }else{
        break;
    }
 }