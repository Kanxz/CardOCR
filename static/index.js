/**
 * 标签切换
 * @param index 第几个标签
 */
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

/**
 * 本地图片上传提交
 */
function submit_file() {
    let file_submit = document.getElementById("file_submit");
    file_submit.click();
}

/**
 * 加载等待图片
 */
function loading() {
    let img = document.getElementById('loading');
    img.style.display = "block";
    try {
        let pic = document.getElementById('pic');
        pic.style.display = "none";
    } catch (e) {
        console.log("no pic");
    }
    try {
        let msg = document.getElementById('msg');
        msg.innerText = "";
    } catch (e) {
        console.log("no msg");
    }
}

/**
 * 移除等待图片
 */
function rmLoading() {
    let img = document.getElementById('loading');
    img.style.display = "none";
    let pic = document.getElementById('pic');
    pic.style.display = "block";
}

/**
 * json数据格式化
 */
function jsonModify() {
    let res_json = document.getElementById('res_json');
    let json = res_json.innerHTML;
    // console.log(json);

    try {
        json = JSON.stringify(JSON.parse(json), null, 4);
        json = json
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        res_json.innerHTML = json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    } catch (e) {
        console.log('already modified');
    }
}