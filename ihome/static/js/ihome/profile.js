function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // 页面加载好
    $("#form-avatar").submit(function (event) {
        alert(123)
        // 阻止表单的默认行为
        event.preventDefault();
        // jquery.form.min.js
        $(this).ajaxSubmit({
            url: "/api/v1_0/users/avatar",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == 0) {
                    // 上传头像成功, 设置页面中头像展示的url
                    $("#user-avatar").attr("src", resp.data.avatar_url);
                } else if (resp.errno == 4101 ){
                    // 表示用户未登录, 跳转到登录页面
                    location.href = "/login.html";
                } else {
                    alert(resp.errmsg);
                }
            }
        });
    });

})
