function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');


    // 获取城区信息
    $.ajax({
        url: "api/areas",
        type: "get",
        success: function (resp) {
            if (resp.errno == "0") {
                var datas = resp.data;
                for (var i=0; i<datas.length; i++) {
                    $("#area-id").append('<option value="'+ resp.data[i].aid +'">'+ resp.data[i].a_name +'</option>')
                }
            }
        }
    });
    // 发布新房源
    $("#form-house-info").submit(function (e) {
        e.preventDefault();
        var data = {};

        // 收集form表单信息
        $("#form-house-info").serializeArray().map(function (x) {
            data[x.name] = x.value
        });
        // 收集设施id信息
        var facility = [];
        $(":checked[name=facility]").each(function (index, x) {
            facility[index] = $(x).val()
        });
        data.facility = facility;

        $.ajax({
            url: "api/houses/info",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(data),
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "4101") {
                    self.location.href = "/login.html"
                } else if (resp.errno == "0"){
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(resp.data.house_id)
                } else {
                    alert(resp.errmsg)
                }
            }
        })
    });

    // 上传图片
    $("#form-house-image").submit(function (e) {
        e.preventDefault();
        var file = $("#house-image").get(0).files[0];
        if (!file) {
            alert("请选择上传文件");
            return
        }
        var data = new FormData($("#form-house-image")[0]);   //注意jQuery选择出来的结果是个数组,需要加上[0]获取
        $.ajax({
            url: 'api/houses/image',
            method: 'POST',
            data: data,
            processData: false,
            contentType: false,
            cache: false,
            success: function (resp) {
                if (resp.errno == "4101") {
                    self.location.href = "/login.html"
                } else if (resp.errno == "0") {
                    $(".house-image-cons").append('<img src="/api/user/show/' + resp.data.image_name +'">')
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    })
});