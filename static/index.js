function show(index) {
    let response_area = document.getElementById("response_area");
    let ul1 = document.getElementById("ul1");
    let lis = ul1.getElementsByTagName("li");
    let divs = response_area.getElementsByTagName("div");
    for (let i = 0; i < lis.length; i++) {
        if (i === index)
            lis[i].className = "active";
        else
            lis[i].className = "";
    }
    for (let i = 0; i < divs.length; i++) {
        if (i === index)
            divs[i].className = "show";
        else
            divs[i].className = "hide";
    }
}