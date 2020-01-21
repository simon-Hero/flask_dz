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

    $.ajax({
       url: "api/users/auth",
       type: "get",
        success: function (resp) {
           if (resp.errno == "0") {
               if (resp.data.real_name && resp.data.id_card){
                    $("#real-name").prop("disabled", true).val(resp.data.real_name);
                    $("#id-card").prop("disabled", true).val(resp.data.id_card);
                    $("#form-auth>input[type=submit]").hide();
               }
           } else if (resp.errno == "4101") {
               self.location.href = "/login.html"
           } else {
               alert(resp.errmsg)
           }
        }
    });


    // 提交表单
    $("#form-auth").submit(function (e) {
        e.preventDefault();
        var real_name = $("#real-name").val();
        var id_card = $("#id-card").val();
        if (id_card.length != 18) {
            $(".error-msg").html();
            $(".error-msg").html("身份证号码格式不正确，请重新填写！");
        }
        if (real_name == "" || id_card == "") {
            $(".error-msg").show()
        }
        var data = {
            real_name: real_name,
            id_card: id_card,
        };
        var data_json = JSON.stringify(data);
        $.ajax({
            url: "api/users/auth",
            type: "post",
            data: data_json,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    $(".error-msg").hide();
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true);
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide();
                } else {
                    $(".error-msg").html($(".error-msg>i"));
                    $(".error-msg").text(resp.errmsg).css("display", "block");
                }
            }
        })
    })
});
