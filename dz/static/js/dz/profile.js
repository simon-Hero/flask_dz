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

    // 查询用户信息
    $.ajax({
        url: "api/user",
        type: "get",
        dataType: 'json',
        success: function (resp) {
            if (resp.errno == "4101") {
                self.location.href = "/login.html"
            } else if (resp.errno == "0") {
                $("#user-name").val(resp.data.name);
                $("#user-avatar").attr("src", "/api/user/show/" + resp.data.avatar);
            }
        }
    });

    // 设置用户名
    $("#form-name").submit(function (e) {
        e.preventDefault();
        var name = $("#user-name").val();
        if (!name) {
            alert("请填写用户名");
            return
        }
        $.ajax({
            url: "api/user/name",
            type: "put",
            data: JSON.stringify({"name": name}),
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    $("#form-name").hide();
                    $("#content-menu").html(resp.data.name);
                    showSuccessMsg();
                } else if (resp.errno == "4101") {
                    self.location.href = "/login.html"
                } else if (resp.errno == "4103") {
                    $(".error-msg").show()
                }
            }
        })
    });

    // 上传头像
    $("#form-avatar").submit(function (e) {
        e.preventDefault();
        var file = $("#img_file").get(0).files[0];
        if (!file) {
            alert("请选择上传文件");
            return
        }
        var data = new FormData($("#form-avatar")[0]);   //注意jQuery选择出来的结果是个数组,需要加上[0]获取
        $.ajax({
            url: 'api/user/avatar',
            method: 'POST',
            data: data,
            processData: false,
            contentType: false,
            cache: false,
            success: function (resp) {
                if (resp.errno == "0") {
                    showSuccessMsg();
                } else if (resp.errno == "4101") {
                    self.location.href = "/login.html";
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    })
});



