function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // 向后端获取城区的信息
    $.get("/api/v1_0/areas", function (resp) {
        if (resp.errno == 0) {
            // 获取到了城区信息
            // var areas = resp.data.areas;
            // for (i=0; i < areas.length; i++){
            //     var area = areas[i];
            //     $("#area-id").append('<option value="'+ area.aid +'">'+ area.aname +'</option>')
            // };

            //1. 初始化模板-->告诉我模板script的id, 同时告诉我数据
            house_html = template('areas-templ', {areas: resp.data.areas})
            // 2.将模板设置到指定的标签内
            $("#area-id").html(house_html);

        } else {
            alert(resp.errmsg);
        }
    });

        // 处理房屋基本信息的表单数据
    $("#form-house-info").submit(function (e) {
        e.preventDefault();
        // 获取表单数据，转换为json发送到后端
        var houseData = {};
        $("#form-house-info").serializeArray().map(function(x){ houseData[x.name] = x.value});

        var facilities = [];
        $(":checked[name=facility]").each(function(index, x){ facilities[index] = $(x).val()});

        // 这里的房屋设施比较特殊, 所以单独获取. 获取之后,还需要传递给原来的数据中
        // 这里的facility 其实对应的就是房屋信息的facilities属性. 只不过这里只是在拼接数据, 所以可以不一致
        houseData.facility = facilities;

        $.ajax({
            url: "/api/v1_0/houses/info",
            type: "post",
            data: JSON.stringify(houseData),
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == 4101) {
                    // 用户未登录
                    location.href = "/login.html";
                } else if (resp.errno == 0) {
                    // 保存成功
                    // 隐藏基本信息表单
                    $("#form-house-info").hide();
                    // 显示图片表单
                    $("#form-house-image").show();
                    // 设置图片表单中的房屋id
                    $("#house-id").val(resp.data.house_id);
                } else {
                    alert(resp.errmsg);
                }
            }
        })

    });

        $("#form-house-image").submit(function (e) {
        e.preventDefault();
        $("#form-house-image").ajaxSubmit({
            url: "/api/v1_0/houses/image",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == 0){
                    // 保存图片成功
                    $(".house-image-cons").append('<img src="'+ resp.data.image_url +'">');
                } else if (resp.errno == 4101) {
                    location.href = "/login.html";
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });
})